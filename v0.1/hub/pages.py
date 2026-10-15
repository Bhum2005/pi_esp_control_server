# -*- coding: utf-8 -*-
"""หน้าเว็บทั้งสามของระบบจดมิเตอร์

แยกไฟล์ออกมาจาก hub.py เพราะเป็นคนละเรื่องกัน แก้หน้าตาไม่ต้องแตะตรรกะ

แนวคิดการออกแบบ: ตัวเลขมิเตอร์แสดงเป็นช่องตัวเลขทีละหลัก เหมือนหน้าปัดจริง
ที่หุ่นไปถ่ายมา เป็นตัวเดินเรื่องของทั้งระบบ อย่างอื่นให้เงียบไว้
น้ำใช้หมึกน้ำเงินเขียว ไฟใช้หมึกส้มไหม้ แยกด้วยสีตลอดทุกหน้า
"""

HEAD = """<!DOCTYPE html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>%s</style></head><body>"""

CSS = """
:root{
  --paper:#E9EAE4; --card:#FFFFFF; --ink:#15191C; --dim:#6B7076;
  --line:#D3D5CC; --water:#17627F; --power:#A8560C; --warn:#9B2C2C;
  --ok:#2E7D4F;
  --f:"IBM Plex Sans Thai","Noto Sans Thai",system-ui,sans-serif;
  --r:10px;
}
@media (prefers-color-scheme:dark){:root{
  --paper:#121417; --card:#1A1D21; --ink:#E7E8E3; --dim:#8E949A;
  --line:#2A2E33; --water:#5FB2CE; --power:#E0963F; --warn:#E2756B;
  --ok:#6BCB92;}}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--paper);color:var(--ink);font-family:var(--f);
  line-height:1.5;-webkit-text-size-adjust:100%;
  font-feature-settings:"tnum" 1}
a{color:inherit}
button,input,select{font-family:inherit;font-size:inherit;color:inherit}
button{cursor:pointer}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}

/* ---- ช่องตัวเลขมิเตอร์ — ตัวเอกของหน้าเว็บนี้ ---- */
.meter{display:flex;gap:3px;align-items:stretch}
.meter b{display:flex;align-items:center;justify-content:center;
  min-width:30px;padding:7px 2px;font-size:25px;font-weight:700;
  background:var(--card);border:1.5px solid currentColor;border-radius:3px;
  font-variant-numeric:tabular-nums;line-height:1}
.meter.sm b{min-width:21px;font-size:17px;padding:4px 1px;border-width:1.2px}
.meter .dec{border-style:dashed;opacity:.75}
.water{color:var(--water)}
.power{color:var(--power)}
.meter.empty b{color:var(--dim);border-style:dotted;font-weight:400}

/* ---- ส่วนประกอบทั่วไป ---- */
.card{background:var(--card);border:1px solid var(--line);
  border-radius:var(--r)}
.btn{background:var(--ink);color:var(--paper);border:0;border-radius:8px;
  padding:10px 16px;font-weight:600;text-decoration:none;display:inline-block}
.btn.ghost{background:transparent;color:var(--ink);
  border:1px solid var(--line);font-weight:500}
.btn.sm{padding:6px 11px;font-size:13.5px;border-radius:7px}
.btn:disabled{opacity:.45;cursor:not-allowed}
input,select{background:var(--card);border:1px solid var(--line);
  border-radius:8px;padding:9px 11px;width:100%}
input:focus-visible,button:focus-visible,select:focus-visible{
  outline:2px solid var(--ink);outline-offset:2px}
label{display:block;font-size:13px;color:var(--dim);margin:0 0 5px}
.muted{color:var(--dim)}
.sep{height:1px;background:var(--line);border:0;margin:16px 0}
.err{color:var(--warn);font-size:14px;min-height:20px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

FOOT = "</body></html>"


# =====================================================================
# หน้าเข้าสู่ระบบ — แยกคนละหน้าระหว่างลูกบ้านกับเจ้าของหอ
# ---------------------------------------------------------------------
# แยกเพราะเป็นคนละงานกันจริง ๆ ลูกบ้านเข้าจากลิงก์ที่ติดหน้าห้อง
# เจ้าของหอเข้าจากทางที่ไม่ประกาศให้ใครรู้ ตั้งชื่อทางเองได้ด้วย --owner-path
# ผลพลอยได้ที่สำคัญ: หน้าลูกบ้านไม่มีอะไรบอกใบ้เลยว่าทางเข้าของเจ้าของหออยู่ไหน
LOGIN_BASE = (HEAD % ("เข้าสู่ระบบ · มิเตอร์หอพัก", CSS + """
body{display:grid;place-items:center;min-height:100dvh;padding:20px}
.box{width:100%;max-width:370px}
.plate{background:var(--card);border:1px solid var(--line);
  border-radius:var(--r);padding:20px}
