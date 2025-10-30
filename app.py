import os
from flask import Flask, request, jsonify, abort
from models import db, License
from datetime import datetime

# ambil secret dari env
ADMIN_KEY = os.getenv("ADMIN_KEY", "changeme")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# bikin tabel kalau belum ada
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET"])
def home():
    return {
        "status": "online",
        "service": "license-server",
        "time_utc": datetime.utcnow().isoformat() + "Z",
        "endpoints": {
            "POST /check_license": "cek akses client",
            "POST /admin/add": "tambah machine id (admin)",
            "GET  /admin/list": "lihat semua (admin)",
            "POST /admin/remove": "hapus machine id (admin)"
        }
    }, 200

# =========================
#  CLIENT ENDPOINT
# =========================
@app.route("/check_license", methods=["POST"])
def check_license():
    body = request.get_json(force=True)
    machine_id = body.get("machine_id")
    if not machine_id:
        return jsonify({"error": "machine_id required"}), 400

    lic = License.query.filter_by(machine_id=machine_id).first()
    allowed = bool(lic)

    return jsonify({"allowed": allowed}), 200

# =========================
#  ADMIN AUTH
# =========================
def require_admin():
    key = request.headers.get("X-API-KEY")
    if not key or key != ADMIN_KEY:
        abort(401)

# =========================
#  ADMIN ENDPOINTS
# =========================
@app.route("/admin/add", methods=["POST"])
def admin_add():
    require_admin()

    body = request.get_json(force=True)
    machine_id = body.get("machine_id")
    note = body.get("note", "")

    if not machine_id:
        return jsonify({"error": "machine_id required"}), 400

    # jangan double
    if License.query.filter_by(machine_id=machine_id).first():
        return jsonify({"error": "already exists"}), 400

    lic = License(machine_id=machine_id, note=note)
    db.session.add(lic)
    db.session.commit()

    return jsonify({"ok": True, "id": lic.id}), 201

@app.route("/admin/list", methods=["GET"])
def admin_list():
    require_admin()

    rows = License.query.order_by(License.created_at.desc()).all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "machine_id": r.machine_id,
            "note": r.note,
            "created_at": r.created_at.isoformat() + "Z"
        })
    return jsonify(out), 200

@app.route("/admin/remove", methods=["POST"])
def admin_remove():
    require_admin()

    body = request.get_json(force=True)
    machine_id = body.get("machine_id")
    if not machine_id:
        return jsonify({"error": "machine_id required"}), 400

    lic = License.query.filter_by(machine_id=machine_id).first()
    if not lic:
        return jsonify({"error": "not found"}), 404

    db.session.delete(lic)
    db.session.commit()

    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    # lokal dev
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
