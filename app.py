"""
ICT施工・取付実績カタログアプリ
- HTMLテキスト化バグ修正（CSSの{}とf-stringの衝突を回避）
- ページ本文（子ブロック）の画像も取得対応
"""

import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="ICT実績カタログ",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSSはf-stringを使わず単独で出力（{}の衝突を完全回避）
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
.card-image-wrap img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s; }
.card:hover .card-image-wrap img { transform: scale(1.03); }
.no-image { position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #374151; gap: 8px; }
.no-image-icon { font-size: 2.5rem; opacity: 0.4; }
.no-image-text { font-family: 'Barlow Condensed', sans-serif; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.12em; opacity: 0.5; text-transform: uppercase; }
.photo-count { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); color: #d1d5db; font-size: 0.7rem; font-weight: 700; padding: 3px 8px; border-radius: 20px; }

.card-body { padding: 16px 18px 18px; }
.card-maker { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #f59e0b; margin-bottom: 4px; }
.card-model { font-family: 'Barlow Condensed', sans-serif; font-size: 1.5rem; font-weight: 800; color: #f3f4f6; line-height: 1.2; margin-bottom: 4px; }
.card-bucket { font-size: 0.72rem; color: #9ca3af; margin-bottom: 8px; }

.spec-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.spec-tag { background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.25); border-radius: 4px; padding: 2px 8px; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.04em; }

.badge-section { margin-top: 10px; }
.badge-label { font-size: 0.6rem; color: #4b5563; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; font-weight: 700; }
.badge-row { display: flex; flex-wrap: wrap; gap: 5px; }
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.03em; line-height: 1; }
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
.empty-state-msg { font-family: 'Barlow Condensed', sans-serif; font-size: 1.1rem; font-weight: 600; margin-top: 12px; letter-spacing: 0.06em; text-transform: uppercase; }

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
# Notion API（requests で直接呼ぶ）
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
    """ページネーション対応で全レコード取得。"""
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
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


@st.cache_data(ttl=60, show_spinner=False)
def fetch_page_images(page_id, token):
    """
    ページの子ブロックを再帰的に取得し、
    image ブロックのURLをすべて返す。
    Notionのサイドピークに貼った写真はここに入る。
    """
    headers = _headers(token)
    urls = []
    cursor = None

    while True:
        url = "https://api.notion.com/v1/blocks/" + page_id + "/children?page_size=100"
        if cursor:
            url += "&start_cursor=" + cursor
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            break
        data = resp.json()
        for block in data.get("results", []):
            btype = block.get("type", "")
            if btype == "image":
                img = block["image"]
                itype = img.get("type", "")
                if itype == "file":
                    urls.append(img["file"]["url"])
                elif itype == "external":
                    urls.append(img["external"]["url"])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    return urls


def force_refresh():
    fetch_all_records.clear()
    fetch_page_images.clear()
    st.rerun()


# ─────────────────────────────────────────
# プロパティ取得ヘルパー
# ─────────────────────────────────────────
def get_title(props, key):
    try: return props[key]["title"][0]["plain_text"]
    except (KeyError, IndexError): return ""

def get_rich_text(props, key):
    try: return props[key]["rich_text"][0]["plain_text"]
    except (KeyError, IndexError): return ""

def get_select(props, key):
    try: return props[key]["select"]["name"] or ""
    except (KeyError, TypeError): return ""

def get_multi_select(props, key):
    try: return [o["name"] for o in props[key]["multi_select"]]
    except (KeyError, TypeError): return []

def get_number(props, key):
    try:
        v = props[key]["number"]
        return v if v is not None else ""
    except KeyError: return ""

def get_checkbox(props, key):
    try: return props[key]["checkbox"]
    except KeyError: return False

def get_files_prop(props, key):
    """filesプロパティ（ファイル&メディア列）からURL取得"""
    try:
        urls = []
        for f in props[key]["files"]:
            ft = f.get("type", "")
            if   ft == "file":     urls.append(f["file"]["url"])
            elif ft == "external": urls.append(f["external"]["url"])
        return urls
    except (KeyError, TypeError):
        return []


# ─────────────────────────────────────────
# レコードをパース
# ─────────────────────────────────────────
def parse_record(page):
    p = page.get("properties", {})
    kit = get_select(p, "キット") or get_rich_text(p, "キット")
    bucket_raw = get_number(p, "バケット")
    bucket = (str(bucket_raw) + " m3") if bucket_raw != "" else ""

    return {
        "id":     page["id"],
        "maker":  get_select(p, "メーカー"),
        "model":  get_title(p, "機種名"),
        "bucket": bucket,
        "specs":  get_multi_select(p, "車体仕様"),
        "photos_prop": get_files_prop(p, "実績写真"),  # filesプロパティ
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
# カードHTML生成（f-string不使用・文字列結合で構築）
# ─────────────────────────────────────────
def render_card_html(rec, photos):
    """
    photos: filesプロパティ + ページ本文imageブロック を結合したリスト
    HTMLはf-stringを一切使わず + 演算子で構築（CSSの{}との衝突を回避）
    """
    # 写真エリア
    if photos:
        cnt_html = ('<div class="photo-count">📷 ' + str(len(photos)) + '</div>') if len(photos) > 1 else ""
        image_html = (
            '<div class="card-image-wrap">'
            + '<img src="' + photos[0] + '" alt="' + rec["model"] + '" loading="lazy">'
            + cnt_html
            + '</div>'
        )
    else:
        image_html = (
            '<div class="card-image-wrap">'
            '<div class="no-image">'
            '<div class="no-image-icon">📷</div>'
            '<div class="no-image-text">NO IMAGE</div>'
            '</div></div>'
        )

    # 車体仕様タグ
    spec_inner = "".join('<span class="spec-tag">' + s + '</span>' for s in rec.get("specs", []))
    spec_html  = ('<div class="spec-tags">' + spec_inner + '</div>') if spec_inner else ""

    # ICTバッジ
    badge_inner = ""
    for name, ok in rec["ict"].items():
        cls  = "badge badge-yes" if ok else "badge badge-no"
        mark = "✓" if ok else "—"
        badge_inner += '<span class="' + cls + '">' + mark + " " + name + '</span>'
    badge_html = (
        '<div class="badge-section">'
        '<div class="badge-label">ICT対応システム</div>'
        '<div class="badge-row">' + badge_inner + '</div>'
        '</div>'
    )

    # 備考・キット
    meta_inner = ""
    if rec.get("note"):
        meta_inner += '<div class="meta-row"><span class="meta-key">備考</span><span class="meta-val">' + rec["note"] + '</span></div>'
    if rec.get("kit"):
        meta_inner += '<div class="meta-row"><span class="meta-key">キット</span><span class="meta-val">' + rec["kit"] + '</span></div>'
    meta_html = ('<div class="card-meta">' + meta_inner + '</div>') if meta_inner else ""

    bucket_html = ('<div class="card-bucket">バケット容量: ' + rec["bucket"] + '</div>') if rec.get("bucket") else ""

    return (
        '<div class="card">'
        '<div class="card-accent"></div>'
        + image_html +
        '<div class="card-body">'
        '<div class="card-maker">' + (rec.get("maker") or "—") + '</div>'
        '<div class="card-model">' + (rec.get("model") or "（機種名未登録）") + '</div>'
        + bucket_html
        + spec_html
        + badge_html
        + meta_html +
        '</div>'
        '</div>'
    )


# ─────────────────────────────────────────
# メインアプリ
# ─────────────────────────────────────────
def main():
    st.markdown(
        '<div class="app-header">'
        '<div class="app-header-inner">'
        '<div class="header-icon">🏗️</div>'
        '<div>'
        '<div class="header-title">ICT施工・取付実績</div>'
        '<div class="header-subtitle">Construction ICT Catalog</div>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )

    if "NOTION_TOKEN" not in st.secrets or "NOTION_DATABASE_ID" not in st.secrets:
        st.error(
            "⚠️ Streamlit Cloud の Secrets に以下を設定してください:\n\n"
            "```toml\n"
            "NOTION_TOKEN = 'secret_xxxxxx'\n"
            "NOTION_DATABASE_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'\n"
            "```"
        )
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

    # 検索UI
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

    # フィルタ
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

    # カード描画（3列）
    for row in [filtered[i:i+3] for i in range(0, len(filtered), 3)]:
        cols = st.columns(3, gap="medium")
        for col, rec in zip(cols, row):
            with col:
                # filesプロパティ + ページ本文の画像ブロック を統合
                page_imgs = fetch_page_images(rec["id"], token)
                all_photos = rec["photos_prop"] + [u for u in page_imgs if u not in rec["photos_prop"]]
                st.markdown(render_card_html(rec, all_photos), unsafe_allow_html=True)

    st.markdown(
        '<div class="last-updated">最終更新: '
        + datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        + '　|　データは最大60秒ごとに自動更新</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