h1{font-size:21px;margin:0 0 3px;font-weight:700;letter-spacing:-.01em}
.sub{color:var(--dim);font-size:14px;margin:0 0 18px}
.f{margin:0 0 13px}
.hint{font-size:12.5px;color:var(--dim);margin:14px 0 0;line-height:1.5}
.mark{display:flex;gap:3px;justify-content:center;margin:0 0 18px}
.mark b{min-width:26px;padding:6px 0;text-align:center;font-weight:700;
  border:1.5px solid currentColor;border-radius:3px;font-size:19px}
""") + """
<div class="box">
  <div class="mark">__MARK__</div>
  <div class="plate">
    <h1>__TITLE__</h1>
    <p class="sub">__SUB__</p>
    <form onsubmit="go(event)">
      <div class="f" id="roomf">
        <label for="room">เลขห้อง</label>
        <input id="room" autocomplete="username" inputmode="text"
          placeholder="เช่น 101">
      </div>
      <div class="f">
        <label for="pw">รหัสผ่าน</label>
        <input id="pw" type="password" autocomplete="current-password">
      </div>
      <p class="err" id="err"></p>
      <button class="btn" style="width:100%" id="btnLogin">เข้าสู่ระบบ</button>
    </form>
    <p class="hint">__HINT__</p>
  </div>
</div>
<script>
const role='__ROLE__';
if(role==='owner') document.getElementById('roomf').remove();
async function go(e){
  e.preventDefault();
  const b=document.getElementById('btnLogin'); b.disabled=true;
  const err=document.getElementById('err'); err.textContent='';
  try{
    const r=await fetch('/api/login',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({role:role,
        room:(document.getElementById('room')||{value:''}).value.trim(),
        password:document.getElementById('pw').value})});
    const j=await r.json();
    if(j.ok){location.href='__HOME__';return;}
    err.textContent=j.error||'เข้าสู่ระบบไม่สำเร็จ';
  }catch(ex){ err.textContent='ต่อเซิร์ฟเวอร์ไม่ได้'; }
  b.disabled=false;
}
(document.getElementById('room')||document.getElementById('pw')).focus();
</script>""" + FOOT)


def login_page(role, owner_path="/owner"):
    """สร้างหน้าล็อกอินของแต่ละฝั่งจากแม่แบบเดียวกัน"""
    if role == "tenant":
        sub = {"__ROLE__": "tenant", "__HOME__": "/",
               "__TITLE__": "มิเตอร์หอพัก",
               "__SUB__": "ดูเลขน้ำเลขไฟของห้องคุณ",
               "__HINT__": "รหัสของห้องขอได้ที่เจ้าของหอ",
               "__MARK__": '<b class="water">0</b><b class="water">0</b>'
                           '<b class="power">0</b><b class="power">0</b>'}
    else:
        sub = {"__ROLE__": "owner", "__HOME__": owner_path,
               "__TITLE__": "สำหรับเจ้าของหอ",
               "__SUB__": "จัดการห้องและจดมิเตอร์",
               "__HINT__": "รหัสแรกเข้าอยู่ในหน้าจอตอนเปิดระบบครั้งแรก",
               "__MARK__": '<b class="power">H</b><b class="power">U</b>'
                           '<b class="power">B</b>'}
    out = LOGIN_BASE.replace(
        "<title>เข้าสู่ระบบ · มิเตอร์หอพัก</title>",
        "<title>%s</title>" % ("เข้าสู่ระบบ · มิเตอร์หอพัก" if role == "tenant"
                               else "เจ้าของหอ · มิเตอร์หอพัก"))
    for k, v in sub.items():
        out = out.replace(k, v)
    return out


# =====================================================================
# หน้าลูกบ้าน
# ---------------------------------------------------------------------
# เปิดมาต้องเห็นคำตอบทันทีว่าเดือนนี้ใช้ไปเท่าไหร่ ไม่ต้องกดอะไรก่อน
# รูปมิเตอร์วางไว้ให้กดดูได้ เพราะเป็นหลักฐานว่าเลขที่คีย์มาจากไหน
TENANT = (HEAD % ("ห้องของฉัน · มิเตอร์หอพัก", CSS + """
header{border-bottom:1px solid var(--line);background:var(--card)}
.hrow{display:flex;align-items:center;gap:12px;padding-block:13px}
.room{font-size:24px;font-weight:700;letter-spacing:-.02em}
.room small{display:block;font-size:12.5px;color:var(--dim);font-weight:400;
  letter-spacing:0}
