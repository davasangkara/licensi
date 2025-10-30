#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ---------------- License check (client-side) ----------------
import uuid
import hashlib
import platform
import sys
import requests
import json
import time
import random
import string
from urllib.parse import urljoin, quote_plus

LICENSE_CHECK_URL = "http://127.0.0.1:5000/check_license"
# contoh production:
# LICENSE_CHECK_URL = "https://license.digitalconvert.id/check_license"

def get_machine_fingerprint():
    raw = (
        str(uuid.getnode()) +
        platform.node() +
        platform.platform()
    )
    return hashlib.sha256(raw.encode()).hexdigest()

def check_license_remote():
    fp = get_machine_fingerprint()
    try:
        r = requests.post(LICENSE_CHECK_URL, json={"fingerprint": fp}, timeout=5)
        data = r.json()
    except Exception as e:
        print("[!] License server error, akses ditolak.")
        print("Detail:", e)
        sys.exit(1)

    if not data.get("allowed", False):
        print("========================================")
        print("[❌] LISENSI DITOLAK")
        print("Machine ID :", fp)
        print("Pesan      : Device ini belum terdaftar.")
        print("Hubungi admin untuk whitelist.")
        print("========================================")
        sys.exit(1)

    # kalau allowed True, lanjut normal
    print("[✅] Lisensi valid untuk device ini.")

# ---------------- GENCO AUTO TOOL (original program) ----------------

BASE_WEB = "https://genconusantara.com"
API_BASE = "https://appapigo.genconusantara.com"
ACCOUNTS_FILE = "accounts.json"
ORDERS_FILE = "orders.json"

SENDCODE = "/api/front/sendCode"
LOGIN_MOBILE = "/api/front/login/mobile"
CHECKPHONE = "/api/front/user/checkPhone"
USER_INFO = "/api/front/user"
SET_PASSWORD = "/api/front/user/setPassword"
ORDER_CREATE = "/api/front/virtual-product/order/create"
ORDER_PAY = "/api/front/self-order/pay/create"
USER_EVENT = "/api/front/user-events"

# === HEADER TEMPLATE ===
WEB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36",
    "Accept-Encoding": "gzip, deflate",  # fix decode issue
    "Content-Type": "application/json",
    "sec-ch-ua-platform": '"Android"',
    "sec-ch-ua": '"Android WebView";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?1",
    "origin": "https://genconusantara.com",
    "x-requested-with": "mark.via.gr",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://genconusantara.com/",
    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "priority": "u=1, i"
}

APP_HEADERS = {
    "User-Agent": "Dart/3.9 (dart:io)",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "accept-language": "zh"
}

DEVICE_MODELS = ["TP1A.220624.014", "M2101K7BNY", "POCOF3", "RMX3301", "VIVO2206", "SM-G991B"]
NAMES = ["Agus", "Andi", "Bagas", "Rizky", "Dewi", "Putri", "Bunga", "Yudha", "Dimas", "Rani", "Sinta", "Indra"]

# === HELPERS ===
def random_name():
    base = random.choice(NAMES)
    return f"{base}{random.randint(100,9999)}"

def random_email():
    letters = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{letters}@gmail.com"

def normalize_phone(num):
    return "0" + num[3:] if num.startswith("+62") else ("0" + num[2:] if num.startswith("62") else num.strip())

def to_international(num):
    return "+62" + num[1:] if num.startswith("0") else ("+" + num if num.startswith("62") else num)

