"""
PHI Integration Design — STEP Assembly Engine
Uses CadQuery to:
1. Load real STEP files (when available from SMC)
2. Generate parametric geometry (fallback when STEP not available)
3. Position each part correctly using assembly_rules/positions.json
4. Export a single Assembly STEP file
"""

import cadquery as cq
import json, os, math
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RULES_FILE = BASE_DIR / "assembly_rules" / "positions.json"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(RULES_FILE) as f:
    RULES = json.load(f)


# ─────────────────────────────────────────────
# PARAMETRIC GEOMETRY (fallback when no STEP file)
# ─────────────────────────────────────────────

def make_solenoid_valve(series: str, orientation: str = "V") -> cq.Workplane:
    """Parametric SY-series solenoid valve body."""
    r = RULES["series_rules"][series]
    w = r["manifold_width"]
    h = r["sv_height_above_manifold"]
    d = r["manifold_depth"] * 0.7

    body = (
        cq.Workplane("XY")
        .box(w, d, h)
        .edges("|Z").fillet(1.5)
    )
    # Solenoid coil block on top
    coil = (
        cq.Workplane("XY")
        .box(w * 0.8, d * 0.5, h * 0.35)
        .edges("|Z").fillet(1.0)
        .translate((0, 0, h * 0.5 + h * 0.35 / 2 - h / 2))
    )
    # Connector plug
    plug = (
        cq.Workplane("XY")
        .box(w * 0.5, d * 0.3, h * 0.15)
        .translate((0, -d * 0.3, h * 0.5 + h * 0.15 / 2 - h / 2 + h * 0.35))
    )
    # Port holes on bottom face
    sv = body.union(coil).union(plug)
    return sv


def make_manifold(series: str, stations: int) -> cq.Workplane:
    """Parametric SS5Y manifold block."""
    r = RULES["series_rules"][series]
    pitch = r["station_pitch"]
    mh = r["manifold_height"]
    mw = r["manifold_width"]
    md = r["manifold_depth"]
    total_length = pitch * stations + 20  # end plates

    body = (
        cq.Workplane("XY")
        .box(total_length, md, mh)
        .edges("|Y").fillet(1.5)
    )
    # Station dividers (grooves)
    for i in range(1, stations):
        x = -total_length / 2 + 10 + i * pitch
        groove = (
            cq.Workplane("XY")
            .box(1.5, md + 2, mh * 0.4)
            .translate((x, 0, mh * 0.3))
        )
        body = body.cut(groove)
    # Port holes on side
    for i in range(stations):
        x = -total_length / 2 + 10 + i * pitch + pitch / 2
        hole = (
            cq.Workplane("YZ")
            .circle(mw * 0.15)
            .extrude(total_length)
            .translate((x, 0, 0))
        )
    # End caps
    cap_l = cq.Workplane("XY").box(8, md, mh).translate((-total_length / 2 + 4, 0, 0))
    cap_r = cq.Workplane("XY").box(8, md, mh).translate((total_length / 2 - 4, 0, 0))
    manifold = body.union(cap_l).union(cap_r)
    return manifold


def make_blanking_plate(series: str) -> cq.Workplane:
    """Parametric blanking plate."""
    r = RULES["series_rules"][series]
    w = r["manifold_width"]
    h = r["sv_height_above_manifold"] * 0.6
    d = r["manifold_depth"] * 0.4
    plate = (
        cq.Workplane("XY")
        .box(w, d, h)
        .edges("|Z").fillet(1.0)
    )
    return plate


# ─────────────────────────────────────────────
# STEP FILE LOADER (uses real file when available)
# ─────────────────────────────────────────────

def load_or_generate(part_type: str, series: str, orientation: str = "V", stations: int = 1) -> cq.Workplane:
    """Try to load real STEP file; fall back to parametric geometry."""
    r = RULES["series_rules"][series]

    if part_type == "solenoid":
        key = "model_file_h" if orientation == "H" else "model_file"
        step_path = MODELS_DIR / r[key]
        if step_path.exists():
            print(f"  Loading real STEP: {step_path.name}")
            return cq.importers.importStep(str(step_path))
        else:
            print(f"  Generating parametric: {series} SV ({orientation})")
            return make_solenoid_valve(series, orientation)

    elif part_type == "manifold":
        # Try pattern match for station count
        fname = r["manifold_model"].replace("XX", str(stations).zfill(2))
        step_path = MODELS_DIR / fname
        if step_path.exists():
            print(f"  Loading real STEP: {step_path.name}")
            return cq.importers.importStep(str(step_path))
        else:
            print(f"  Generating parametric: {series} Manifold {stations} station")
            return make_manifold(series, stations)

    elif part_type == "blanking":
        step_path = MODELS_DIR / f"blanking/{r['blanking_part']}.step"
        if step_path.exists():
            print(f"  Loading real STEP: {step_path.name}")
            return cq.importers.importStep(str(step_path))
        else:
            print(f"  Generating parametric: {series} Blanking Plate")
            return make_blanking_plate(series)