main{padding:20px 0 50px}
.two{display:grid;gap:14px;grid-template-columns:1fr 1fr}
@media(max-width:700px){.two{grid-template-columns:1fr}}
.util{padding:16px}
.uhead{display:flex;align-items:baseline;gap:9px;margin:0 0 12px}
.uhead h2{font-size:16px;margin:0;font-weight:600}
.uhead span{font-size:13px;color:var(--dim)}
.used{margin:13px 0 0;font-size:14px}
.used b{font-size:27px;font-weight:700;letter-spacing:-.02em}
.proof{margin:12px 0 0}
.proof img{width:100%;max-height:230px;object-fit:cover;
  border-radius:7px;border:1px solid var(--line);display:block;cursor:zoom-in}
h3{font-size:14px;font-weight:600;margin:26px 0 9px}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px;min-width:420px}
th,td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line)}
th{font-size:12.5px;color:var(--dim);font-weight:500}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.none{padding:28px 16px;text-align:center;color:var(--dim);font-size:14px}
#lb{position:fixed;inset:0;background:#000;display:none;z-index:9}
#lb.on{display:grid;grid-template-rows:1fr auto}
#lb img{width:100%;height:100%;object-fit:contain;min-height:0}
#lb div{padding:12px;text-align:center}
""") + """
<header><div class="wrap hrow">
  <div class="room" id="room">—<small id="rname">ห้องของฉัน</small></div>
  <span style="flex:1"></span>
  <a class="btn ghost sm" href="/out?to=/">ออก</a>
</div></header>
<main class="wrap">
  <div class="two">
    <section class="card util" id="u-water"></section>
    <section class="card util" id="u-power"></section>
  </div>
  <h3>ย้อนหลัง</h3>
  <div class="card scroll" id="hist"></div>
</main>
<div id="lb" onclick="this.classList.remove('on')">
  <img id="lbimg" alt=""><div class="muted">แตะเพื่อปิด</div></div>
<script>
const TH={water:'น้ำ',power:'ไฟ'};
const UNIT={water:'หน่วย',power:'หน่วย'};

