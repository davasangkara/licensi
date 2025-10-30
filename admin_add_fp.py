import requests
import os
import sys

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
ADMIN_KEY = os.getenv("ADMIN_KEY", "changeme")

def add_machine(machine_id, note=""):
    r = requests.post(
        f"{API_URL}/admin/add",
        json={"machine_id": machine_id, "note": note},
        headers={
            "X-API-KEY": ADMIN_KEY,
            "Content-Type": "application/json"
        },
        timeout=10
    )
    print(r.status_code, r.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python admin_add_fp.py <machine_id> [note]")
        sys.exit(1)

    mid = sys.argv[1]
    note = sys.argv[2] if len(sys.argv) > 2 else ""
    add_machine(mid, note)
