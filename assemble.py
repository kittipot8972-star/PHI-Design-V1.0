"""
PHI Integration Design — STEP Assembly Engine v1.2
Fixes vs v1.1:
  - BUG FIX: station_pitch ใน positions.json SY5 แก้จาก 16→20mm
  - BUG FIX: SV/Blanking X อ้างอิงจาก global_x (left edge of manifold)
             ถูกต้องแล้ว ไม่เลื่อนออกนอก manifold
  - NEW: center_step() — re-centre real SMC STEP files ให้ origin
         อยู่กลาง bbox เหมือน parametric parts
  - NEW: แสดง position report ทุก part เมื่อ run
"""

import cadquery as cq
import json
from pathlib import Path

BASE_DIR   = Path(__file__).parent.parent
RULES_FILE = BASE_DIR / "assembly_rules" / "positions.json"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

with open(RULES_FILE) as f:
    RULES = json.load(f)


# ─────────────────────────────────────────────────────────────────
# HELPER: centre real STEP files
# ─────────────────────────────────────────────────────────────────

def center_step(shape: cq.Workplane) -> cq.Workplane:
    """
    SMC STEP files มักมี origin ที่มุมหรือพื้นผิว port
    ฟังก์ชันนี้ย้าย shape ให้ bbox center อยู่ที่ origin (0,0,0)
    เหมือน parametric geometry ที่สร้างด้วย cq.Workplane.box()
    """
    bb = shape.val().BoundingBox()
    cx = (bb.xmin + bb.xmax) / 2
    cy = (bb.ymin + bb.ymax) / 2
    cz = (bb.zmin + bb.zmax) / 2
    return shape.translate((-cx, -cy, -cz))


# ─────────────────────────────────────────────────────────────────
# PARAMETRIC GEOMETRY
# ─────────────────────────────────────────────────────────────────

def make_solenoid_valve(series: str, orientation: str = "V") -> cq.Workplane:
    """
    Origin ที่ bbox center.
    X = manifold_width, Y = manifold_depth*0.7, Z = sv_height_above_manifold
    """
    r = RULES["series_rules"][series]
    w = r["manifold_width"]
    h = r["sv_height_above_manifold"]
    d = r["manifold_depth"] * 0.7

    body = (cq.Workplane("XY").box(w, d, h)
            .edges("|Z").fillet(min(1.5, w * 0.1)))
    coil = (cq.Workplane("XY").box(w*0.8, d*0.5, h*0.35)
            .edges("|Z").fillet(min(1.0, w*0.07))
            .translate((0, 0, h*0.5 + h*0.35/2 - h/2)))
    plug = (cq.Workplane("XY").box(w*0.5, d*0.3, h*0.15)
            .translate((0, -d*0.3, h*0.5 + h*0.15/2 - h/2 + h*0.35)))
    return body.union(coil).union(plug)


def make_manifold(series: str, stations: int) -> cq.Workplane:
    """
    Origin ที่ bbox center (cq.box() centred automatically).
    X = station_pitch * stations + 20 (end-caps)
    Y = manifold_depth
    Z = manifold_height
    """
    r     = RULES["series_rules"][series]
    pitch = r["station_pitch"]      # ← ใช้ pitch จาก JSON เสมอ
    mh    = r["manifold_height"]
    mw    = r["manifold_width"]
    md    = r["manifold_depth"]
    total = pitch * stations + 20

    body = (cq.Workplane("XY").box(total, md, mh)
            .edges("|Y").fillet(min(1.5, mh*0.05)))

    # Station divider grooves
    for i in range(1, stations):
        x = -total/2 + 10 + i * pitch
        body = body.cut(
            cq.Workplane("XY").box(1.5, md+2, mh*0.4).translate((x, 0, mh*0.3))
        )

    # End caps
    cap_l = cq.Workplane("XY").box(8, md, mh).translate((-total/2 + 4, 0, 0))
    cap_r = cq.Workplane("XY").box(8, md, mh).translate(( total/2 - 4, 0, 0))
    return body.union(cap_l).union(cap_r)


def make_blanking_plate(series: str) -> cq.Workplane:
    """
    Origin ที่ bbox center.
    X = manifold_width, Z = sv_height*0.6
    """
    r = RULES["series_rules"][series]
    w = r["manifold_width"]
    h = r["sv_height_above_manifold"] * 0.6
    d = r["manifold_depth"] * 0.4
    return (cq.Workplane("XY").box(w, d, h)
            .edges("|Z").fillet(min(1.0, w*0.07)))


# ─────────────────────────────────────────────────────────────────
# STEP FILE LOADER
# ─────────────────────────────────────────────────────────────────