def save_json(path, data):
    try:
        arr = []
        try:
            arr = json.load(open(path, "r", encoding="utf-8"))
        except FileNotFoundError:
            pass
        arr.append(data)
        json.dump(arr, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Gagal simpan {path}: {e}")

def random_device_id():
    return f"NATIVE_{random.choice(DEVICE_MODELS)}.{random.randint(100,999)}"

def register_device_event(s, device_id, device_ip=None):
    payload = {"device_id": device_id, "event_code": "LaunchApp", "platform": "android", "version": "1.2.7"}
    if device_ip:
        payload["device_ip"] = device_ip
    try:
        r = s.post(urljoin(API_BASE, USER_EVENT), json=payload, timeout=10, headers=APP_HEADERS)
        j = r.json()
        data = j.get("data", {})
        dev = data.get("deviceId") or data.get("device_id") or device_id
        print(f"[+] Device registered: {dev}")
        return dev
    except Exception as e:
        print("[!] Gagal register device event:", e)
        return device_id

# === REGISTER WEB ===
def register_web():
    print("\n=== [1] REGISTER VIA WEB ===")
    phone = normalize_phone(input("Nomor HP: ").strip())
    invite = input("Kode Reff (default EXKHE1): ").strip() or "EXKHE1"
    s = requests.Session()
    s.headers.update(WEB_HEADERS)
    try:
        s.get(f"{BASE_WEB}/register?inviteCode={invite}", timeout=8)
    except:
        pass

    print(f"[+] Kirim OTP ke {phone} ...")
    try:
        r = s.post(urljoin(API_BASE, SENDCODE), json={"phone": phone}, timeout=15)
        j = r.json()
    except Exception:
        print("[!] Respon tidak JSON:", r.text if 'r' in locals() else "")
        return
    if j.get("code") != 200:
        print("[!] Kirim OTP gagal:", j)
        return

    otp = input("Masukkan OTP (6 digit): ").strip()
    if not otp:
        return
    data = {"phone": phone, "captcha": otp, "invite_code": invite}
    try:
        r = s.post(urljoin(API_BASE, LOGIN_MOBILE), json=data, headers=WEB_HEADERS, timeout=15)
        j = r.json()
    except Exception:
        print("[!] Respon tidak JSON:", r.text if 'r' in locals() else "")
        return

    if j.get("code") == 200:
        token = j["data"]["token"]
        uid = j["data"]["uid"]
        print(f"[✅] Register sukses UID {uid}")
        save_json(ACCOUNTS_FILE, {"mode": "web", "phone": phone, "invite": invite, "token": token, "uid": uid})
    else:
        print("[!] Register gagal:", j)

# === LOGIN + TOPUP ===
def login_app():
    print("\n=== [2] LOGIN VIA APP + TOPUP ===")
    phone = input("Nomor HP: ").strip()
    phone08 = normalize_phone(phone)
    intl = to_international(phone08)
    s = requests.Session()
    s.headers.update(APP_HEADERS)

    dev_manual = input("Masukkan device_id (kosong = auto): ").strip() or random_device_id()
    dev_ip = input("Device IP (kosong skip): ").strip() or None
    device_id = register_device_event(s, dev_manual, dev_ip)

    try:
        s.get(f"{API_BASE}{CHECKPHONE}?phone={quote_plus(intl)}", timeout=10)
    except:
        pass

    print(f"[+] Kirim OTP ke {phone08} ...")
    try:
        r = s.post(f"{API_BASE}{SENDCODE}?phone={quote_plus(intl)}",
                   headers={"User-Agent": APP_HEADERS["User-Agent"], "Accept-Encoding": "gzip", "content-type": "application/x-www-form-urlencoded"},
                   timeout=10)
        j = r.json()
        print("→", j)
        if j.get("code") != 200:
            print("[!] Gagal kirim OTP:", j)
            return
    except Exception as e:
        print("[!] Error kirim OTP:", e)
        return

    otp = input("Masukkan OTP: ").strip()
    if not otp:
        return
    data = {"phone": intl, "captcha": otp, "spread_spid": 0, "device_id": device_id}

    try:
        print("[+] Login verifikasi OTP ...")
        r = s.post(urljoin(API_BASE, LOGIN_MOBILE), json=data, timeout=15)
        j = r.json()
        if j.get("code") != 200:
            print("[!] Login gagal:", j)
            return
        token = j["data"]["token"]
        uid = j["data"]["uid"]
        print(f"[✅] Login sukses UID {uid}")

        headers_auth = APP_HEADERS.copy()
        headers_auth["authorization"] = token

        try:
            r = s.get(urljoin(API_BASE, USER_INFO), headers=headers_auth, timeout=10)
            info = r.json().get("data", {})
            print(f"[📱] {info.get('phone')} | Saldo: {info.get('nowMoney')} | Invite: {info.get('inviteCode')}")
        except:
            info = {}

        pw = "Akukeren123"
        r = s.post(urljoin(API_BASE, SET_PASSWORD), headers=headers_auth, json={"password": pw, "inviteCode": "EXKHE1"})
        print(f"[🔒] Password diset otomatis: {pw}")

        uname = random_name()
        email = random_email()

        save_json(ACCOUNTS_FILE, {"mode": "app", "phone": phone08, "uid": uid, "token": token, "device_id": device_id, "email": email, "name": uname, "password": pw})

        if input("Top-up pulsa sekarang? (Y/n): ").strip().lower() == "n":
            return
        print("\n=== AUTO TOPUP ===")
        target = normalize_phone(input("Nomor tujuan (08...): ").strip())
        paytype = input("Metode (OVO/ShopeePay) [OVO]: ").strip() or "OVO"

        payload_order = {
            "productId": 2, "skuKey": "5,000 IDR", "quantity": 1,
            "paymentMethod": paytype, "rechargeAccount": {"mobile_phone": target},
            "userName": uname, "userEmail": email
        }

        print(f"[🌀] Membuat order pulsa ke {target} ({paytype}) ...")
        orderNo = None
        for i in range(20):
            r = s.post(urljoin(API_BASE, ORDER_CREATE), headers=headers_auth, json=payload_order)
            try:
                j = r.json()
            except:
                j = {}
                print(f"[{i+1}/20] Non-JSON:", r.text if 'r' in locals() else "")
            if j.get("code") == 200:
                orderNo = j["data"]["orderNo"]
                amt = j["data"]["totalAmount"]
                print(f"[✅] Order sukses percobaan {i+1}: {orderNo} total {amt}")
                save_json(ORDERS_FILE, {"orderNo": orderNo, "amount": amt, "payType": paytype, "target": target, "email": email, "time": time.asctime()})
                break
            else:
                print(f"[{i+1}/20] Gagal ({j.get('message')}), retry 3s...")
                time.sleep(3)
        if not orderNo:
            print("[❌] Gagal buat order")
            return

        payload_pay = {"orderNo": orderNo, "payType": paytype, "userName": uname, "userPhone": phone08, "userEmail": email}
        r = s.post(urljoin(API_BASE, ORDER_PAY), headers=headers_auth, json=payload_pay, timeout=12)
        try:
            jpay = r.json()
        except:
            print("[!] Non-JSON:", r.text if 'r' in locals() else "")
            return
        if jpay.get("code") == 200:
            d = jpay["data"]
            print(f"\n[✅] PAYMENT READY!\nOrder: {d.get('orderNo')}\nTotal: {d.get('totalAmount')}\nURL: {d.get('payUrl')}")
            save_json(ORDERS_FILE, d)
        else:
            print("[!] Gagal link bayar:", jpay)
    except Exception as e:
        print("[!] Error login/topup:", e)

def main():
    while True:
        print("\n=== GENCO AUTO TOOL ===")
        print("[1] Register via Web")
        print("[2] Login via App + Topup Pulsa")
        print("[0] Exit")
        c = input("Pilih menu: ").strip()
        if c == "1":
            register_web()
        elif c == "2":
            login_app()
        elif c == "0":
            break
        else:
            print("Pilihan salah")

if __name__ == "__main__":
    # cek lisensi dulu
    check_license_remote()
    # lalu lanjut ke program utama
    main()
