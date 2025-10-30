import uuid, hashlib, platform, sys, requests, time

LICENSE_CHECK_URL = "http://127.0.0.1:5000/check_license"

def get_machine_fingerprint():
    raw = str(uuid.getnode()) + platform.node() + platform.platform()
    return hashlib.sha256(raw.encode()).hexdigest()

def check_license_remote():
    fp = get_machine_fingerprint()
    try:
        r = requests.post(LICENSE_CHECK_URL, json={"fingerprint": fp}, timeout=5)
        data = r.json()
    except Exception as e:
        print("[!] License server error:", e)
        sys.exit(1)

    if not data.get("allowed", False):
        print("[❌] LISENSI DITOLAK")
        print("Machine ID:", fp)
        sys.exit(1)

    print("[✅] Lisensi valid. Lanjut...")

def main():
    print("Program utama jalan... (contoh pekerjaan)")
    for i in range(3,0,-1):
        print("Working", i)
        time.sleep(1)

if __name__ == "__main__":
    check_license_remote()
    main()