function digits(v,cls,sm){
  // แสดงเป็นช่องตัวเลขทีละหลักเหมือนหน้าปัดมิเตอร์จริง
  if(v===null||v===undefined||v===''){
    return '<div class="meter empty '+cls+(sm?' sm':'')+'">'+
      '<b>–</b><b>–</b><b>–</b><b>–</b></div>';}
  const s=String(v).replace(/\\.0+$/,'');
  const [i,d]=s.split('.');
  let h='<div class="meter '+cls+(sm?' sm':'')+'">';
  String(i).padStart(4,'0').split('').forEach(c=>h+='<b>'+c+'</b>');
  if(d) d.split('').forEach(c=>h+='<b class="dec">'+c+'</b>');
  return h+'</div>';
}
function monthTH(m){
  if(!m) return '';
  const [y,mm]=m.split('-');
  const n=['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.',
           'ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
  return n[parseInt(mm,10)-1]+' '+(parseInt(y,10)+543-2500);
}
function card(kind,series,photos){
  const last=series.length?series[series.length-1]:null;
  let h='<div class="uhead"><h2>'+TH[kind]+'</h2>'+
    '<span>'+(last?monthTH(last.month):'ยังไม่มีข้อมูล')+'</span></div>';
  h+=digits(last?last.value:null,kind);
  if(last&&last.used!==null&&last.used!==undefined){
    h+='<p class="used">ใช้ไป <b class="'+kind+'">'+last.used+'</b> '+
       UNIT[kind]+'</p>';
  }else if(last){
    h+='<p class="used muted">เดือนแรกที่จด ยังเทียบกับเดือนก่อนไม่ได้</p>';
  }else{
    h+='<p class="used muted">ยังไม่มีการจดมิเตอร์</p>';
  }
  const p=photos.find(x=>x.kind===kind);
  if(p) h+='<div class="proof"><img loading="lazy" src="/t/'+p.name+
    '" alt="รูปมิเตอร์'+TH[kind]+'" onclick="zoom(\\''+p.name+'\\')"></div>';
  return h;
}
function zoom(n){document.getElementById('lbimg').src='/p/'+n;
  document.getElementById('lb').classList.add('on');}

(async function(){
  const d=await (await fetch('/api/me')).json();
  if(d.role!=='tenant'){location.href='/';return;}
  document.getElementById('room').firstChild.textContent='ห้อง '+d.room;
  document.getElementById('rname').textContent=d.name||'ห้องของฉัน';
  document.title='ห้อง '+d.room+' · มิเตอร์หอพัก';
  for(const k of ['water','power'])
    document.getElementById('u-'+k).innerHTML=card(k,d.readings[k],d.photos);

  const months={};
  for(const k of ['water','power'])
    d.readings[k].forEach(r=>{months[r.month]=months[r.month]||{};
      months[r.month][k]=r;});
  const keys=Object.keys(months).sort().reverse();
  const hist=document.getElementById('hist');
  if(!keys.length){hist.innerHTML='<p class="none">ยังไม่มีประวัติ '+
    'เมื่อเจ้าของหอจดมิเตอร์แล้วจะขึ้นที่นี่</p>';return;}
  let h='<table><tr><th>เดือน</th><th>น้ำ</th><th class="n">ใช้ไป</th>'+
    '<th>ไฟ</th><th class="n">ใช้ไป</th></tr>';
  keys.forEach(m=>{const w=months[m].water,p=months[m].power;
    h+='<tr><td>'+monthTH(m)+'</td>'+
      '<td>'+digits(w?w.value:null,'water',1)+'</td>'+
      '<td class="n">'+(w&&w.used!=null?w.used:'–')+'</td>'+
      '<td>'+digits(p?p.value:null,'power',1)+'</td>'+
      '<td class="n">'+(p&&p.used!=null?p.used:'–')+'</td></tr>';});
  hist.innerHTML=h+'</table>';
})();
</script>""" + FOOT)


# =====================================================================
# หน้าเจ้าของหอ
# ---------------------------------------------------------------------
# งานจริงของหน้านี้คือ "คีย์เลขให้ครบทุกห้องภายในวันเดียว"
# ทุกอย่างจึงจัดให้เห็นว่าห้องไหนยังขาด แล้วคีย์ต่อกันรวดเดียวได้
# รูปที่หุ่นถ่ายมาแต่ยังไม่รู้ว่าห้องไหน จะถูกดันขึ้นมาไว้บนสุด
OWNER = (HEAD % ("เจ้าของหอ · มิเตอร์หอพัก", CSS + """
header{border-bottom:1px solid var(--line);background:var(--card);
  position:sticky;top:0;z-index:4}
.hrow{display:flex;align-items:center;gap:10px;padding-block:11px;flex-wrap:wrap}
.hrow h1{font-size:17px;margin:0;font-weight:700}
main{padding:16px 0 60px}
.cols{display:grid;gap:16px;grid-template-columns:300px 1fr;
  align-items:start}
@media(max-width:820px){.cols{grid-template-columns:1fr}}
.panel{padding:14px}
.panel h2{font-size:14px;margin:0 0 11px;font-weight:600}
.rooms{display:flex;flex-direction:column;gap:1px}
.rm{display:flex;align-items:center;gap:9px;padding:9px 10px;
  background:transparent;border:0;border-radius:7px;width:100%;text-align:left}
.rm:hover{background:var(--paper)}
.rm[aria-current=true]{background:var(--ink);color:var(--paper)}
.rm .no{font-weight:600;min-width:46px}
.rm .nm{font-size:12.5px;color:var(--dim);flex:1;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.rm[aria-current=true] .nm{color:var(--paper);opacity:.7}
.pip{width:9px;height:9px;border-radius:50%;border:1.5px solid currentColor;
  display:inline-block;flex:0 0 auto}
.pip.on{background:currentColor}
.inbox{border:1px solid var(--warn);border-radius:var(--r);padding:12px 14px;
  margin:0 0 16px;display:flex;gap:11px;align-items:center;flex-wrap:wrap}
.inbox b{color:var(--warn)}
.shots{display:grid;gap:11px;
  grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.shot{border:1px solid var(--line);border-radius:9px;overflow:hidden;
  background:var(--card)}
.shot img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;
  background:var(--line);cursor:zoom-in}
.shot .f{padding:9px;display:flex;flex-direction:column;gap:7px}
.shot .when{font-size:12px;color:var(--dim)}
.rowf{display:flex;gap:6px}
.rowf input,.rowf select{padding:7px 9px;border-radius:7px;font-size:14px}
.saved{color:var(--ok);font-size:12px;min-height:16px}
.rowf [data-save]{flex:0 0 auto}
.none{padding:30px 14px;text-align:center;color:var(--dim);font-size:14px}
.sum{display:flex;gap:30px;flex-wrap:wrap;align-items:flex-start;
  padding:16px;margin:0 0 14px}
.sum .blk h3{margin:0 0 8px;font-size:13px;font-weight:500;color:var(--dim)}
.sum .use{margin:9px 0 0;font-size:13px}
.sum .acts{display:flex;gap:7px;padding-top:21px}
.legend{display:flex;gap:11px;font-size:12px;color:var(--dim);
  margin:0 0 9px;align-items:center}
.legend span{display:flex;gap:4px;align-items:center}
dialog{border:1px solid var(--line);border-radius:var(--r);padding:18px;
  background:var(--card);color:var(--ink);max-width:340px;width:92%}
dialog::backdrop{background:rgba(0,0,0,.5)}
.pw{font-size:27px;font-weight:700;letter-spacing:.09em;text-align:center;
  padding:14px;border:1px dashed var(--line);border-radius:8px;margin:12px 0}
#lb{position:fixed;inset:0;background:#000;display:none;z-index:9}
#lb.on{display:grid;grid-template-rows:1fr auto}
#lb img{width:100%;height:100%;object-fit:contain;min-height:0}
#lb div{padding:12px;text-align:center;color:#bbb}
""") + """
<header><div class="wrap hrow">
  <h1>มิเตอร์หอพัก</h1>
  <select id="month" style="width:auto" onchange="loadRooms()"></select>
  <span style="flex:1"></span>
  <a class="btn ghost sm" id="robotLink" href="__OWNER_PATH__/robot">คุมหุ่น</a>
  <button class="btn ghost sm" onclick="dlgAdd.showModal()">เพิ่มห้อง</button>
  <button class="btn ghost sm" onclick="dlgPw.showModal()">รหัสของฉัน</button>
  <a class="btn ghost sm" href="/out?to=__OWNER_PATH__">ออก</a>
</div></header>
<main class="wrap">
  <div id="inbox"></div>
  <div class="cols">
    <section class="card panel">
      <h2>ห้องทั้งหมด</h2>
      <div class="legend">
        <span><i class="pip water on"></i>จดน้ำแล้ว</span>
        <span><i class="pip power on"></i>จดไฟแล้ว</span>
      </div>
      <div class="rooms" id="rooms"></div>
    </section>
    <section id="detail"></section>
  </div>
</main>

<dialog id="dlgAdd"><form method="dialog" onsubmit="addRoom(event)">
  <h2 style="margin:0 0 14px;font-size:16px">เพิ่มห้อง</h2>
  <div style="margin:0 0 11px"><label for="nroom">เลขห้อง</label>
    <input id="nroom" placeholder="101"></div>
  <div style="margin:0 0 11px"><label for="nname">ชื่อผู้เช่า (ไม่ใส่ก็ได้)</label>
    <input id="nname"></div>
  <p class="err" id="adderr"></p>
  <div style="display:flex;gap:8px;justify-content:flex-end">
    <button class="btn ghost" type="button" onclick="dlgAdd.close()">ยกเลิก</button>
    <button class="btn">เพิ่มห้อง</button></div>
</form></dialog>

<dialog id="dlgShow"><div>
  <h2 style="margin:0 0 4px;font-size:16px" id="showTitle"></h2>
  <p class="muted" style="font-size:13px;margin:0">
    รหัสนี้แสดงครั้งเดียว จดใส่กระดาษให้ลูกบ้านก่อนปิด</p>
  <div class="pw" id="showPw"></div>
  <div style="display:flex;gap:8px;justify-content:flex-end">
    <button class="btn" onclick="dlgShow.close()">จดแล้ว</button></div>
</div></dialog>

<dialog id="dlgPw"><form method="dialog" onsubmit="setOwnerPw(event)">
  <h2 style="margin:0 0 14px;font-size:16px">เปลี่ยนรหัสเจ้าของหอ</h2>
  <div style="margin:0 0 11px"><label for="opw">รหัสใหม่ อย่างน้อย 8 ตัว</label>
    <input id="opw" type="password" autocomplete="new-password"></div>
  <p class="err" id="pwerr"></p>
  <div style="display:flex;gap:8px;justify-content:flex-end">
    <button class="btn ghost" type="button" onclick="dlgPw.close()">ยกเลิก</button>
    <button class="btn">เปลี่ยน</button></div>
</form></dialog>

<div id="lb" onclick="this.classList.remove('on')">
  <img id="lbimg" alt=""><div>แตะเพื่อปิด</div></div>

<script>
const TH={water:'น้ำ',power:'ไฟ',other:'อื่น ๆ'};
let month='', rooms=[], cur=null;

function monthTH(m){const [y,mm]=m.split('-');
  const n=['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.',
           'ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
  return n[parseInt(mm,10)-1]+' '+(parseInt(y,10)+543);}
function when(ts){return new Date(ts*1000).toLocaleString('th-TH',
  {day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'});}
function digits(v,cls,sm){
  if(v===null||v===undefined||v===''){
    return '<div class="meter empty '+cls+(sm?' sm':'')+'">'+
      '<b>–</b><b>–</b><b>–</b><b>–</b></div>';}
  const s=String(v).replace(/\\.0+$/,''); const [i,d]=s.split('.');
  let h='<div class="meter '+cls+(sm?' sm':'')+'">';
  String(i).padStart(4,'0').split('').forEach(c=>h+='<b>'+c+'</b>');
  if(d) d.split('').forEach(c=>h+='<b class="dec">'+c+'</b>');
  return h+'</div>';}
function zoom(n){document.getElementById('lbimg').src='/p/'+n;
  document.getElementById('lb').classList.add('on');}

function fillMonths(){
  const sel=document.getElementById('month'); const now=new Date();
  let h='';
  for(let i=0;i<13;i++){
    const d=new Date(now.getFullYear(),now.getMonth()-i,1);
    const k=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');
    h+='<option value="'+k+'">'+monthTH(k)+'</option>';}
  sel.innerHTML=h; month=sel.value;}

async function loadRooms(){
  month=document.getElementById('month').value;
  const d=await (await fetch('/api/owner/rooms?month='+month)).json();
  rooms=d.rooms;
  const el=document.getElementById('rooms');
  if(!rooms.length){
    el.innerHTML='<p class="none">ยังไม่มีห้อง<br>กดปุ่มเพิ่มห้องด้านบน</p>';
  }else{
    el.innerHTML=rooms.map(r=>
      '<button class="rm" aria-current="'+(cur===r.room)+'" '+
      'onclick="openRoom(\\''+r.room+'\\')">'+
      '<span class="no">'+r.room+'</span>'+
      '<span class="nm">'+(r.name||'')+'</span>'+
      '<span class="pip water'+(r.water?' on':'')+'"></span>'+
      '<span class="pip power'+(r.power?' on':'')+'"></span>'+
      '</button>').join('');
  }
  const ib=document.getElementById('inbox');
  ib.innerHTML = d.inbox ? '<div class="inbox">'+
    '<span>มีรูป <b>'+d.inbox+'</b> ใบที่ยังไม่ได้ระบุห้อง</span>'+
    '<button class="btn sm" onclick="openInbox()">จัดเข้าห้อง</button></div>' : '';
  if(cur) openRoom(cur); else if(d.inbox) openInbox();
  else if(rooms.length) openRoom(rooms[0].room);
}

async function openInbox(){
  cur=null;
  document.querySelectorAll('.rm').forEach(b=>b.setAttribute('aria-current',false));
  const ph=await (await fetch('/api/owner/photos?inbox=1')).json();
  document.getElementById('detail').innerHTML=
    '<div class="card panel"><h2>รูปที่ยังไม่ได้ระบุห้อง</h2>'+
    (ph.length?'<div class="shots">'+ph.map(shot).join('')+'</div>'
      :'<p class="none">ไม่มีรูปค้าง ทุกใบเข้าห้องเรียบร้อย</p>')+'</div>';
}

async function openRoom(room){
  cur=room;
  document.querySelectorAll('.rm .no').forEach(n=>
    n.parentElement.setAttribute('aria-current', n.textContent===room));
  const d=await (await fetch('/api/owner/room?room='+encodeURIComponent(room))).json();
  if(d.error){document.getElementById('detail').innerHTML=
    '<div class="card panel"><p class="none">'+d.error+'</p></div>';return;}
  // โชว์เลขของ "เดือนที่เลือกอยู่" ไม่ใช่เลขล่าสุดเสมอ
  // ไม่งั้นย้อนดูเดือนก่อนแล้วเลขข้างบนยังเป็นของเดือนนี้ จะเข้าใจผิดทันที
  const cm={};
  ['water','power'].forEach(k=>{
    cm[k]=d.readings[k].find(r=>r.month===month)||null;});
  const start=new Date(month+'-01').getTime();
  const end=new Date(new Date(month+'-01').setMonth(
    new Date(month+'-01').getMonth()+1)).getTime();
  const ph=d.photos.filter(p=>p.ts*1000>=start && p.ts*1000<end);

  let h='<div class="card sum">';
  ['water','power'].forEach(k=>{
    h+='<div class="blk"><h3>'+TH[k]+' · '+monthTH(month)+'</h3>'+
      digits(cm[k]?cm[k].value:null,k);
    if(cm[k]&&cm[k].used!=null)
      h+='<p class="use">ใช้ไป <b class="'+k+'">'+cm[k].used+'</b> หน่วย</p>';
    else if(cm[k]) h+='<p class="use muted">ไม่มีเดือนก่อนให้เทียบ</p>';
    else h+='<p class="use muted">ยังไม่ได้จด</p>';
    h+='</div>';});
  h+='<span style="flex:1"></span><div class="acts">'+
    '<button class="btn ghost sm" onclick="resetPw(\\''+room+'\\')">'+
    'ตั้งรหัสใหม่</button>'+
    '<button class="btn ghost sm" onclick="delRoom(\\''+room+'\\')">'+
    'ลบห้อง</button></div></div>';

  h+='<div class="card panel"><h2>รูปของเดือน '+monthTH(month)+'</h2>'+
    (ph.length?'<div class="shots">'+ph.map(shot).join('')+'</div>'
      :'<p class="none">ยังไม่มีรูปของเดือนนี้</p>')+'</div>';
  document.getElementById('detail').innerHTML=h;
}

function shot(p){
  const opts=['water','power','other'].map(k=>
    '<option value="'+k+'"'+(p.kind===k?' selected':'')+'>'+TH[k]+'</option>'
  ).join('');
  const roomOpts='<option value="">— ห้อง —</option>'+rooms.map(r=>
    '<option value="'+r.room+'"'+(p.room===r.room?' selected':'')+'>'+
    r.room+'</option>').join('');
  // เลือกห้อง เลือกชนิด พิมพ์เลข แล้วค่อยกดบันทึกทีเดียว
  // ถ้าบันทึกทันทีที่เลือกห้อง รูปจะย้ายออกจากหน้าจอไปก่อนที่จะได้พิมพ์เลข
  return '<div class="shot" data-n="'+p.name+'">'+
    '<img loading="lazy" src="/t/'+p.name+'" alt="" onclick="zoom(\\''+
      p.name+'\\')">'+
    '<div class="f"><span class="when">'+when(p.ts)+'</span>'+
    '<div class="rowf"><select data-k="room" onchange="dirty(this)">'+roomOpts+
      '</select><select data-k="kind" onchange="dirty(this)">'+opts+
      '</select></div>'+
    '<div class="rowf"><input data-k="reading" inputmode="decimal" '+
      'placeholder="เลขที่อ่านได้" value="'+(p.reading||'')+'" '+
      'oninput="dirty(this)" onkeydown="if(event.key===&quot;Enter&quot;)'+
      'save(this)">'+
      '<button class="btn sm" data-save onclick="save(this)" disabled>'+
      'บันทึก</button></div>'+
    '<span class="saved"></span>'+
    '</div></div>';
}

function dirty(el){
  const box=el.closest('.shot');
  box.querySelector('[data-save]').disabled=false;
  box.querySelector('.saved').textContent='';
}

async function save(el){
  const box=el.closest('.shot');
  const btn=box.querySelector('[data-save]');
  const tag=box.querySelector('.saved');
  const body={name:box.dataset.n};
  box.querySelectorAll('[data-k]').forEach(f=>{body[f.dataset.k]=f.value;});
  btn.disabled=true; tag.textContent='กำลังบันทึก…';
  const r=await fetch('/api/owner/set-photo',{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(r.ok){ tag.textContent='บันทึกแล้ว';
    setTimeout(()=>tag.textContent='',1800);
    loadRooms();
  }else{ tag.textContent='บันทึกไม่สำเร็จ'; btn.disabled=false; }
}

async function addRoom(e){
  e.preventDefault();
  const r=await fetch('/api/owner/add-room',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({room:document.getElementById('nroom').value.trim(),
      name:document.getElementById('nname').value.trim()})});
  const j=await r.json();
  if(j.error){document.getElementById('adderr').textContent=j.error;
    dlgAdd.showModal();return;}
  document.getElementById('nroom').value='';
  document.getElementById('nname').value='';
  document.getElementById('adderr').textContent='';
  showPw('ห้อง '+j.room,j.password);
  cur=j.room; loadRooms();
}
async function resetPw(room){
  const r=await fetch('/api/owner/reset-pw',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({room:room})});
  const j=await r.json();
  if(j.password) showPw('ห้อง '+room,j.password);
}
function showPw(title,pw){
  document.getElementById('showTitle').textContent=title;
  document.getElementById('showPw').textContent=pw;
  dlgShow.showModal();
}
async function delRoom(room){
  if(!confirm('ลบห้อง '+room+' ออกจากระบบ รูปที่ถ่ายไว้จะยังอยู่'))return;
  await fetch('/api/owner/del-room',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({room:room})});
  cur=null; loadRooms();
}
async function setOwnerPw(e){
  e.preventDefault();
  const r=await fetch('/api/owner/set-owner-pw',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({password:document.getElementById('opw').value})});
  const j=await r.json();
  if(j.error){document.getElementById('pwerr').textContent=j.error;
    dlgPw.showModal();return;}
  document.getElementById('opw').value='';
  document.getElementById('pwerr').textContent='';
}

fillMonths(); loadRooms();
</script>""" + FOOT)
