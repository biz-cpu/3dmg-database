"""
ICT施工・取付実績カタログアプリ
- 画面サイズにフィットするレイアウト（スクロール不要）
- ライトボックスは画面全体を使った全画面表示
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime
import json

st.set_page_config(
    page_title="ICT実績カタログ",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Barlow+Condensed:wght@600;800&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,.stApp{background:#0f1117!important;color:#e8eaed!important;font-family:'Noto Sans JP',sans-serif!important;}
.app-header{background:linear-gradient(135deg,#1a1f2e 0%,#141820 100%);border-bottom:2px solid #f59e0b;padding:14px 24px 12px;}
.app-header-inner{display:flex;align-items:center;gap:14px;}
.header-icon{font-size:1.8rem;line-height:1;}
.header-title{font-family:'Barlow Condensed',sans-serif;font-size:1.5rem;font-weight:800;color:#f59e0b;letter-spacing:.05em;line-height:1.1;}
.header-subtitle{font-size:.65rem;color:#6b7280;letter-spacing:.08em;text-transform:uppercase;margin-top:1px;}
.result-count{background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.25);color:#f59e0b;font-family:'Barlow Condensed',sans-serif;font-size:.85rem;font-weight:600;padding:4px 12px;border-radius:20px;display:inline-block;margin-bottom:8px;}
.stButton>button{background:linear-gradient(135deg,#f59e0b,#d97706)!important;color:#0f1117!important;font-family:'Barlow Condensed',sans-serif!important;font-size:1rem!important;font-weight:700!important;border:none!important;border-radius:10px!important;padding:10px 22px!important;width:100%!important;}
.stTextInput>div>div>input{background:#1a1f2e!important;border:1.5px solid #2a3146!important;border-radius:10px!important;color:#e8eaed!important;font-size:1rem!important;padding:10px 14px!important;height:auto!important;}
.stSelectbox>div>div{background:#1a1f2e!important;border:1.5px solid #2a3146!important;border-radius:10px!important;color:#e8eaed!important;}
.block-container{padding-top:0!important;padding-bottom:4px!important;max-width:100%!important;}
header[data-testid="stHeader"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
label[data-testid="stWidgetLabel"]{color:#9ca3af!important;font-size:.72rem!important;letter-spacing:.08em!important;text-transform:uppercase!important;}
/* iframeの余白を消す */
iframe{display:block;border:none;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────
# Notion API
# ─────────────────────────────────────────
NOTION_VERSION = "2022-06-28"

def _headers(token):
    return {"Authorization":"Bearer "+token,"Notion-Version":NOTION_VERSION,"Content-Type":"application/json"}

@st.cache_data(ttl=60, show_spinner=False)
def fetch_all_records(database_id, token):
    url = "https://api.notion.com/v1/databases/"+database_id+"/query"
    results, payload = [], {"page_size":100}
    while True:
        resp = requests.post(url, headers=_headers(token), json=payload, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError("HTTP "+str(resp.status_code)+": "+resp.text[:400])
        data = resp.json()
        results.extend(data.get("results",[]))
        if not data.get("has_more"): break
        payload["start_cursor"] = data["next_cursor"]
    return results

@st.cache_data(ttl=60, show_spinner=False)
def fetch_page_images(page_id, token):
    urls, cursor = [], None
    while True:
        url = "https://api.notion.com/v1/blocks/"+page_id+"/children?page_size=100"
        if cursor: url += "&start_cursor="+cursor
        resp = requests.get(url, headers=_headers(token), timeout=15)
        if resp.status_code != 200: break
        data = resp.json()
        for block in data.get("results",[]):
            if block.get("type") == "image":
                img = block["image"]
                it  = img.get("type","")
                if   it=="file":     urls.append(img["file"]["url"])
                elif it=="external": urls.append(img["external"]["url"])
        if not data.get("has_more"): break
        cursor = data.get("next_cursor")
    return urls

def force_refresh():
    fetch_all_records.clear(); fetch_page_images.clear(); st.rerun()

def get_title(p,k):
    try: return p[k]["title"][0]["plain_text"]
    except: return ""
def get_rich_text(p,k):
    try: return p[k]["rich_text"][0]["plain_text"]
    except: return ""
def get_select(p,k):
    try: return p[k]["select"]["name"] or ""
    except: return ""
def get_multi_select(p,k):
    try: return [o["name"] for o in p[k]["multi_select"]]
    except: return []
def get_number(p,k):
    """numberプロパティから数値を返す"""
    try:
        v=p[k]["number"]; return v if v is not None else ""
    except: return ""

def get_bucket_value(p, k):
    """
    バケットプロパティをどの型でも取得する。
    Notionでは number / rich_text / select / formula のいずれかで設定される。
    取得した値を float に変換して返す（失敗時は None）。
    """
    prop = p.get(k)
    if prop is None:
        return None
    ptype = prop.get("type", "")

    raw = None
    if ptype == "number":
        raw = prop.get("number")
    elif ptype == "rich_text":
        items = prop.get("rich_text", [])
        raw = items[0]["plain_text"] if items else None
    elif ptype == "select":
        sel = prop.get("select")
        raw = sel["name"] if sel else None
    elif ptype == "formula":
        formula = prop.get("formula", {})
        ftype = formula.get("type", "")
        if ftype == "number":
            raw = formula.get("number")
        elif ftype == "string":
            raw = formula.get("string")
    elif ptype == "text":
        items = prop.get("text", [])
        raw = items[0]["plain_text"] if items else None

    if raw is None:
        return None
    try:
        return float(str(raw).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None
def get_checkbox(p,k):
    try: return p[k]["checkbox"]
    except: return False
def get_files_prop(p,k):
    try:
        urls=[]
        for f in p[k]["files"]:
            ft=f.get("type","")
            if   ft=="file":     urls.append(f["file"]["url"])
            elif ft=="external": urls.append(f["external"]["url"])
        return urls
    except: return []

def parse_record(page):
    p   = page.get("properties",{})
    kit = get_select(p,"キット") or get_rich_text(p,"キット")
    # バケット: number/rich_text/select/formula すべてに対応
    bv = get_bucket_value(p, "バケットサイズ")   # float or None

    if bv is not None:
        try:
            # 小数点以下の末尾ゼロを除去（0.10→"0.1"、1.0→"1"）
            bucket_label = (str(int(bv)) if bv == int(bv) else
                            ("{:.10f}".format(bv)).rstrip("0").rstrip(".")) + " m³"
        except Exception:
            bucket_label = str(bv) + " m³"
    else:
        bucket_label = ""

    return {
        "id":           page["id"],
        "maker":        get_select(p,"メーカー"),
        "model":        get_title(p,"機種名"),
        "bucket":       bucket_label,
        "bucket_num":   bv,  # float or None（ソート・フィルタ用）
        "specs":        get_multi_select(p,"車体仕様"),
        "photos_prop":  get_files_prop(p,"実績写真"),
        "ict":{
            "レトロ":       get_checkbox(p,"レトロ"),
            "杭ナビショベル": get_checkbox(p,"杭ナビショベル"),
            "ブル3DMC":     get_checkbox(p,"ブル3DMC"),
            "転圧システム":  get_checkbox(p,"転圧システム"),
        },
        "note": get_rich_text(p,"備考"),
        "kit":  kit,
    }


# ─────────────────────────────────────────
# メインHTMLコンポーネント
# ─────────────────────────────────────────
def render_gallery(records_with_photos):
    photo_data = []
    cards_html = ""

    for idx, (rec, photos) in enumerate(records_with_photos):
        photo_data.append({"model": rec.get("model",""), "photos": photos})

        if photos:
            cnt = ('<span class="photo-count">📷 '+str(len(photos))+'</span>') if len(photos)>1 else ""
            img_html = (
                '<div class="card-img" onclick="lbOpen('+str(idx)+')" role="button">'
                +'<img src="'+photos[0]+'" alt="" loading="lazy">'
                +'<span class="zoom-hint">🔍 拡大</span>'+cnt+'</div>'
            )
        else:
            img_html = (
                '<div class="card-img no-click">'
                '<div class="no-img"><span class="ni-icon">📷</span>'
                '<span class="ni-text">NO IMAGE</span></div></div>'
            )

        spec_html = "".join('<span class="stag">'+s+'</span>' for s in rec.get("specs",[]))
        badge_html = ""
        for name,ok in rec["ict"].items():
            badge_html += '<span class="badge '+ ("by" if ok else "bn") +'">'+ ("✓" if ok else "—") +" "+name+"</span>"

        meta_html = ""
        if rec.get("note"):
            meta_html += '<div class="mrow"><span class="mk">備考</span><span class="mv">'+rec["note"]+'</span></div>'
        if rec.get("kit"):
            meta_html += '<div class="mrow"><span class="mk">キット</span><span class="mv">'+rec["kit"]+'</span></div>'

        cards_html += (
            '<div class="card">'
            '<div class="accent"></div>'
            + img_html +
            '<div class="cbody">'
            '<div class="maker">'+( rec.get("maker") or "—")+'</div>'
            '<div class="model">'+( rec.get("model") or "未登録")+'</div>'
            +('<div class="bucket">バケット: '+rec["bucket"]+'</div>' if rec.get("bucket") else "")
            +('<div class="stags">'+spec_html+'</div>' if spec_html else "")
            +'<div class="bsec"><div class="blabel">ICT対応</div>'
            '<div class="brow">'+badge_html+'</div></div>'
            +('<div class="meta">'+meta_html+'</div>' if meta_html else "")
            +'</div></div>'
        )

    photo_json = json.dumps(photo_data, ensure_ascii=False)

    html = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Barlow+Condensed:wght@700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{
  width:100%;height:100%;
  background:#0f1117;color:#e8eaed;
  font-family:'Noto Sans JP',sans-serif;
  overflow:hidden; /* ← スクロール禁止：グリッド内でスクロール */
}

/* ── 全体レイアウト ── */
#app{
  display:flex;flex-direction:column;
  width:100%;height:100vh;
}

/* ── グリッドエリア（残り全高さをここに割り当て） ── */
#grid-wrap{
  flex:1;
  overflow-y:auto;
  overflow-x:hidden;
  padding:12px 10px 8px;
}
#grid-wrap::-webkit-scrollbar{width:4px;}
#grid-wrap::-webkit-scrollbar-thumb{background:#2a3146;border-radius:4px;}

.grid{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:12px;
  min-height:100%;
}
@media(max-width:640px){.grid{grid-template-columns:1fr;}}
@media(min-width:641px) and (max-width:960px){.grid{grid-template-columns:repeat(2,1fr);}}

/* ── カード ── */
.card{
  background:linear-gradient(160deg,#1a1f2e 0%,#141820 100%);
  border:1px solid #1f2532;border-radius:14px;
  overflow:hidden;position:relative;
  display:flex;flex-direction:column;
  transition:transform .18s,box-shadow .18s;
}
.card:hover{transform:translateY(-2px);box-shadow:0 10px 28px rgba(0,0,0,.55),0 0 0 1px rgba(245,158,11,.22);}
.accent{position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#f59e0b,#d97706);}

/* 画像エリア：カード高さの40%固定 */
.card-img{
  position:relative;width:100%;padding-top:55%;
  background:#0d111a;overflow:hidden;cursor:pointer;flex-shrink:0;
}
.card-img.no-click{cursor:default;}
.card-img img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;transition:transform .35s;}
.card:hover .card-img img{transform:scale(1.04);}
.zoom-hint{position:absolute;top:8px;left:8px;background:rgba(0,0,0,.65);color:#d1d5db;font-size:.6rem;padding:2px 7px;border-radius:12px;opacity:0;transition:opacity .2s;pointer-events:none;}
.card-img:hover .zoom-hint{opacity:1;}
.photo-count{position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,.72);color:#d1d5db;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:12px;pointer-events:none;}
.no-img{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#374151;gap:6px;}
.ni-icon{font-size:2rem;opacity:.35;}
.ni-text{font-family:'Barlow Condensed',sans-serif;font-size:.75rem;font-weight:700;letter-spacing:.12em;opacity:.4;text-transform:uppercase;}

/* 本文 */
.cbody{padding:10px 12px 12px;flex:1;display:flex;flex-direction:column;gap:4px;overflow:hidden;}
.maker{font-size:.6rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#f59e0b;}
.model{font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;font-weight:800;color:#f3f4f6;line-height:1.15;}
.bucket{font-size:.65rem;color:#9ca3af;}
.stags{display:flex;flex-wrap:wrap;gap:3px;margin-top:2px;}
.stag{background:rgba(99,102,241,.15);color:#a5b4fc;border:1px solid rgba(99,102,241,.25);border-radius:3px;padding:1px 6px;font-size:.6rem;font-weight:600;}
.bsec{margin-top:4px;}
.blabel{font-size:.55rem;color:#4b5563;letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px;font-weight:700;}
.brow{display:flex;flex-wrap:wrap;gap:3px;}
.badge{display:inline-flex;align-items:center;gap:3px;padding:2px 7px;border-radius:5px;font-size:.6rem;font-weight:700;line-height:1;}
.by{background:rgba(16,185,129,.15);color:#10b981;border:1px solid rgba(16,185,129,.28);}
.bn{background:rgba(75,85,99,.1);color:#374151;border:1px solid rgba(75,85,99,.12);}
.meta{margin-top:4px;padding-top:6px;border-top:1px solid #1f2532;}
.mrow{display:flex;gap:4px;font-size:.62rem;}
.mk{color:#6b7280;font-weight:700;white-space:nowrap;min-width:30px;}
.mv{color:#9ca3af;line-height:1.35;}

/* ── ライトボックス ── */
#lb{
  display:none;position:fixed;inset:0;
  background:rgba(0,0,0,.97);
  z-index:9999;
  flex-direction:column;
  align-items:center;justify-content:center;
}
#lb.on{display:flex;}

#lb-close{
  position:absolute;top:14px;right:16px;
  width:42px;height:42px;border-radius:50%;
  background:rgba(255,255,255,.1);border:none;
  color:#9ca3af;font-size:1.3rem;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:background .2s,color .2s;z-index:10;
}
#lb-close:hover{background:rgba(255,255,255,.22);color:#fff;}

/* 画像エリア：viewportの80%高さを使う */
.lb-stage{
  flex:1;width:100%;
  display:flex;align-items:center;justify-content:center;
  position:relative;
  padding:56px 64px 8px;
  min-height:0;
}
#lb-img{
  max-width:100%;max-height:100%;
  object-fit:contain;
  border-radius:6px;
  box-shadow:0 20px 60px rgba(0,0,0,.8);
  transition:opacity .2s;
  display:block;
}
#lb-img.fade{opacity:0;}

.lb-arr{
  position:absolute;top:50%;transform:translateY(-50%);
  width:48px;height:48px;border-radius:50%;
  background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.13);
  color:#d1d5db;font-size:1.5rem;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:background .2s,color .2s,border-color .2s;
  user-select:none;
}
.lb-arr:hover{background:rgba(245,158,11,.28);color:#f59e0b;border-color:#f59e0b;}
.lb-arr.hide{opacity:0;pointer-events:none;}
#lb-prev{left:10px;}
#lb-next{right:10px;}

.lb-foot{
  padding:8px 20px 16px;
  display:flex;flex-direction:column;align-items:center;gap:6px;
  width:100%;flex-shrink:0;
}
.lb-model{font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:700;color:#f3f4f6;letter-spacing:.06em;}
.lb-cnt{font-size:.7rem;color:#6b7280;}
.lb-dots{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;max-width:320px;}
.dot{width:8px;height:8px;border-radius:50%;background:#374151;border:none;cursor:pointer;transition:background .2s,transform .15s;}
.dot.on{background:#f59e0b;transform:scale(1.3);}
</style>
</head>
<body>
<div id="app">
  <div id="grid-wrap">
    <div class="grid">
      %%CARDS%%
    </div>
  </div>
</div>

<!-- ライトボックス -->
<div id="lb">
  <button id="lb-close">&#x2715;</button>
  <div class="lb-stage">
    <button class="lb-arr hide" id="lb-prev">&#8249;</button>
    <img id="lb-img" src="" alt="">
    <button class="lb-arr hide" id="lb-next">&#8250;</button>
  </div>
  <div class="lb-foot">
    <div class="lb-model" id="lb-model"></div>
    <div class="lb-cnt"   id="lb-cnt"></div>
    <div class="lb-dots"  id="lb-dots"></div>
  </div>
</div>

<script>
var DATA=%%PHOTO_DATA%%;
var lb=document.getElementById('lb');
var img=document.getElementById('lb-img');
var modEl=document.getElementById('lb-model');
var cntEl=document.getElementById('lb-cnt');
var dotsEl=document.getElementById('lb-dots');
var btnP=document.getElementById('lb-prev');
var btnN=document.getElementById('lb-next');
var cur=0,photos=[],curIdx=0;

function dots(){
  dotsEl.innerHTML='';
  if(photos.length<=1)return;
  photos.forEach(function(_,i){
    var d=document.createElement('button');
    d.className='dot'+(i===cur?' on':'');
    d.onclick=function(){go(i);};
    dotsEl.appendChild(d);
  });
}
function ui(){
  modEl.textContent=DATA[curIdx]?DATA[curIdx].model:'';
  cntEl.textContent=photos.length>1?(cur+1)+' / '+photos.length:'';
  btnP.className='lb-arr'+(cur===0?' hide':'');
  btnN.className='lb-arr'+(cur===photos.length-1?' hide':'');
  dotsEl.querySelectorAll('.dot').forEach(function(d,i){d.className='dot'+(i===cur?' on':'');});
}
function go(i){
  if(i<0||i>=photos.length)return;
  img.classList.add('fade');
  setTimeout(function(){
    cur=i;img.src=photos[cur];
    img.onload=function(){img.classList.remove('fade');};
    img.onerror=function(){img.classList.remove('fade');};
    ui();
  },200);
}
function lbOpen(idx){
  var d=DATA[idx];
  if(!d||!d.photos||!d.photos.length)return;
  curIdx=idx;photos=d.photos;cur=0;
  img.src=photos[0];
  dots();ui();
  lb.classList.add('on');
  document.body.style.overflow='hidden';
}
function lbClose(){
  lb.classList.remove('on');
  document.body.style.overflow='';
  img.src='';
}
document.getElementById('lb-close').onclick=lbClose;
btnP.onclick=function(){go(cur-1);};
btnN.onclick=function(){go(cur+1);};
lb.addEventListener('click',function(e){if(e.target===lb)lbClose();});
document.addEventListener('keydown',function(e){
  if(!lb.classList.contains('on'))return;
  if(e.key==='ArrowLeft')go(cur-1);
  if(e.key==='ArrowRight')go(cur+1);
  if(e.key==='Escape')lbClose();
});
var sx=0;
lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
lb.addEventListener('touchend',function(e){
  var dx=e.changedTouches[0].clientX-sx;
  if(Math.abs(dx)<40)return;
  dx<0?go(cur+1):go(cur-1);
});
</script>
</body>
</html>"""

    html = html.replace("%%CARDS%%", cards_html)
    html = html.replace("%%PHOTO_DATA%%", photo_json)

    # height=100vh に相当する値をピクセルで渡す
    # Streamlit の components.html は height 指定が必須なので
    # JavaScript で window.innerHeight を使い自動リサイズする仕組みを追加
    components.html(html, height=900, scrolling=False)


