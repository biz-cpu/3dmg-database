"""
ICT施工・取付実績カタログアプリ
- ライトボックスをst.components.v1.htmlで実装（Streamlit iframe制約回避）
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

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: #0f1117 !important; color: #e8eaed !important; font-family: 'Noto Sans JP', sans-serif !important; }

.app-header { background: linear-gradient(135deg, #1a1f2e 0%, #141820 100%); border-bottom: 2px solid #f59e0b; padding: 20px 24px 16px; margin-bottom: 16px; }
.app-header-inner { display: flex; align-items: center; gap: 14px; }
.header-icon { font-size: 2rem; line-height: 1; }
.header-title { font-family: 'Barlow Condensed', sans-serif; font-size: 1.6rem; font-weight: 800; color: #f59e0b; letter-spacing: 0.05em; line-height: 1.1; }
.header-subtitle { font-size: 0.7rem; color: #6b7280; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px; }

.card { background: linear-gradient(160deg, #1a1f2e 0%, #141820 100%); border: 1px solid #1f2532; border-radius: 16px; overflow: hidden; margin-bottom: 20px; position: relative; transition: transform 0.2s, box-shadow 0.2s; }
.card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(245,158,11,0.25); }
.card-accent { position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #f59e0b, #d97706); }
.card-image-wrap { position: relative; width: 100%; padding-top: 62%; background: #0d111a; overflow: hidden; }
.card-image-wrap img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
.no-image { position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #374151; gap: 8px; }
.no-image-icon { font-size: 2.5rem; opacity: 0.4; }
.no-image-text { font-family: 'Barlow Condensed', sans-serif; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.12em; opacity: 0.5; text-transform: uppercase; }
.photo-count { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #d1d5db; font-size: 0.7rem; font-weight: 700; padding: 3px 8px; border-radius: 20px; pointer-events: none; }

.card-body { padding: 16px 18px 18px; }
.card-maker { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #f59e0b; margin-bottom: 4px; }
.card-model { font-family: 'Barlow Condensed', sans-serif; font-size: 1.5rem; font-weight: 800; color: #f3f4f6; line-height: 1.2; margin-bottom: 4px; }
.card-bucket { font-size: 0.72rem; color: #9ca3af; margin-bottom: 8px; }
.spec-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.spec-tag { background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.25); border-radius: 4px; padding: 2px 8px; font-size: 0.65rem; font-weight: 600; }
.badge-section { margin-top: 10px; }
.badge-label { font-size: 0.6rem; color: #4b5563; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; font-weight: 700; }
.badge-row { display: flex; flex-wrap: wrap; gap: 5px; }
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; font-size: 0.68rem; font-weight: 700; line-height: 1; }
.badge-yes { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.badge-no  { background: rgba(75,85,99,0.12); color: #374151; border: 1px solid rgba(75,85,99,0.15); }
.card-meta { margin-top: 10px; padding-top: 10px; border-top: 1px solid #1f2532; display: flex; flex-direction: column; gap: 4px; }
.meta-row { display: flex; gap: 6px; align-items: flex-start; font-size: 0.7rem; }
.meta-key { color: #6b7280; font-weight: 700; white-space: nowrap; min-width: 36px; }
.meta-val { color: #9ca3af; line-height: 1.4; }

.result-count { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #f59e0b; font-family: 'Barlow Condensed', sans-serif; font-size: 0.85rem; font-weight: 600; padding: 5px 12px; border-radius: 20px; display: inline-block; margin-bottom: 16px; }
.last-updated { font-size: 0.65rem; color: #374151; text-align: center; padding: 8px; letter-spacing: 0.06em; }
.empty-state { text-align: center; padding: 60px 20px; color: #374151; }
.empty-state-icon { font-size: 3rem; }
.empty-state-msg { font-family: 'Barlow Condensed', sans-serif; font-size: 1.1rem; font-weight: 600; margin-top: 12px; text-transform: uppercase; }

.stButton > button { background: linear-gradient(135deg, #f59e0b, #d97706) !important; color: #0f1117 !important; font-family: 'Barlow Condensed', sans-serif !important; font-size: 1rem !important; font-weight: 700 !important; border: none !important; border-radius: 10px !important; padding: 10px 22px !important; width: 100% !important; }
.stTextInput > div > div > input { background: #1a1f2e !important; border: 1.5px solid #2a3146 !important; border-radius: 10px !important; color: #e8eaed !important; font-size: 1rem !important; padding: 12px 16px !important; height: auto !important; }
.stSelectbox > div > div { background: #1a1f2e !important; border: 1.5px solid #2a3146 !important; border-radius: 10px !important; color: #e8eaed !important; }
.block-container { padding-top: 0 !important; padding-bottom: 20px !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
label[data-testid="stWidgetLabel"] { color: #9ca3af !important; font-size: 0.75rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────
# Notion API
# ─────────────────────────────────────────
NOTION_VERSION = "2022-06-28"

def _headers(token):
    return {
        "Authorization": "Bearer " + token,
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

@st.cache_data(ttl=60, show_spinner=False)
def fetch_all_records(database_id, token):
    url     = "https://api.notion.com/v1/databases/" + database_id + "/query"
    headers = _headers(token)
    results = []
    payload = {"page_size": 100}
    while True:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError("HTTP " + str(resp.status_code) + ": " + resp.text[:400])
        data = resp.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"): break
        payload["start_cursor"] = data["next_cursor"]
    return results

@st.cache_data(ttl=60, show_spinner=False)
def fetch_page_images(page_id, token):
    headers = _headers(token)
    urls    = []
    cursor  = None
    while True:
        url = "https://api.notion.com/v1/blocks/" + page_id + "/children?page_size=100"
        if cursor: url += "&start_cursor=" + cursor
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200: break
        data = resp.json()
        for block in data.get("results", []):
            if block.get("type") == "image":
                img = block["image"]
                it  = img.get("type", "")
                if   it == "file":     urls.append(img["file"]["url"])
                elif it == "external": urls.append(img["external"]["url"])
        if not data.get("has_more"): break
        cursor = data.get("next_cursor")
    return urls

def force_refresh():
    fetch_all_records.clear()
    fetch_page_images.clear()
    st.rerun()


# ─────────────────────────────────────────
# プロパティ取得ヘルパー
# ─────────────────────────────────────────
def get_title(p, k):
    try: return p[k]["title"][0]["plain_text"]
    except (KeyError, IndexError): return ""

def get_rich_text(p, k):
    try: return p[k]["rich_text"][0]["plain_text"]
    except (KeyError, IndexError): return ""

def get_select(p, k):
    try: return p[k]["select"]["name"] or ""
    except (KeyError, TypeError): return ""

def get_multi_select(p, k):
    try: return [o["name"] for o in p[k]["multi_select"]]
    except (KeyError, TypeError): return []

def get_number(p, k):
    try:
        v = p[k]["number"]
        return v if v is not None else ""
    except KeyError: return ""

def get_checkbox(p, k):
    try: return p[k]["checkbox"]
    except KeyError: return False

def get_files_prop(p, k):
    try:
        urls = []
        for f in p[k]["files"]:
            ft = f.get("type", "")
            if   ft == "file":     urls.append(f["file"]["url"])
            elif ft == "external": urls.append(f["external"]["url"])
        return urls
    except (KeyError, TypeError): return []

def parse_record(page):
    p   = page.get("properties", {})
    kit = get_select(p, "キット") or get_rich_text(p, "キット")
    bv  = get_number(p, "バケット")
    return {
        "id":          page["id"],
        "maker":       get_select(p, "メーカー"),
        "model":       get_title(p, "機種名"),
        "bucket":      (str(bv) + " m3") if bv != "" else "",
        "specs":       get_multi_select(p, "車体仕様"),
        "photos_prop": get_files_prop(p, "実績写真"),
        "ict": {
            "レトロ":        get_checkbox(p, "レトロ"),
            "杭ナビショベル":  get_checkbox(p, "杭ナビショベル"),
            "ブル3DMC":      get_checkbox(p, "ブル3DMC"),
            "転圧システム":   get_checkbox(p, "転圧システム"),
        },
        "note": get_rich_text(p, "備考"),
        "kit":  kit,
    }


# ─────────────────────────────────────────
# ライトボックス付きグリッドを
# st.components.v1.html で丸ごとレンダリング
# （Streamlit の iframe 制約を回避）
# ─────────────────────────────────────────
def render_gallery_component(records_with_photos):
    """
    records_with_photos: list of (rec_dict, photos_list)
    全カードとライトボックスを1つのHTMLコンポーネントとして出力。
    """

    # カードHTML断片を構築
    cards_html = ""
    all_photo_data = []   # [{model, photos}, ...]

    for idx, (rec, photos) in enumerate(records_with_photos):
        all_photo_data.append({
            "model":  rec.get("model", ""),
            "photos": photos,
        })

        # 写真エリア
        if photos:
            cnt = ('<span class="photo-count">📷 ' + str(len(photos)) + '</span>') if len(photos) > 1 else ""
            image_html = (
                '<div class="card-image-wrap" onclick="lbOpen(' + str(idx) + ')" title="クリックで拡大">'
                + '<img src="' + photos[0] + '" alt="" loading="lazy">'
                + '<span class="zoom-hint">🔍 拡大</span>'
                + cnt
                + '</div>'
            )
        else:
            image_html = (
                '<div class="card-image-wrap no-click">'
                '<div class="no-image">'
                '<div class="no-image-icon">📷</div>'
                '<div class="no-image-text">NO IMAGE</div>'
                '</div></div>'
            )

        spec_inner = "".join('<span class="spec-tag">' + s + '</span>' for s in rec.get("specs", []))
        spec_html  = ('<div class="spec-tags">' + spec_inner + '</div>') if spec_inner else ""

        badge_inner = ""
        for name, ok in rec["ict"].items():
            cls  = "badge badge-yes" if ok else "badge badge-no"
            mark = "✓" if ok else "—"
            badge_inner += '<span class="' + cls + '">' + mark + " " + name + "</span>"

        meta_inner = ""
        if rec.get("note"):
            meta_inner += '<div class="meta-row"><span class="meta-key">備考</span><span class="meta-val">' + rec["note"] + "</span></div>"
        if rec.get("kit"):
            meta_inner += '<div class="meta-row"><span class="meta-key">キット</span><span class="meta-val">' + rec["kit"] + "</span></div>"

        bucket_html = ('<div class="card-bucket">バケット容量: ' + rec["bucket"] + "</div>") if rec.get("bucket") else ""
        meta_html   = ('<div class="card-meta">' + meta_inner + "</div>") if meta_inner else ""

        cards_html += (
            '<div class="card">'
            '<div class="card-accent"></div>'
            + image_html +
            '<div class="card-body">'
            '<div class="card-maker">' + (rec.get("maker") or "—") + "</div>"
            '<div class="card-model">' + (rec.get("model") or "（機種名未登録）") + "</div>"
            + bucket_html + spec_html +
            '<div class="badge-section">'
            '<div class="badge-label">ICT対応システム</div>'
            '<div class="badge-row">' + badge_inner + "</div>"
            "</div>"
            + meta_html +
            "</div></div>"
        )

    # Python側でJSONを生成してHTMLに埋め込む
    photo_data_json = json.dumps(all_photo_data, ensure_ascii=False)

    # 行数に応じた高さ（カード1行 ≒ 520px、3列グリッド）
    n_rows = max(1, -(-len(records_with_photos) // 3))
    height = n_rows * 560 + 80

    html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Barlow+Condensed:wght@600;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:#0f1117;color:#e8eaed;font-family:'Noto Sans JP',sans-serif;padding:4px 0 12px;}

.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
@media(max-width:700px){.grid{grid-template-columns:1fr;}}
@media(min-width:701px) and (max-width:1000px){.grid{grid-template-columns:repeat(2,1fr);}}

.card{background:linear-gradient(160deg,#1a1f2e 0%,#141820 100%);border:1px solid #1f2532;border-radius:16px;overflow:hidden;position:relative;transition:transform .2s,box-shadow .2s;}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 32px rgba(0,0,0,.5),0 0 0 1px rgba(245,158,11,.25);}
.card-accent{position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#f59e0b,#d97706);}

.card-image-wrap{position:relative;width:100%;padding-top:62%;background:#0d111a;overflow:hidden;cursor:pointer;}
.card-image-wrap.no-click{cursor:default;}
.card-image-wrap img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;transition:transform .4s;}
.card:hover .card-image-wrap img{transform:scale(1.04);}
.no-image{position:absolute;top:0;left:0;right:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#374151;gap:8px;}
.no-image-icon{font-size:2.5rem;opacity:.4;}
.no-image-text{font-family:'Barlow Condensed',sans-serif;font-size:.85rem;font-weight:600;letter-spacing:.12em;opacity:.5;text-transform:uppercase;}
.zoom-hint{position:absolute;top:10px;left:10px;background:rgba(0,0,0,.65);color:#d1d5db;font-size:.65rem;padding:3px 8px;border-radius:20px;opacity:0;transition:opacity .25s;pointer-events:none;}
.card-image-wrap:hover .zoom-hint{opacity:1;}
.photo-count{position:absolute;bottom:10px;right:10px;background:rgba(0,0,0,.7);color:#d1d5db;font-size:.7rem;font-weight:700;padding:3px 8px;border-radius:20px;pointer-events:none;}

.card-body{padding:14px 16px 16px;}
.card-maker{font-size:.65rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#f59e0b;margin-bottom:4px;}
.card-model{font-family:'Barlow Condensed',sans-serif;font-size:1.45rem;font-weight:800;color:#f3f4f6;line-height:1.2;margin-bottom:4px;}
.card-bucket{font-size:.72rem;color:#9ca3af;margin-bottom:8px;}
.spec-tags{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;}
.spec-tag{background:rgba(99,102,241,.15);color:#a5b4fc;border:1px solid rgba(99,102,241,.25);border-radius:4px;padding:2px 8px;font-size:.65rem;font-weight:600;}
.badge-section{margin-top:8px;}
.badge-label{font-size:.6rem;color:#4b5563;letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px;font-weight:700;}
.badge-row{display:flex;flex-wrap:wrap;gap:4px;}
.badge{display:inline-flex;align-items:center;gap:3px;padding:3px 9px;border-radius:6px;font-size:.67rem;font-weight:700;line-height:1;}
.badge-yes{background:rgba(16,185,129,.15);color:#10b981;border:1px solid rgba(16,185,129,.3);}
.badge-no{background:rgba(75,85,99,.12);color:#374151;border:1px solid rgba(75,85,99,.15);}
.card-meta{margin-top:10px;padding-top:10px;border-top:1px solid #1f2532;display:flex;flex-direction:column;gap:4px;}
.meta-row{display:flex;gap:6px;align-items:flex-start;font-size:.7rem;}
.meta-key{color:#6b7280;font-weight:700;white-space:nowrap;min-width:36px;}
.meta-val{color:#9ca3af;line-height:1.4;}

/* ── ライトボックス ── */
#lb{display:none;position:fixed;inset:0;background:rgba(0,0,0,.97);z-index:9999;flex-direction:column;align-items:center;justify-content:center;}
#lb.on{display:flex;}

#lb-close{position:absolute;top:16px;right:18px;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.1);border:none;color:#9ca3af;font-size:1.4rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .2s,color .2s;z-index:10;}
#lb-close:hover{background:rgba(255,255,255,.22);color:#fff;}

.lb-stage{flex:1;width:100%;display:flex;align-items:center;justify-content:center;position:relative;padding:60px 70px 10px;min-height:0;}
.lb-stage img{max-width:100%;max-height:100%;object-fit:contain;border-radius:8px;box-shadow:0 20px 60px rgba(0,0,0,.8);transition:opacity .22s ease;user-select:none;display:block;}
.lb-stage img.fade{opacity:0;}

.lb-arrow{position:absolute;top:50%;transform:translateY(-50%);width:50px;height:50px;border-radius:50%;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.14);color:#d1d5db;font-size:1.5rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .2s,color .2s,border-color .2s;user-select:none;}
.lb-arrow:hover{background:rgba(245,158,11,.3);color:#f59e0b;border-color:#f59e0b;}
.lb-arrow.hide{opacity:0;pointer-events:none;}
#lb-prev{left:12px;}
#lb-next{right:12px;}

.lb-foot{padding:10px 20px 20px;display:flex;flex-direction:column;align-items:center;gap:8px;width:100%;}
.lb-title{font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;color:#f3f4f6;letter-spacing:.06em;}
.lb-counter{font-size:.75rem;color:#6b7280;letter-spacing:.08em;}
.lb-dots{display:flex;gap:7px;flex-wrap:wrap;justify-content:center;max-width:340px;}
.lb-dot{width:9px;height:9px;border-radius:50%;background:#374151;border:none;cursor:pointer;transition:background .2s,transform .15s;}
.lb-dot.on{background:#f59e0b;transform:scale(1.35);}
</style>
</head>
<body>

<div class="grid">
CARDS_PLACEHOLDER
</div>

<!-- ライトボックス -->
<div id="lb">
  <button id="lb-close" aria-label="閉じる">&#x2715;</button>
  <div class="lb-stage">
    <button class="lb-arrow hide" id="lb-prev" aria-label="前へ">&#8249;</button>
    <img id="lb-img" src="" alt="">
    <button class="lb-arrow hide" id="lb-next" aria-label="次へ">&#8250;</button>
  </div>
  <div class="lb-foot">
    <div class="lb-title" id="lb-title"></div>
    <div class="lb-counter" id="lb-counter"></div>
    <div class="lb-dots" id="lb-dots"></div>
  </div>
</div>

<script>
var DATA = PHOTO_DATA_PLACEHOLDER;

var lb      = document.getElementById('lb');
var lbImg   = document.getElementById('lb-img');
var lbTitle = document.getElementById('lb-title');
var lbCnt   = document.getElementById('lb-counter');
var lbDots  = document.getElementById('lb-dots');
var btnPrev = document.getElementById('lb-prev');
var btnNext = document.getElementById('lb-next');

var cur = 0;
var photos = [];

function buildDots(){
  lbDots.innerHTML = '';
  if(photos.length <= 1) return;
  photos.forEach(function(_, i){
    var d = document.createElement('button');
    d.className = 'lb-dot' + (i===cur?' on':'');
    d.onclick = function(){ goTo(i); };
    lbDots.appendChild(d);
  });
}

function updateUI(){
  lbTitle.textContent = DATA[window._lbIdx] ? DATA[window._lbIdx].model : '';
  lbCnt.textContent   = photos.length > 1 ? (cur+1) + ' / ' + photos.length : '';
  btnPrev.className   = 'lb-arrow' + (cur===0 ? ' hide' : '');
  btnNext.className   = 'lb-arrow' + (cur===photos.length-1 ? ' hide' : '');
  lbDots.querySelectorAll('.lb-dot').forEach(function(d,i){
    d.className = 'lb-dot' + (i===cur?' on':'');
  });
}

function goTo(idx){
  if(idx < 0 || idx >= photos.length) return;
  lbImg.classList.add('fade');
  setTimeout(function(){
    cur = idx;
    lbImg.src = photos[cur];
    lbImg.onload = function(){ lbImg.classList.remove('fade'); };
    lbImg.onerror = function(){ lbImg.classList.remove('fade'); };
    updateUI();
  }, 200);
}

function lbOpen(idx){
  var d = DATA[idx];
  if(!d || !d.photos || d.photos.length === 0) return;
  window._lbIdx = idx;
  photos = d.photos;
  cur = 0;
  lbImg.src = photos[0];
  buildDots();
  updateUI();
  lb.classList.add('on');
  document.body.style.overflow = 'hidden';
}

function lbClose(){
  lb.classList.remove('on');
  document.body.style.overflow = '';
  lbImg.src = '';
}

document.getElementById('lb-close').onclick = lbClose;
btnPrev.onclick = function(){ goTo(cur-1); };
btnNext.onclick = function(){ goTo(cur+1); };
lb.addEventListener('click', function(e){ if(e.target===lb) lbClose(); });

document.addEventListener('keydown', function(e){
  if(!lb.classList.contains('on')) return;
  if(e.key==='ArrowLeft')  goTo(cur-1);
  if(e.key==='ArrowRight') goTo(cur+1);
  if(e.key==='Escape')     lbClose();
});

var sx=0;
lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
lb.addEventListener('touchend',function(e){
  var dx=e.changedTouches[0].clientX-sx;
  if(Math.abs(dx)<40) return;
  dx<0?goTo(cur+1):goTo(cur-1);
});
</script>
</body>
</html>
"""

    html = html.replace("CARDS_PLACEHOLDER", cards_html)
    html = html.replace("PHOTO_DATA_PLACEHOLDER", photo_data_json)

    components.html(html, height=height, scrolling=True)


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
            st.error("Notion APIエラー: " + str(e))
            st.stop()

    records = [parse_record(r) for r in raw]

    col_maker, col_search, col_btn = st.columns([2, 3, 1.2])
    makers = sorted({r["maker"] for r in records if r.get("maker")})

    with col_maker:
        selected_maker = st.selectbox("メーカー", ["すべて"] + makers)
    with col_search:
        search_query = st.text_input("機種名で検索", placeholder="例: PC200, ZX135...")
    with col_btn:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        if st.button("🔄 更新"):
            force_refresh()

    filtered = records
    if selected_maker != "すべて":
        filtered = [r for r in filtered if r.get("maker") == selected_maker]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [r for r in filtered if q in r.get("model", "").lower()]

    st.markdown(
        '<div class="result-count">📋 ' + str(len(filtered)) + ' 件の実績</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">🔍</div>'
            '<div class="empty-state-msg">該当する実績が見つかりません</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    # 写真を統合
    records_with_photos = []
    with st.spinner("写真を読み込み中..."):
        for rec in filtered:
            page_imgs  = fetch_page_images(rec["id"], token)
            all_photos = rec["photos_prop"] + [u for u in page_imgs if u not in rec["photos_prop"]]
            records_with_photos.append((rec, all_photos))

    # ライトボックス付きグリッドを1コンポーネントで描画
    render_gallery_component(records_with_photos)

    st.markdown(
        '<div class="last-updated">最終更新: '
        + datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        + '　|　データは最大60秒ごとに自動更新</div>',
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
