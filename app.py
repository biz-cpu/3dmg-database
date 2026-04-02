"""
ICT施工・取付実績カタログアプリ
Notion APIをDBとして使用するStreamlitアプリ
notion-client ライブラリを使わず requests で直接APIを叩く設計。
Notion-Version: 2022-06-28 を固定することでAPIの破壊的変更を回避。
"""

import streamlit as st
import requests
from datetime import datetime

# ─────────────────────────────────────────
# ページ設定
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ICT実績カタログ",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# カスタムCSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Barlow+Condensed:wght@600;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: #0f1117 !important; color: #e8eaed !important; font-family: 'Noto Sans JP', sans-serif !important; }

.app-header { background: linear-gradient(135deg, #1a1f2e 0%, #141820 100%); border-bottom: 2px solid #f59e0b; padding: 20px 24px 16px; }
.app-header-inner { display: flex; align-items: center; gap: 14px; }
.header-icon { font-size: 2rem; line-height: 1; }
.header-title { font-family: 'Barlow Condensed', sans-serif; font-size: 1.6rem; font-weight: 800; color: #f59e0b; letter-spacing: 0.05em; line-height: 1.1; }
.header-subtitle { font-size: 0.7rem; color: #6b7280; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px; }

.card { background: linear-gradient(160deg, #1a1f2e 0%, #141820 100%); border: 1px solid #1f2532; border-radius: 16px; overflow: hidden; margin-bottom: 20px; position: relative; transition: transform 0.2s, box-shadow 0.2s; }
.card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(245,158,11,0.25); }
.card-accent { position: absolute; top:0; left:0; right:0; height:3px; background: linear-gradient(90deg,#f59e0b,#d97706); }
.card-image-wrap { position:relative; width:100%; padding-top:62%; background:#0d111a; overflow:hidden; }
.card-image-wrap img { position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; transition:transform 0.4s; }
.card:hover .card-image-wrap img { transform: scale(1.03); }
.no-image { position:absolute; top:0; left:0; right:0; bottom:0; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#374151; gap:8px; }
.no-image-icon { font-size:2.5rem; opacity:0.4; }
.no-image-text { font-family:'Barlow Condensed',sans-serif; font-size:0.85rem; font-weight:600; letter-spacing:0.12em; opacity:0.5; text-transform:uppercase; }
.card-body { padding: 16px 18px 18px; }
.card-maker { font-size:0.65rem; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:#f59e0b; margin-bottom:4px; }
.card-model { font-family:'Barlow Condensed',sans-serif; font-size:1.4rem; font-weight:800; color:#f3f4f6; line-height:1.2; margin-bottom:6px; }
.card-spec { font-size:0.75rem; color:#6b7280; margin-bottom:14px; line-height:1.5; }
.badge-row { display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; }
.badge { display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border-radius:6px; font-size:0.7rem; font-weight:700; letter-spacing:0.04em; line-height:1; }
.badge-yes { background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); }
.badge-no { background:rgba(75,85,99,0.2); color:#4b5563; border:1px solid rgba(75,85,99,0.2); }
.photo-count { position:absolute; bottom:10px; right:10px; background:rgba(0,0,0,0.7); backdrop-filter:blur(4px); color:#d1d5db; font-size:0.7rem; font-weight:700; padding:3px 8px; border-radius:20px; }
.result-count { background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.25); color:#f59e0b; font-family:'Barlow Condensed',sans-serif; font-size:0.85rem; font-weight:600; padding:5px 12px; border-radius:20px; display:inline-block; margin-bottom:16px; }
.last-updated { font-size:0.65rem; color:#374151; text-align:center; padding:8px; letter-spacing:0.06em; }
.empty-state { text-align:center; padding:60px 20px; color:#374151; }
.empty-state-icon { font-size:3rem; }
.empty-state-msg { font-family:'Barlow Condensed',sans-serif; font-size:1.1rem; font-weight:600; margin-top:12px; letter-spacing:0.06em; text-transform:uppercase; }
.stButton > button { background:linear-gradient(135deg,#f59e0b,#d97706) !important; color:#0f1117 !important; font-family:'Barlow Condensed',sans-serif !important; font-size:1rem !important; font-weight:700 !important; border:none !important; border-radius:10px !important; padding:10px 22px !important; width:100% !important; }
.stTextInput > div > div > input { background:#1a1f2e !important; border:1.5px solid #2a3146 !important; border-radius:10px !important; color:#e8eaed !important; font-size:1rem !important; padding:12px 16px !important; height:auto !important; }
.stSelectbox > div > div { background:#1a1f2e !important; border:1.5px solid #2a3146 !important; border-radius:10px !important; color:#e8eaed !important; }
.block-container { padding-top:0 !important; padding-bottom:20px !important; max-width:100% !important; }
header[data-testid="stHeader"] { display:none !important; }
section[data-testid="stSidebar"] { display:none !important; }
label[data-testid="stWidgetLabel"] { color:#9ca3af !important; font-size:0.75rem !important; letter-spacing:0.08em !important; text-transform:uppercase !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Notion API（requests で直接呼ぶ）
# notion-client ライブラリを一切使わないため
# バージョン問題を根本から回避する。
# ─────────────────────────────────────────
NOTION_VERSION = "2022-06-28"


def _notion_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


@st.cache_data(ttl=60, show_spinner=False)
def fetch_all_records(database_id: str, token: str) -> list:
    """
    Notion REST API を requests で直接叩き全レコードを取得。
    ページネーション対応。S3 URL失効対策として ttl=60秒でキャッシュ。
    """
    url     = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = _notion_headers(token)
    results = []
    payload = {"page_size": 100}

    while True:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:400]}")
        data = resp.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return results


def force_refresh():
    fetch_all_records.clear()
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

def get_checkbox(props, key):
    try: return props[key]["checkbox"]
    except KeyError: return False

def get_files(props, key):
    """S3一時URLは毎回取得で失効を回避"""
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
def parse_record(page: dict) -> dict:
    """
    【Notionプロパティ名の対応表】
    実際のプロパティ名に合わせて変更してください。
    ────────────────────────────────────────
    "機種名"          → タイトル     (title)
    "メーカー"        → セレクト     (select)
    "車体仕様"        → テキスト     (rich_text)
    "実績写真"        → ファイル     (files)
    "杭ナビ"         → チェックボックス
    "ICT建機"        → チェックボックス
    "マシンガイダンス" → チェックボックス
    "自動追尾TS"     → チェックボックス
    "ICTドローン"    → チェックボックス
    ────────────────────────────────────────
    """
    p = page.get("properties", {})
    return {
        "id":     page["id"],
        "model":  get_title(p, "機種名"),
        "maker":  get_select(p, "メーカー"),
        "spec":   get_rich_text(p, "車体仕様"),
        "photos": get_files(p, "実績写真"),
        "ict_systems": {
            "杭ナビ":         get_checkbox(p, "杭ナビ"),
            "ICT建機":        get_checkbox(p, "ICT建機"),
            "MG":             get_checkbox(p, "マシンガイダンス"),
            "自動追尾TS":     get_checkbox(p, "自動追尾TS"),
            "ICTドローン":    get_checkbox(p, "ICTドローン"),
        },
    }


# ─────────────────────────────────────────
# カードHTML生成
# ─────────────────────────────────────────
def render_card_html(rec: dict) -> str:
    photos = rec.get("photos", [])
    if photos:
        cnt = f'<div class="photo-count">📷 {len(photos)}</div>' if len(photos) > 1 else ""
        image_html = f'<div class="card-image-wrap"><img src="{photos[0]}" alt="{rec["model"]}" loading="lazy">{cnt}</div>'
    else:
        image_html = '<div class="card-image-wrap"><div class="no-image"><div class="no-image-icon">📷</div><div class="no-image-text">NO IMAGE</div></div></div>'

    badges = "".join(
        f'<span class="badge {"badge-yes" if ok else "badge-no"}">{"✓" if ok else "—"} {name}</span>'
        for name, ok in rec["ict_systems"].items()
    )

    return f"""
<div class="card">
  <div class="card-accent"></div>
  {image_html}
  <div class="card-body">
    <div class="card-maker">{rec.get("maker") or "—"}</div>
    <div class="card-model">{rec.get("model") or "（機種名未登録）"}</div>
    <div class="card-spec">{rec.get("spec") or "仕様情報なし"}</div>
    <div class="badge-row">{badges}</div>
  </div>
</div>
"""


# ─────────────────────────────────────────
# メインアプリ
# ─────────────────────────────────────────
def main():
    st.markdown("""
    <div class="app-header">
      <div class="app-header-inner">
        <div class="header-icon">🏗️</div>
        <div>
          <div class="header-title">ICT施工・取付実績</div>
          <div class="header-subtitle">Construction ICT Catalog</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

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
            st.error(f"Notion APIエラー: {e}")
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

    st.markdown(f'<div class="result-count">📋 {len(filtered)} 件の実績</div>', unsafe_allow_html=True)

    if not filtered:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-state-icon">🔍</div>
          <div class="empty-state-msg">該当する実績が見つかりません</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for row in [filtered[i:i+3] for i in range(0, len(filtered), 3)]:
            cols = st.columns(3, gap="medium")
            for col, rec in zip(cols, row):
                with col:
                    st.markdown(render_card_html(rec), unsafe_allow_html=True)

    st.markdown(
        f'<div class="last-updated">最終更新: {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}　|　データは最大60秒ごとに自動更新</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