# ─────────────────────────────────────────
# メインアプリ
# ─────────────────────────────────────────
def main():
    st.markdown(
        '<div class="app-header"><div class="app-header-inner">'
        '<div class="header-icon">🏗️</div>'
        '<div><div class="header-title">ICT施工・取付実績</div>'
        '<div class="header-subtitle">Construction ICT Catalog</div>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )

    if "NOTION_TOKEN" not in st.secrets or "NOTION_DATABASE_ID" not in st.secrets:
        st.error("⚠️ Secrets に NOTION_TOKEN と NOTION_DATABASE_ID を設定してください。")
        st.stop()

    token       = st.secrets["NOTION_TOKEN"]
    database_id = st.secrets["NOTION_DATABASE_ID"]

    with st.spinner("最新データを取得中..."):
        try:
            raw = fetch_all_records(database_id, token)
        except Exception as e:
            st.error("Notion APIエラー: " + str(e)); st.stop()

    records = [parse_record(r) for r in raw]


    # ── 検索UI: メーカー／バケットサイズ／機種名（各条件独立）──
    col_maker, col_bucket, col_search, col_btn = st.columns([2, 1.8, 2.5, 1])

    makers = sorted({r["maker"] for r in records if r.get("maker")})

    # バケットサイズ一覧: Notionの "バケットサイズ" プロパティの数値を昇順で並べる
    bucket_label_to_num = {
        r["bucket"]: r["bucket_num"]
        for r in records
        if r.get("bucket") and r.get("bucket_num") is not None
    }
    bucket_set = sorted(
        {r["bucket"] for r in records if r.get("bucket")},
        key=lambda x: bucket_label_to_num.get(x, 0.0),
    )

    with col_maker:
        selected_maker = st.selectbox("🏭 メーカー", ["すべて"] + makers)
    with col_bucket:
        selected_bucket = st.selectbox("🪣 バケットサイズ (m³)", ["すべて"] + bucket_set)
    with col_search:
        search_query = st.text_input("🔍 機種名で検索", placeholder="例: PC200, ZX135...")
    with col_btn:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        if st.button("🔄 更新"): force_refresh()

    # 3条件 AND フィルタ（各条件は単独でも組み合わせでも使用可能）
    filtered = records
    if selected_maker != "すべて":
        filtered = [r for r in filtered if r.get("maker") == selected_maker]
    if selected_bucket != "すべて":
        filtered = [r for r in filtered if r.get("bucket") == selected_bucket]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [r for r in filtered if q in r.get("model", "").lower()]


    st.markdown(
        '<div class="result-count">📋 '+str(len(filtered))+' 件の実績</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;color:#374151;">'
            '<div style="font-size:3rem;">🔍</div>'
            '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.1rem;font-weight:600;margin-top:12px;text-transform:uppercase;">該当する実績が見つかりません</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    with st.spinner("写真を読み込み中..."):
        records_with_photos = []
        for rec in filtered:
            page_imgs = fetch_page_images(rec["id"], token)
            all_photos = rec["photos_prop"] + [u for u in page_imgs if u not in rec["photos_prop"]]
            records_with_photos.append((rec, all_photos))

    render_gallery(records_with_photos)

if __name__ == "__main__":
    main()
