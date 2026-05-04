"""
PHI Integration Design — Assembly API v2
POST /api/assemble       → sync  (รอจนเสร็จ ส่ง STEP กลับ)
POST /api/assemble-async → async (คืน job_id ทันที)
GET  /api/job/<id>       → ดู status
GET  /api/download/<id>  → ดาวน์โหลด STEP
GET  /health             → healthcheck
"""

from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import sys, os, uuid, threading, time, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))
from assemble import assemble, RULES

app  = Flask(__name__)
CORS(app, origins="*")

BASE_DIR     = Path(__file__).parent.parent
OUTPUT_DIR   = BASE_DIR / "output"
PREVIEWS_DIR = BASE_DIR / "previews"
OUTPUT_DIR.mkdir(exist_ok=True)
PREVIEWS_DIR.mkdir(exist_ok=True)

jobs: dict = {}
VALID_SERIES = set(RULES["series_rules"].keys())


def validate_bom(bom):
    if not isinstance(bom, list) or len(bom) == 0:
        return "bom must be a non-empty list"
    for i, item in enumerate(bom):
        if not isinstance(item, dict):
            return f"bom[{i}] must be an object"
        if item.get("series") not in VALID_SERIES:
            return f"bom[{i}].series '{item.get('series')}' invalid. Valid: {sorted(VALID_SERIES)}"
        if item.get("orientation") not in ("V", "H"):
            return f"bom[{i}].orientation must be 'V' or 'H'"
        qty = item.get("qty", 1)
        if not isinstance(qty, int) or qty < 1 or qty > 50:
            return f"bom[{i}].qty must be integer 1–50"
    return None


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "engine": "CadQuery 2.7",
        "valid_series": sorted(VALID_SERIES),
        "jobs_active": sum(1 for j in jobs.values() if j["status"] == "processing"),
        "jobs_done":   sum(1 for j in jobs.values() if j["status"] == "done"),
    })


@app.route("/api/assemble", methods=["POST"])
def api_assemble():
    data = request.get_json(force=True, silent=True) or {}
    bom  = data.get("bom", [])
    name = (data.get("name") or "PHI_Assembly").replace(" ", "_")[:60]
    err  = validate_bom(bom)
    if err:
        return jsonify({"error": err}), 400
    job_id = uuid.uuid4().hex[:8]
    log.info(f"[{job_id}] Sync assemble — {len(bom)} items")
    try:
        out_path = assemble(bom, f"{name}_{job_id}")
        return send_file(out_path, as_attachment=True,
                         download_name=f"{name}.step",
                         mimetype="application/step")
    except Exception as e:
        log.error(f"[{job_id}] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/assemble-async", methods=["POST"])
def api_assemble_async():
    data = request.get_json(force=True, silent=True) or {}
    bom  = data.get("bom", [])
    name = (data.get("name") or "PHI_Assembly").replace(" ", "_")[:60]
    err  = validate_bom(bom)
    if err:
        return jsonify({"error": err}), 400
    job_id   = uuid.uuid4().hex[:8]
    out_name = f"{name}_{job_id}"
    jobs[job_id] = {"status": "processing", "name": out_name, "started": time.time()}
    log.info(f"[{job_id}] Async assemble — {len(bom)} items")

    def run():
        try:
            out_path = assemble(bom, out_name)
            jobs[job_id].update({"status": "done", "path": out_path,
                                  "elapsed": round(time.time()-jobs[job_id]["started"], 1)})
            log.info(f"[{job_id}] Done — {jobs[job_id]['elapsed']}s")
        except Exception as e:
            jobs[job_id].update({"status": "error", "error": str(e)})
            log.error(f"[{job_id}] Error: {e}")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "processing"})


@app.route("/api/job/<job_id>")
def api_job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    resp = {"status": job["status"]}
    if job["status"] == "done":
        resp["download_url"] = f"/api/download/{job_id}"
        resp["elapsed_sec"]  = job.get("elapsed")
    elif job["status"] == "error":
        resp["error"] = job.get("error")
    else:
        resp["elapsed_sec"] = round(time.time() - job["started"], 1)
    return jsonify(resp)


@app.route("/api/download/<job_id>")
def api_download(job_id):
    job = jobs.get(job_id)
    if not job or job["status"] != "done":
        abort(404)
    base = job["name"].rsplit("_", 1)[0]
    return send_file(job["path"], as_attachment=True,
                     download_name=f"{base}.step",
                     mimetype="application/step")


@app.route("/api/preview/<path:part_no>")
def api_preview(part_no):
    safe = part_no.replace("/","_").replace("..","").replace(" ","_")
    for ext in [".png", ".jpg"]:
        p = PREVIEWS_DIR / f"{safe}{ext}"
        if p.exists():
            return send_file(str(p), mimetype="image/png")
    abort(404)


def _cleanup():
    while True:
        time.sleep(300)
        now = time.time()
        for jid in [k for k,j in list(jobs.items()) if now-j.get("started",now) > 3600]:
            job = jobs.pop(jid, None)
            if job and job.get("path"):
                try: Path(job["path"]).unlink()
                except: pass

threading.Thread(target=_cleanup, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    log.info(f"PHI Assembly API → http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
