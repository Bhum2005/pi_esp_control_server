"""ไล่ทดสอบระบบหอพักทั้งเส้นทาง: หุ่นส่งรูป -> เจ้าของหอคีย์เลข -> ลูกบ้านเห็น"""
import base64
import json
import sys
import time
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8201"
TOKEN = "tok-test"
import os
OWNER_PW = os.environ.get("TEST_OWNER_PW", "testowner123")
ok = fail = 0


def check(label, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print("  ok   %s" % label)
    else:
        fail += 1
        print("  FAIL %s  %s" % (label, extra))


def client():
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(CookieJar()))


def call(op, path, data=None, headers=None, raw=False):
    req = urllib.request.Request(BASE + path,
                                 data=data if raw else
                                 (json.dumps(data).encode() if data else None),
                                 method="POST" if data is not None else "GET")
    if data is not None and not raw:
        req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with op.open(req, timeout=10) as r:
            body = r.read()
            try:
                return r.status, json.loads(body)
            except ValueError:
                return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, body


def jpg(text, w=640, h=480):
    import cv2
    import numpy as np
    im = np.full((h, w, 3), 235, np.uint8)
    cv2.putText(im, text, (30, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.6,
                (30, 30, 30), 4)
    return cv2.imencode(".jpg", im)[1].tobytes()


anon = client()
print("\n1. ยังไม่ล็อกอิน")
s, b = call(anon, "/api/owner/rooms")
check("ขอข้อมูลเจ้าของหอโดยไม่ล็อกอิน ต้องโดนปฏิเสธ", s == 401, s)
s, b = call(anon, "/")
check("หน้าแรกเป็นหน้าล็อกอิน",
      s == 200 and "มิเตอร์หอพัก" in b.decode("utf-8", "ignore"), s)

print("\n2. หุ่นส่งรูป")
meta = base64.b64encode(json.dumps(
    {"room": "101", "kind": "water"}).encode()).decode()
s, b = call(anon, "/push", jpg("W 0 1 2 3"), raw=True, headers={
    "X-Token": TOKEN, "X-Name": "shot_20260915_080000.jpg", "X-Meta": meta})
check("ส่งรูปน้ำห้อง 101 เดือนกันยายน", s == 200 and b.get("room") == "101", b)

s, b = call(anon, "/push", jpg("X"), raw=True, headers={
    "X-Token": "wrong-token", "X-Name": "shot_20260915_080001.jpg"})
check("โทเคนผิดต้องโดนปฏิเสธ", s == 403, s)

for name, room, kind in [
        ("shot_20261014_080000.jpg", "101", "water"),
        ("shot_20261014_080100.jpg", "101", "power"),
        ("shot_20261014_081000.jpg", "102", "water"),
        ("shot_20261014_082000.jpg", "", "other")]:
    m = base64.b64encode(json.dumps({"room": room, "kind": kind}).encode()).decode()
    call(anon, "/push", jpg("%s %s" % (room or "?", kind)), raw=True,
         headers={"X-Token": TOKEN, "X-Name": name, "X-Meta": m})
print("  (ส่งครบ 5 ใบ)")

print("\n3. เจ้าของหอ")
own = client()
s, b = call(own, "/api/login", {"role": "owner", "password": "ผิดแน่นอน"})
check("รหัสผิดเข้าไม่ได้", s == 401, s)
s, b = call(own, "/api/login", {"role": "owner", "password": OWNER_PW})
check("รหัสถูกเข้าได้", s == 200 and b.get("role") == "owner", b)

s, b = call(own, "/api/owner/add-room", {"room": "101", "name": "พี่หมู"})
check("เพิ่มห้อง 101 ได้รหัสมา", s == 200 and len(b.get("password", "")) == 6, b)
PW101 = b.get("password")
s, b2 = call(own, "/api/owner/add-room", {"room": "101"})
check("เพิ่มห้องซ้ำไม่ได้", s == 400, s)
call(own, "/api/owner/add-room", {"room": "102", "name": "น้องแนน"})
call(own, "/api/owner/add-room", {"room": "103"})
s, b = call(own, "/api/owner/add-room", {"room": "ห้อง ที่ มีช่องว่าง"})
check("เลขห้องแปลก ๆ ไม่ผ่าน", s == 400, s)

s, b = call(own, "/api/owner/rooms?month=2026-10")
check("มี 3 ห้อง", len(b["rooms"]) == 3, b)
check("มีรูปค้างไม่ระบุห้อง 1 ใบ", b["inbox"] == 1, b["inbox"])

s, b = call(own, "/api/owner/set-photo",
            {"name": "shot_20260915_080000.jpg", "reading": "120"})
check("คีย์เลขเดือนก่อนได้", s == 200 and b["reading"] == "120", b)
s, b = call(own, "/api/owner/set-photo",
            {"name": "shot_20261014_080000.jpg", "reading": "138.5"})
check("คีย์เลขเดือนนี้ได้", s == 200, b)
s, b = call(own, "/api/owner/set-photo",
            {"name": "shot_20261014_080100.jpg", "reading": "2045"})
check("คีย์เลขไฟได้", s == 200, b)

s, b = call(own, "/api/owner/set-photo",
            {"name": "shot_20261014_082000.jpg", "room": "103",
             "kind": "water", "reading": "77"})
check("จัดรูปค้างเข้าห้อง 103 ได้", s == 200 and b["room"] == "103", b)
s, b = call(own, "/api/owner/rooms?month=2026-10")
check("ไม่มีรูปค้างแล้ว", b["inbox"] == 0, b["inbox"])

s, b = call(own, "/api/owner/room?room=101")
w = b["readings"]["water"]
check("ห้อง 101 มีเลขน้ำสองเดือน", len(w) == 2, w)
check("คำนวณหน่วยที่ใช้ถูก 138.5-120=18.5",
      w[-1]["used"] == 18.5, w[-1] if w else None)

print("\n4. ลูกบ้าน")
ten = client()
s, b = call(ten, "/api/login", {"role": "tenant", "room": "101",
                                "password": "999999"})
check("รหัสผิดเข้าไม่ได้", s == 401, s)
s, b = call(ten, "/api/login", {"role": "tenant", "room": "101",
                                "password": PW101})
check("รหัสถูกเข้าได้", s == 200, b)
s, b = call(ten, "/api/me")
check("เห็นห้องตัวเอง", b.get("room") == "101", b.get("room"))
check("เห็นเฉพาะรูปห้องตัวเอง",
      all(p["room"] == "101" for p in b["photos"]), b["photos"])
check("เห็นหน่วยที่ใช้", b["readings"]["water"][-1]["used"] == 18.5, b)

s, b = call(ten, "/api/owner/rooms")
check("ลูกบ้านเรียก API เจ้าของหอไม่ได้", s == 401, s)
s, b = call(ten, "/p/shot_20261014_081000.jpg")   # รูปห้อง 102
check("ลูกบ้านเปิดรูปห้องอื่นไม่ได้", s == 403, s)
s, b = call(ten, "/p/shot_20261014_080000.jpg")   # รูปห้องตัวเอง
check("ลูกบ้านเปิดรูปห้องตัวเองได้", s == 200, s)

s, b = call(anon, "/p/shot_20261014_080000.jpg")
check("คนไม่ล็อกอินเปิดรูปไม่ได้", s == 403, s)

print("\n5. โครงสร้างโฟลเดอร์")
root = os.path.expanduser(sys.argv[2] if len(sys.argv) > 2 else "~/hubtest")
want = os.path.join(root, "photos", "101", "2026-10",
                    "shot_20261014_080000.jpg")
check("รูปอยู่ใน photos/101/2026-10/", os.path.exists(want), want)
moved = os.path.join(root, "photos", "103", "2026-10",
                     "shot_20261014_082000.jpg")
check("รูปที่ย้ายห้องถูกย้ายไฟล์จริง", os.path.exists(moved), moved)

print("\n%d ผ่าน, %d ไม่ผ่าน" % (ok, fail))
sys.exit(1 if fail else 0)
