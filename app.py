"""
ICT施工・取付実績カタログアプリ
Notion APIをDBとして使用するStreamlitアプリ
"""

import streamlit as st
from notion_client import Client
from datetime import datetime
import time

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
# カスタムCSS（スマホ最適化 + プロ仕様デザイン）
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Barlow+Condensed:wght@600;800&display=swap');

/* ── ベースリセット ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #0f1117 !important;
    color: #e8eaed !important;
    font-family: 'Noto Sans JP', sans-serif !important;
}

/* ── ヘッダー ── */
.app-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #141820 100%);
    border-bottom: 2px solid #f59e0b;
    padding: 20px 24px 16px;
    margin-bottom: 0;
}
.app-header-inner {
    display: flex;
    align-items: center;
    gap: 14px;
}
.header-icon {
    font-size: 2rem;
    line-height: 1;
}
.header-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #f59e0b;
    letter-spacing: 0.05em;
    line-height: 1.1;
}
.header-subtitle {
    font-size: 0.7rem;
    color: #6b7280;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── 検索バー ── */
.search-section {
    background: #141820;
    border-bottom: 1px solid #1f2532;
    padding: 16px 20px;
    position: sticky;
    top: 0;
    z-index: 100;
}

/* ── Streamlit部品の上書き ── */
.stTextInput > div > div > input {
    background: #1a1f2e !important;
    border: 1.5px solid #2a3146 !important;
    border-radius: 10px !important;
    color: #e8eaed !important;
    font-family: 'Noto Sans JP', sans-serif !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
    height: auto !important;
}
.stTextInput > div > div > input:focus {
    border-color: #f59e0b !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.15) !important;
}
.stSelectbox > div > div {
    background: #1a1f2e !important;
    border: 1.5px solid #2a3146 !important;
    border-radius: 10px !important;
    color: #e8eaed !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #f59e0b !important;
}

/* ── 更新ボタン ── */
.stButton > button {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    color: #0f1117 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    width: 100% !important;
    transition: opacity 0.15s, transform 0.1s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── カード ── */
.card {
    background: linear-gradient(160deg, #1a1f2e 0%, #141820 100%);
    border: 1px solid #1f2532;
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 20px;
    position: relative;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(245,158,11,0.25);
}
.card-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #f59e0b, #d97706);
}

/* 画像エリア */
.card-image-wrap {
    position: relative;
    width: 100%;
    padding-top: 62%;
    background: #0d111a;
    overflow: hidden;
}
.card-image-wrap img {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    object-fit: cover;
    transition: transform 0.4s;
}
.card:hover .card-image-wrap img {
    transform: scale(1.03);
}
.no-image {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #374151;
    gap: 8px;
}
.no-image-icon {
    font-size: 2.5rem;
    opacity: 0.4;
}
.no-image-text {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    opacity: 0.5;
    text-transform: uppercase;
}

/* カード本文 */
.card-body {
    padding: 16px 18px 18px;
}
.card-maker {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #f59e0b;
    margin-bottom: 4px;
}
.card-model {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #f3f4f6;
    line-height: 1.2;
    margin-bottom: 6px;
}
.card-spec {
    font-size: 0.75rem;
    color: #6b7280;
    margin-bottom: 14px;
    line-height: 1.5;
}

/* ICTバッジ */
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    line-height: 1;
}
.badge-yes {
    background: rgba(16,185,129,0.15);
    color: #10b981;
    border: 1px solid rgba(16,185,129,0.3);
}
.badge-no {
    background: rgba(75,85,99,0.2);
    color: #4b5563;
    border: 1px solid rgba(75,85,99,0.2);
}

/* フォトカウント */
.photo-count {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(4px);
    color: #d1d5db;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 20px;
    letter-spacing: 0.04em;
}

/* 件数バッジ */
.result-count {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    color: #f59e0b;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 16px;
    letter-spacing: 0.05em;
}

/* 最終更新 */
.last-updated {
    font-size: 0.65rem;
    color: #374151;
    text-align: center;
    padding: 8px;
    letter-spacing: 0.06em;
}

/* エラー・空状態 */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #374151;
}
.empty-state-icon { font-size: 3rem; }
.empty-state-msg {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 12px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* divider */
hr { border-color: #1f2532 !important; }

/* Streamlit余白リセット */
.block-container { padding-top: 0 !important; padding-bottom: 20px !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stSpinner > div { color: #f59e0b !important; }

/* ラベル */
label[data-testid="stWidgetLabel"] {
    color: #9ca3af !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Notion クライアント初期化
# ─────────────────────────────────────────
@st.cache_resource
def get_notion_client():
    """Notionクライアントをシングルトンで返す"""
    return Client(auth=st.secrets["NOTION_TOKEN"])


# ─────────────────────────────────────────
# データ取得（TTL=60秒でキャッシュ）
# ─────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def fetch_all_records(database_id: str) -> list[dict]:
    """
    Notionデータベースから全レコードを取得する。
    ページネーションに対応し、全件を返す。
    TTL=60秒なので最大1分で最新データが反映される。
    """
    notion = get_notion_client()
    results = []
    has_more = True
    start_cursor = None

    while has_more:
        kwargs = {
            "database_id": database_id,
            "page_size": 100,
        }
        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        response = notion.databases.query(**kwargs)
        results.extend(response.get("results", []))
        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")

    return results


def force_refresh():
    """キャッシュをクリアして強制再取得"""
    fetch_all_records.clear()
    st.rerun()


# ─────────────────────────────────────────
# プロパティ取得ヘルパー
# ─────────────────────────────────────────
def get_title(props: dict, key: str) -> str:
    """titleプロパティからテキストを取得"""
    try:
        return props[key]["title"][0]["plain_text"]
    except (KeyError, IndexError):
        return ""


def get_rich_text(props: dict, key: str) -> str:
    """rich_textプロパティからテキストを取得"""
    try:
        return props[key]["rich_text"][0]["plain_text"]
    except (KeyError, IndexError):
        return ""


def get_select(props: dict, key: str) -> str:
    """selectプロパティから値を取得"""
    try:
        return props[key]["select"]["name"] or ""
    except (KeyError, TypeError):
        return ""


def get_checkbox(props: dict, key: str) -> bool:
    """checkboxプロパティからboolを取得"""
    try:
        return props[key]["checkbox"]
    except KeyError:
        return False


def get_files(props: dict, key: str) -> list[str]:
    """
    files（ファイル&メディア）プロパティから画像URLリストを取得。
    Notionの内部ファイル（S3）はURLが1時間で失効するため、
    毎回このヘルパーを呼び出す設計になっている。
    """
    try:
        files = props[key]["files"]
        urls = []
        for f in files:
            file_type = f.get("type", "")
            if file_type == "file":
                # Notionホスト（S3一時URL）
                url = f["file"]["url"]
            elif file_type == "external":
                # 外部URL
                url = f["external"]["url"]
            else:
                continue
            if url:
                urls.append(url)
        return urls
    except (KeyError, TypeError):
        return []


# ─────────────────────────────────────────
# レコードをパース
# ─────────────────────────────────────────
def parse_record(page: dict) -> dict:
    """
    Notionページオブジェクトをアプリ用dictに変換する。

    【Notionデータベースのプロパティ名の対応】
    以下のプロパティ名はお客様のNotionDBに合わせて変更してください。
    ─────────────────────────────────────────────
    "機種名"         : タイトルプロパティ（title）
    "メーカー"       : セレクト（select）
    "車体仕様"       : テキスト（rich_text）
    "実績写真"       : ファイル&メディア（files）
    "杭ナビ"        : チェックボックス（checkbox）
    "ICT建機"       : チェックボックス（checkbox）
    "マシンガイダンス": チェックボックス（checkbox）
    "自動追尾TS"    : チェックボックス（checkbox）
    "ICTドローン"   : チェックボックス（checkbox）
    ─────────────────────────────────────────────
    """
    props = page.get("properties", {})

    return {
        "id": page["id"],
        "model": get_title(props, "機種名"),
        "maker": get_select(props, "メーカー"),
        "spec": get_rich_text(props, "車体仕様"),
        "photos": get_files(props, "実績写真"),   # 毎回新規取得（S3 URL対策）
        "ict_systems": {
            "杭ナビ":         get_checkbox(props, "杭ナビ"),
            "ICT建機":        get_checkbox(props, "ICT建機"),
            "MG":             get_checkbox(props, "マシンガイダンス"),
            "自動追尾TS":     get_checkbox(props, "自動追尾TS"),
            "ICTドローン":    get_checkbox(props, "ICTドローン"),
        },
    }


# ─────────────────────────────────────────
# カードHTML生成
# ─────────────────────────────────────────
def render_card_html(rec: dict) -> str:
    """1機種分のカードHTMLを返す"""
    # 写真
    photos = rec.get("photos", [])
    if photos:
        first_url = photos[0]
        photo_count_html = (
            f'<div class="photo-count">📷 {len(photos)}</div>'
            if len(photos) > 1 else ""
        )
        image_html = f"""
<div class="card-image-wrap">
  <img src="{first_url}" alt="{rec['model']}の実績写真" loading="lazy">
  {photo_count_html}
</div>"""
    else:
        image_html = """
<div class="card-image-wrap">
  <div class="no-image">
    <div class="no-image-icon">📷</div>
    <div class="no-image-text">NO IMAGE</div>
  </div>
</div>"""

    # ICTバッジ
    badges_html = '<div class="badge-row">'
    for name, ok in rec["ict_systems"].items():
        cls = "badge-yes" if ok else "badge-no"
        icon = "✓" if ok else "—"
        badges_html += f'<span class="badge {cls}">{icon} {name}</span>'
    badges_html += "</div>"

    # メーカー・機種名・仕様
    maker = rec.get("maker") or "—"
    model = rec.get("model") or "（機種名未登録）"
    spec = rec.get("spec") or "仕様情報なし"

    return f"""
<div class="card">
  <div class="card-accent"></div>
  {image_html}
  <div class="card-body">
    <div class="card-maker">{maker}</div>
    <div class="card-model">{model}</div>
    <div class="card-spec">{spec}</div>
    {badges_html}
  </div>
</div>
"""


# ─────────────────────────────────────────
# メインアプリ
# ─────────────────────────────────────────
def main():
    # ── ヘッダー ──
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

    # ── secrets チェック ──
    if "NOTION_TOKEN" not in st.secrets or "NOTION_DATABASE_ID" not in st.secrets:
        st.error(
            "⚠️ `st.secrets` に `NOTION_TOKEN` と `NOTION_DATABASE_ID` を設定してください。\n\n"
            "**Streamlit Community Cloud の場合:** Settings > Secrets に以下を追加\n"
            "```toml\n"
            "NOTION_TOKEN = 'secret_xxxxxx'\n"
            "NOTION_DATABASE_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'\n"
            "```"
        )
        st.stop()

    database_id: str = st.secrets["NOTION_DATABASE_ID"]

    # ── データ取得 ──
    with st.spinner("最新データを取得中..."):
        try:
            raw_records = fetch_all_records(database_id)
        except Exception as e:
            st.error(f"Notion APIエラー: {e}")
            st.stop()

    records = [parse_record(r) for r in raw_records]

    # ── 検索UI ──
    col_maker, col_search, col_btn = st.columns([2, 3, 1.2])

    # メーカー一覧（Noneやブランク除外）
    makers = sorted({r["maker"] for r in records if r.get("maker")})
    maker_options = ["すべて"] + makers

    with col_maker:
        selected_maker = st.selectbox("メーカー", maker_options, label_visibility="visible")

    with col_search:
        search_query = st.text_input("機種名で検索", placeholder="例: PC200, ZX135...", label_visibility="visible")

    with col_btn:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        if st.button("🔄 更新", help="Notionから最新データを取得"):
            force_refresh()

    # ── フィルタリング ──
    filtered = records

    if selected_maker != "すべて":
        filtered = [r for r in filtered if r.get("maker") == selected_maker]

    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [r for r in filtered if q in r.get("model", "").lower()]

    # ── 件数表示 ──
    st.markdown(
        f'<div class="result-count">📋 {len(filtered)} 件の実績</div>',
        unsafe_allow_html=True,
    )

    # ── カード一覧 ──
    if not filtered:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-state-icon">🔍</div>
          <div class="empty-state-msg">該当する実績が見つかりません</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # スマホ: 2列、PC: 3列
        cols_per_row = 3
        rows = [filtered[i:i + cols_per_row] for i in range(0, len(filtered), cols_per_row)]

        for row in rows:
            cols = st.columns(cols_per_row, gap="medium")
            for col, rec in zip(cols, row):
                with col:
                    st.markdown(render_card_html(rec), unsafe_allow_html=True)

    # ── 最終更新時刻 ──
    now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    st.markdown(
        f'<div class="last-updated">最終更新: {now_str}　|　データは最大60秒ごとに自動更新</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
