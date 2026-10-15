"""ทดสอบครบวงก่อนส่งไฟล์ — เน้นเส้นทางที่เคยพังจริง

เคสที่ใส่ไว้เพราะเคยพลาดมาแล้ว ไม่ใช่เคสที่คิดขึ้นเอง:
  1. ถ่ายรูปแล้วสตรีมต่อ -> ตัวเลขความหน่วงต้องไม่วิ่งหนี
  2. คนดูช้า -> ต้องข้ามเฟรม ไม่ใช่ไปรั้งให้ Pi ทิ้งเฟรม
  3. คนดูหายไปเฉย ๆ -> สายต้องถูกปิด ไม่ค้างสะสม
  4. ติดป้ายห้องทีหลัง -> ป้ายต้องไปถึงปลายทาง
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from http.cookiejar import CookieJar

S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)
PI = "http://127.0.0.1:9340"
HUB = "http://127.0.0.1:8250"
AUTH = ("admin", "12345678")
ok = fail = 0


def check(label, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print("  ok   %s" % label)
    else:
        fail += 1
        print("  FAIL %s   %s" % (label, extra))


def pi(path):
    m = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    m.add_password(None, PI, *AUTH)
    op = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(m))
    with op.open(PI + path, timeout=20) as r:
        b = r.read()
    try:
        return json.loads(b)
    except ValueError:
        return b


def stream_bytes(url, opener, seconds, rate=None):
    """อ่านสตรีมตามเวลาที่กำหนด rate = ไบต์/วินาทีถ้าอยากจำลองคนดูช้า"""
    got = frames = 0
    t0 = time.time()
    with opener.open(url, timeout=20) as r:
        while time.time() - t0 < seconds:
            chunk = r.read(16384)
            if not chunk:
                break
            got += len(chunk)
            frames += chunk.count(b"--FRAME")
            if rate:
                time.sleep(len(chunk) / float(rate))
    return got, frames


print("1. ความหน่วงต้องไม่วิ่งหนีหลังถ่ายรูป (บั๊กที่เพิ่งแก้)")
op = urllib.request.build_opener()
m = urllib.request.HTTPPasswordMgrWithDefaultRealm()
m.add_password(None, PI, *AUTH)
piop = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(m))
stream_bytes(PI + "/stream", piop, 2)
before = pi("/status")["lagMs"]
pi("/photo")
time.sleep(1)
stream_bytes(PI + "/stream", piop, 3)
mid = pi("/status")["lagMs"]
time.sleep(8)
stream_bytes(PI + "/stream", piop, 3)
after = pi("/status")["lagMs"]
print("     lagMs ก่อนถ่าย %s -> หลังถ่าย %s -> อีก 10 วิ %s"
      % (before, mid, after))
check("ไม่โตตามเวลา (ต่างกันไม่เกิน 2000 ms)", abs(after - mid) < 2000,
      "ต่าง %s" % abs(after - mid))

print("\n2. ผ่านตัวส่งต่อ: คนดูเร็วต้องได้เต็ม และ Pi ต้องไม่ต้องทิ้งเฟรม")
cj = CookieJar()
hop = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
req = urllib.request.Request(HUB + "/api/login", method="POST",
                             data=json.dumps({"role": "owner",
                                              "password": "testowner123"}).encode())
req.add_header("Content-Type", "application/json")
hop.open(req, timeout=10).read()
pi("/status")                       # ล้างตัวนับรอบก่อน
time.sleep(1.2)
got, fr = stream_bytes(HUB + "/stream", hop, 5)
st = pi("/status")
print("     ได้ %d เฟรม ใน 5 วิ | dropHz %s | lagMs %s"
      % (fr, st["dropHz"], st["lagMs"]))
check("ได้เฟรมใกล้เต็ม (>= 45 ใน 5 วิ ที่ 12fps)", fr >= 45, "ได้ %d" % fr)
check("Pi ไม่ต้องทิ้งเฟรม (dropHz < 2)", st["dropHz"] < 2, st["dropHz"])

print("\n3. คนดูช้า: ต้องข้ามเฟรม ไม่ใช่ไปรั้ง Pi")
got, fr = stream_bytes(HUB + "/stream", hop, 8, rate=120000)
st = pi("/status")
print("     คนดูช้าได้ %d เฟรม ใน 8 วิ | dropHz %s | lagMs %s"
      % (fr, st["dropHz"], st["lagMs"]))
check("ได้น้อยกว่าเต็ม แปลว่าข้ามเฟรมจริง", 0 < fr < 70, "ได้ %d" % fr)
check("Pi ยังไม่ต้องทิ้งเฟรม (dropHz < 3)", st["dropHz"] < 3, st["dropHz"])
check("ความหน่วงฝั่ง Pi ยังต่ำ (< 3000 ms)", st["lagMs"] < 3000, st["lagMs"])

print("\n4. คนดูเลิกดู: สายต้องถูกปิด ไม่ค้างสะสม")
time.sleep(3)
out = subprocess.run(
    ["bash", "-c",
     "ss -tn state established '( dport = :9340 )' 2>/dev/null | tail -n +2 | wc -l"],
    capture_output=True, text=True).stdout.strip()
check("ไม่มีสายค้างกับ Pi", out == "0", "เหลือ %s เส้น" % out)

print("\n5. ติดป้ายห้องทีหลังต้องไปถึงปลายทาง")
name = pi("/photo")["name"]
subprocess.run(["python3", os.path.join(ROOT, "pi", "push.py"), "--to", HUB,
                "--token", "tok-test", "--dir", os.path.expanduser("~/ptest3"),
                "--state", S + "/reg.json", "--once"],
               capture_output=True)
pi("/tag?f=%s&room=901&kind=power" % name)
time.sleep(1.1)
subprocess.run(["python3", os.path.join(ROOT, "pi", "push.py"), "--to", HUB,
                "--token", "tok-test", "--dir", os.path.expanduser("~/ptest3"),
                "--state", S + "/reg.json", "--once"],
               capture_output=True)
with hop.open(HUB + "/api/owner/photos?room=901", timeout=10) as r:
    rows = json.load(r)
check("รูปเข้าห้อง 901 หลังติดป้าย",
      any(x["name"] == name and x["kind"] == "power" for x in rows),
      [x["name"] for x in rows])

print("\n%d ผ่าน, %d ไม่ผ่าน" % (ok, fail))
sys.exit(1 if fail else 0)