def load_or_generate(part_type: str, series: str,
                     orientation: str = "V", stations: int = 1) -> cq.Workplane:
    """
    โหลด STEP จริงถ้ามี (แล้ว re-centre) มิฉะนั้นสร้าง parametric
    """
    r = RULES["series_rules"][series]

    if part_type == "solenoid":
        key  = "model_file_h" if orientation == "H" else "model_file"
        path = MODELS_DIR / r[key]
        if path.exists():
            print(f"  ✓ Real STEP: {path.name}")
            return center_step(cq.importers.importStep(str(path)))
        print(f"  ○ Parametric: {series} SV ({orientation})")
        return make_solenoid_valve(series, orientation)

    elif part_type == "manifold":
        fname = r["manifold_model"].replace("XX", str(stations).zfill(2))
        path  = MODELS_DIR / fname
        if path.exists():
            print(f"  ✓ Real STEP: {path.name}")
            return center_step(cq.importers.importStep(str(path)))
        print(f"  ○ Parametric: {series} Manifold {stations}st")
        return make_manifold(series, stations)

    elif part_type == "blanking":
        path = MODELS_DIR / f"blanking/{r['blanking_part']}.step"
        if path.exists():
            print(f"  ✓ Real STEP: {path.name}")
            return center_step(cq.importers.importStep(str(path)))
        print(f"  ○ Parametric: {series} Blanking Plate")
        return make_blanking_plate(series)

    raise ValueError(f"Unknown part_type: {part_type}")


# ─────────────────────────────────────────────────────────────────
# MAIN ASSEMBLER
# ─────────────────────────────────────────────────────────────────

def assemble(bom: list, output_name: str = "PHI_Assembly") -> str:
    """
    bom = list of dicts:
      {"series":"SY5","orientation":"H","part_no":"SY5420-5LZ-01","qty":3}

    ── Coordinate system ──
    ทุก part มี origin ที่ bbox CENTER (ทั้ง parametric และ real STEP)

    Manifold:
      center_X = global_x + total_length / 2
      center_Z = 0   →  top face = +mh/2

    SV / Blanking:
      center_X = global_x + 10 + station_index * pitch + pitch/2
              ← เริ่มจาก left edge ของ manifold เหมือนกัน
      center_Z = mh/2 + part_height/2
              ← วางบน top face ของ manifold พอดี
    """
    print(f"\n{'='*52}")
    print(f"  PHI Assembly Engine v1.2")
    print(f"  BOM: {len(bom)} line items")
    print(f"{'='*52}")

    # Group by series, expand qty
    groups: dict[str, list] = {}
    for item in bom:
        s = item["series"]
        if s not in groups:
            groups[s] = []
        for _ in range(item.get("qty", 1)):
            groups[s].append(item)

    asm      = cq.Assembly(name="PHI_Pneumatic_Assembly")
    global_x = 0.0     # left edge of current series block

    for series, items in groups.items():
        r     = RULES["series_rules"][series]
        pitch = r["station_pitch"]
        mh    = r["manifold_height"]
        sv_h  = r["sv_height_above_manifold"]
        bp_h  = sv_h * 0.6

        sv_count = len(items)
        spare    = 4 if sv_count > 10 else 2
        raw      = sv_count + spare
        stations = raw if raw % 2 == 0 else raw + 1
        blanks   = stations - sv_count
        total    = pitch * stations + 20

        print(f"\n── {series}: {sv_count} SV + {blanks} blank = {stations} station ──")
        print(f"   pitch={pitch}mm | manifold length={total:.1f}mm | height={mh}mm")

        # MANIFOLD
        mf_cx = global_x + total / 2
        asm.add(
            load_or_generate("manifold", series, stations=stations),
            name=f"{series}_Manifold_{stations}st",
            loc=cq.Location(cq.Vector(mf_cx, 0, 0))
        )
        print(f"   Manifold  cx={mf_cx:.1f}  cz=0  top=+{mh/2:.1f}")

        # SOLENOID VALVES
        for i, item in enumerate(items):
            ori    = item.get("orientation", "V")
            pno    = item.get("part_no", f"{series}_SV")
            sv_cx  = global_x + 10 + i * pitch + pitch / 2
            sv_cz  = mh / 2 + sv_h / 2
            angle  = 90.0 if ori == "H" else 0.0
            asm.add(
                load_or_generate("solenoid", series, ori),
                name=f"{series}_SV_{i+1}_{pno}",
                loc=cq.Location(cq.Vector(sv_cx, 0, sv_cz),
                                cq.Vector(0, 0, 1), angle)
            )
            print(f"   SV {i+1:2d} ({ori})  cx={sv_cx:.1f}  cz={sv_cz:.1f}")

        # BLANKING PLATES
        for j in range(blanks):
            idx   = sv_count + j
            bp_cx = global_x + 10 + idx * pitch + pitch / 2
            bp_cz = mh / 2 + bp_h / 2
            asm.add(
                load_or_generate("blanking", series),
                name=f"{series}_Blanking_{j+1}",
                loc=cq.Location(cq.Vector(bp_cx, 0, bp_cz))
            )
            print(f"   Blank {j+1}     cx={bp_cx:.1f}  cz={bp_cz:.1f}")

        global_x += total + 30   # 30mm gap between series

    # EXPORT
    out_path = OUTPUT_DIR / f"{output_name}.step"
    print(f"\nExporting → {out_path.name} ...")
    asm.save(str(out_path))
    print(f"Done! {out_path.stat().st_size/1024:.1f} KB")
    return str(out_path)


# ─────────────────────────────────────────────────────────────────
# CLI TEST
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_bom = [
        {"series": "SY5", "orientation": "H", "part_no": "SY5420-5LZ-01", "qty": 3},
        {"series": "SY5", "orientation": "V", "part_no": "SY5320-5LZ-01", "qty": 1},
    ]
    result = assemble(test_bom, "PHI_Assembly_Fixed")
    print(f"\nOutput: {result}")