# ─────────────────────────────────────────────
# MAIN ASSEMBLER
# ─────────────────────────────────────────────

def assemble(bom: list, output_name: str = "PHI_Assembly") -> str:
    """
    bom = list of dicts from selector:
    [
      {"series": "SY5", "orientation": "H", "part_no": "SY5420-5LZ-01", "qty": 3},
      {"series": "SY5", "orientation": "V", "part_no": "SY5320-5LZ-01", "qty": 1},
      ...
    ]
    Returns path to output STEP file.
    """
    print(f"\n=== PHI Assembly Engine ===")
    print(f"BOM: {len(bom)} items")

    # Group by series
    series_groups = {}
    for item in bom:
        s = item["series"]
        if s not in series_groups:
            series_groups[s] = []
        for _ in range(item.get("qty", 1)):
            series_groups[s].append(item)

    assembly = cq.Assembly(name="PHI_Pneumatic_Assembly")

    global_x_offset = 0

    for series, items in series_groups.items():
        print(f"\n-- Series: {series} ({len(items)} SV) --")
        r = RULES["series_rules"][series]
        pitch = r["station_pitch"]
        mh = r["manifold_height"]
        sv_h = r["sv_height_above_manifold"]

        # Calculate station count (SV + 2 spare, round up to even)
        sv_count = len(items)
        spare = 4 if sv_count > 10 else 2
        raw = sv_count + spare
        stations = raw if raw % 2 == 0 else raw + 1
        blanks = stations - sv_count
        total_length = pitch * stations + 20

        print(f"  {sv_count} SV + {blanks} blanking = {stations} stations")

        # ── MANIFOLD ──
        print(f"  Building manifold...")
        manifold = load_or_generate("manifold", series, stations=stations)
        manifold_x = global_x_offset + total_length / 2
        assembly.add(
            manifold,
            name=f"{series}_Manifold_{stations}st",
            loc=cq.Location(cq.Vector(manifold_x, 0, 0))
        )

        # ── SOLENOID VALVES ──
        for i, item in enumerate(items):
            orientation = item.get("orientation", "V")
            part_no = item.get("part_no", f"{series}3xx")
            print(f"  SV {i+1}: {part_no} ({orientation})")

            sv = load_or_generate("solenoid", series, orientation)

            # X position: center of this station on the manifold
            sv_x = global_x_offset + 10 + i * pitch + pitch / 2
            sv_z = mh / 2 + sv_h / 2  # sit on top of manifold

            # Horizontal orientation rotates 90° around Z
            rot = cq.Location(
                cq.Vector(sv_x, 0, sv_z),
                cq.Vector(0, 0, 1),
                90 if orientation == "H" else 0
            )
            assembly.add(sv, name=f"{series}_SV_{i+1}_{part_no}", loc=rot)

        # ── BLANKING PLATES ──
        for j in range(blanks):
            idx = sv_count + j
            print(f"  Blanking plate {j+1}")
            bp = load_or_generate("blanking", series)
            bp_x = global_x_offset + 10 + idx * pitch + pitch / 2
            bp_z = mh / 2 + r["sv_height_above_manifold"] * 0.3
            assembly.add(
                bp,
                name=f"{series}_Blanking_{j+1}",
                loc=cq.Location(cq.Vector(bp_x, 0, bp_z))
            )

        global_x_offset += total_length + 30  # gap between series groups

    # ── EXPORT ──
    out_path = OUTPUT_DIR / f"{output_name}.step"
    print(f"\nExporting to {out_path.name}...")
    assembly.save(str(out_path))
    print(f"Done! File size: {out_path.stat().st_size / 1024:.1f} KB")
    return str(out_path)


# ─────────────────────────────────────────────
# CLI TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Example: 3x SY5 Horizontal + 1x SY5 Vertical
    test_bom = [
        {"series": "SY5", "orientation": "H", "part_no": "SY5420-5LZ-01", "qty": 3},
        {"series": "SY5", "orientation": "V", "part_no": "SY5320-5LZ-01", "qty": 1},
    ]
    result = assemble(test_bom, "PHI_Assembly_Test")
    print(f"\nOutput: {result}")
