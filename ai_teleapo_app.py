import streamlit as st
import pandas as pd
import re
import csv
import datetime
import openpyxl
import hashlib
import json
import time
from pathlib import Path
from io import BytesIO, StringIO

st.set_page_config(
    page_title="AI管理システム",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ベース */
html, body, [class*="css"] { font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif; }
.stApp { background-color: #f5f6fa; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1200px; }

/* サイドバー */
section[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #94a3b8 !important;
    text-align: left !important;
    padding: 0.55rem 1rem !important;
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e293b !important;
    color: #f1f5f9 !important;
}

/* ヘッダーバー */
.topbar-ds {
    background: #1e3a8a;
    border-radius: 10px;
    padding: 1.25rem 1.75rem;
    margin-bottom: 1.5rem;
    color: white;
}
.topbar-ai {
    background: #0369a1;
    border-radius: 10px;
    padding: 1.25rem 1.75rem;
    margin-bottom: 1.5rem;
    color: white;
}
.topbar-ds h2, .topbar-ai h2 {
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.01em;
}
.topbar-ds p, .topbar-ai p {
    font-size: 0.82rem;
    opacity: 0.8;
    margin: 0;
}

/* カード */
.card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.card-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.6rem;
}

/* ステップ番号 */
.step-num-ds {
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 50%;
    background: #1e3a8a; color: white;
    font-size: 0.72rem; font-weight: 700;
    margin-right: 0.5rem; vertical-align: middle;
}
.step-num-ai {
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 50%;
    background: #0369a1; color: white;
    font-size: 0.72rem; font-weight: 700;
    margin-right: 0.5rem; vertical-align: middle;
}

/* アラートボックス */
.alert-success {
    background: #f0fdf4; border-left: 4px solid #22c55e;
    border-radius: 6px; padding: 0.9rem 1.1rem; margin: 0.8rem 0;
    font-size: 0.875rem; color: #166534;
}
.alert-warn {
    background: #fffbeb; border-left: 4px solid #f59e0b;
    border-radius: 6px; padding: 0.9rem 1.1rem; margin: 0.8rem 0;
    font-size: 0.875rem; color: #92400e;
}
.alert-info {
    background: #eff6ff; border-left: 4px solid #3b82f6;
    border-radius: 6px; padding: 0.9rem 1.1rem; margin: 0.8rem 0;
    font-size: 0.875rem; color: #1e40af;
}

/* ホームカード */
.home-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem; }
.home-card {
    border-radius: 10px; padding: 1.5rem;
    color: white; position: relative;
}
.home-card-ds  { background: #1e3a8a; }
.home-card-ai  { background: #0369a1; }
.home-card-wip { background: #475569; }
.home-card .tag {
    position: absolute; top: 1rem; right: 1rem;
    background: rgba(255,255,255,0.2);
    border-radius: 4px; padding: 0.15rem 0.55rem;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.08em;
}
.home-card h3 { font-size: 1rem; font-weight: 700; margin: 0.5rem 0 0.4rem 0; }
.home-card p  { font-size: 0.8rem; opacity: 0.85; margin: 0; line-height: 1.6; }

/* 工事中 */
.wip-block {
    background: #1e293b;
    border-radius: 10px; padding: 5rem 2rem;
    text-align: center; color: #94a3b8; margin: 2rem 0;
}
.wip-block h2 { font-size: 1.5rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.6rem 0; }
.wip-block p  { font-size: 0.9rem; line-height: 1.8; margin: 0; }

/* ダウンロードボタン */
.stDownloadButton > button {
    background: #16a34a !important;
    color: white !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1.8rem !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
}
.stDownloadButton > button:hover { background: #15803d !important; }

/* プライマリボタン */
.stButton > button[kind="primary"] {
    border-radius: 7px !important;
    font-weight: 600 !important;
}

/* サイドバーロゴ */
.sb-logo {
    padding: 1.5rem 1rem 1rem 1rem;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 0.5rem;
}
.sb-logo h2 {
    font-size: 0.95rem; font-weight: 800;
    color: #f1f5f9 !important; margin: 0;
    letter-spacing: -0.01em;
}
.sb-logo p { font-size: 0.72rem; color: #64748b !important; margin: 0.2rem 0 0 0; }
.sb-section {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #475569 !important;
    padding: 0.9rem 1rem 0.3rem 1rem; margin: 0;
}

/* テーブル */
.stat-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.stat-table th {
    background: #f1f5f9; color: #475569;
    padding: 0.5rem 0.75rem; text-align: left;
    font-weight: 600; font-size: 0.78rem;
    border-bottom: 1px solid #e2e8f0;
}
.stat-table td {
    padding: 0.45rem 0.75rem;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ロジック: ダイヤルシフト リスト成形（Excel入力）
# ============================================================
COL_ID       = 3
COL_CUSTOMER = 7
COL_ADDRESS  = 8
COL_PHONE    = 9
MAX_KEEP_BEFORE_O = 14

def normalize_phone(value):
    if value is None:
        return ''
    s = str(value).strip()
    if re.fullmatch(r'\d+\.0', s):
        s = s[:-2]
    digits = re.sub(r'[^0-9]', '', s)
    if len(digits) == 10 and digits[0] in ('7', '8', '9'):
        digits = '0' + digits
    return digits

def is_valid_phone(value):
    digits = normalize_phone(value)
    if not digits.isdigit():
        return False
    if len(digits) not in (10, 11):
        return False
    if not digits.startswith('0'):
        return False
    return True

def safe_str(value):
    if value is None:
        return ''
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y/%m/%d')
    if isinstance(value, datetime.date):
        return value.strftime('%Y/%m/%d')
    if isinstance(value, datetime.timedelta):
        total = int(value.total_seconds())
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        return f'{h}:{m:02d}:{s:02d}'
    return str(value).strip()

def process_ds_list(file_bytes):
    wb = openpyxl.load_workbook(BytesIO(file_bytes), data_only=True)
    ws = wb.active
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]

    priority_indices = [COL_CUSTOMER, COL_PHONE, COL_ID, COL_ADDRESS]
    priority_headers = ['顧客名', '電話番号', 'IDの頭にID', '住所統合']
    remaining_indices = [
        i for i in range(min(MAX_KEEP_BEFORE_O, len(headers)))
        if i not in set(priority_indices)
    ]
    out_indices = priority_indices + remaining_indices
    out_headers = priority_headers + [safe_str(headers[i]) for i in remaining_indices]

    removed_rows = []
    kept_rows = [out_headers]

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if all(cell is None or str(cell).strip() == '' for cell in row):
            removed_rows.append((row_idx, '空白行'))
            continue
        customer_name = row[COL_CUSTOMER] if len(row) > COL_CUSTOMER else None
        if customer_name is None or str(customer_name).strip() == '':
            removed_rows.append((row_idx, '顧客名が未入力'))
            continue
        phone_raw = row[COL_PHONE] if len(row) > COL_PHONE else None
        if not is_valid_phone(phone_raw):
            removed_rows.append((row_idx, f'電話番号「{phone_raw}」が不正形式'))
            continue
        out_row = []
        for idx in out_indices:
            value = row[idx] if len(row) > idx else None
            if idx == COL_PHONE:
                out_row.append(normalize_phone(value))
            else:
                out_row.append(safe_str(value))
        kept_rows.append(out_row)

    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerows(kept_rows)
    csv_bytes = buf.getvalue().encode('utf-8-sig')

    return csv_bytes, kept_rows, removed_rows, ws.max_row


# ============================================================
# ロジック: ダイヤルシフト FM返送（CSV入力）
# ============================================================
CONVERSION_MAP = {
    "AI終話": "NG",
    "応答なし": "留守",
    "AI対応不可": "留守電",
    "AI同時接続": "再コール・転送成功",
    "留守番電話": "留守電",
    "コール結果記録中": "再コール・転送成功",
    "手動受信_未対応": "受電あり",
    "トスアップ応答前終了": "再コール・転送成功",
    "コール結果未登録": "再コール・転送成功",
    "転送\u3000NG": "NG",
    "転送\u3000再コール": "再コール・転送成功",
    "転送\u3000アポ禁": "アポ禁",
    "転送\u3000留守電": "留守電",
    "受電\u3000NG": "NG",
    "受電\u3000再コール": "再コール",
    "受電\u3000アポ禁": "アポ禁",
    "受電\u3000電話APO": "受電電話APO",
    "受電\u3000留守電": "留守電",
    "AIコールNG": "NG",
    "AIホットリード": "再コール・転送成功",
}

VALIDITY_MAP = {
    "AI終話": "有効",
    "応答なし": "無効",
    "AI対応不可": "有効",
    "AI同時接続": "有効",
    "留守番電話": "有効",
    "コール結果記録中": "有効",
    "手動受信_未対応": "",
    "トスアップ応答前終了": "有効",
    "コール結果未登録": "有効",
    "転送\u3000NG": "有効",
    "転送\u3000再コール": "有効",
    "転送\u3000アポ禁": "有効",
    "転送\u3000留守電": "有効",
    "受電\u3000NG": "有効",
    "受電\u3000再コール": "有効",
    "受電\u3000アポ禁": "有効",
    "受電\u3000電話APO": "有効",
    "受電\u3000留守電": "有効",
    "AIコールNG": "無効",
    "AIホットリード": "有効",
}

DROP_FLAGS = {"転送\u3000お題成立", "転送\u3000紐づけ", "受電\u3000お題成立", "受電\u3000紐づけ"}

DROP_COLUMNS = [
    "次回コール予定日時", "次回コール予定日", "次回コール予定日時 (AI)",
    "通話時間", "通話時間(秒)", "ステータス", "方向", "コール担当者",
    "コールリスト", "通話ID", "文字起こし", "住所", "住所統合",
]

def process_ds_fm(raw_bytes):
    df = None
    used_enc = None
    for enc in ["utf-8-sig", "utf-8", "cp932", "shift_jis"]:
        try:
            df = pd.read_csv(BytesIO(raw_bytes), encoding=enc)
            used_enc = enc
            break
        except Exception:
            continue
    if df is None:
        raise ValueError("CSVを読み込めませんでした。文字コードを確認してください。")

    rows_before = len(df)

    if "コール日時" in df.columns:
        call_datetime = pd.to_datetime(df["コール日時"], errors="coerce")
        loc = df.columns.get_loc("コール日時")
        df.insert(loc + 1, "コール日",   call_datetime.dt.strftime("%Y-%m-%d"))
        df.insert(loc + 2, "コール時間", call_datetime.dt.strftime("%H:%M:%S"))
        df = df.drop(columns=["コール日時"])

    if "コール結果" in df.columns:
        original_result = df["コール結果"].astype("string").str.strip().str.replace(" ", "\u3000", regex=False)
        df = df[~original_result.isin(DROP_FLAGS)].copy()
        original_result = df["コール結果"].astype("string").str.strip().str.replace(" ", "\u3000", regex=False)
        df["コール結果"]   = original_result.map(CONVERSION_MAP).fillna(original_result)
        df["有効無効判定"] = original_result.map(VALIDITY_MAP).fillna("")

    df = df.drop(columns=[c for c in DROP_COLUMNS if c in df.columns])

    rows_after = len(df)
    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    return csv_bytes, df, rows_before, rows_after, used_enc


# ============================================================
# ロジック: AIテレアポ リスト成形（既存ロジック）
# ============================================================
def process_ai_list(file_bytes, filename):
    df = pd.read_excel(BytesIO(file_bytes))
    upload_df = df.copy()

    if '顧客名' in upload_df.columns:
        upload_df = upload_df.rename(columns={'顧客名': '社名'})

    required_columns = ['社名', '電話番号', '住所統合']
    available_columns = [col for col in required_columns if col in upload_df.columns]
    if available_columns:
        upload_df = upload_df[available_columns].copy()

    if '社名' in upload_df.columns:
        upload_df['社名'] = upload_df['社名'].astype(str).str[:50]

    if 'IDの頭にID' in df.columns:
        upload_df['IDの頭にID'] = df['IDの頭にID'].values

    try:
        csv_bytes = upload_df.to_csv(index=False, encoding='shift_jis').encode('shift_jis')
    except UnicodeEncodeError:
        csv_bytes = upload_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    return csv_bytes, upload_df


# ============================================================
# セッション初期化
# ============================================================
def init_session():
    if 'page' not in st.session_state:
        st.session_state.page = 'home'


# ============================================================
# サイドバー
# ============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sb-logo">
            <h2>AI管理システム</h2>
            <p>架電リスト成形 / FM返送</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="sb-section">Dial Shift</p>', unsafe_allow_html=True)
        if st.button("リスト成形", key="nav_ds_list", use_container_width=True):
            st.session_state.page = 'ds_list'
            st.rerun()
        if st.button("ファイルメーカー返送", key="nav_ds_fm", use_container_width=True):
            st.session_state.page = 'ds_fm'
            st.rerun()

        st.markdown('<p class="sb-section">AI Teleapo</p>', unsafe_allow_html=True)
        if st.button("リスト成形", key="nav_ai_list", use_container_width=True):
            st.session_state.page = 'ai_list'
            st.rerun()
        if st.button("ファイルメーカー返送", key="nav_ai_fm", use_container_width=True):
            st.session_state.page = 'ai_fm'
            st.rerun()

        st.markdown('<p class="sb-section">Menu</p>', unsafe_allow_html=True)
        if st.button("ホーム", key="nav_home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()


# ============================================================
# ページ: ホーム
# ============================================================
def page_home():
    st.markdown("""
    <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem;font-weight:800;color:#0f172a;margin:0 0 0.3rem 0;letter-spacing:-0.02em;">
            AI管理システム
        </h1>
        <p style="color:#64748b;font-size:0.9rem;margin:0;">
            ダイヤルシフト・AIテレアポのリスト成形とファイルメーカー返送
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="home-grid">
        <div class="home-card home-card-ds">
            <div class="tag">DIAL SHIFT</div>
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;opacity:0.7;text-transform:uppercase;">01</div>
            <h3>リスト成形</h3>
            <p>Excelをアップロードして顧客名・電話番号・住所を整形。電話番号バリデーション付き。</p>
        </div>
        <div class="home-card home-card-ds">
            <div class="tag">DIAL SHIFT</div>
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;opacity:0.7;text-transform:uppercase;">02</div>
            <h3>ファイルメーカー返送</h3>
            <p>ダイヤルシフトの履歴CSVをアップロードしてコール結果変換・有効無効判定を付与。</p>
        </div>
        <div class="home-card home-card-ai">
            <div class="tag">AI TELEAPO</div>
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;opacity:0.7;text-transform:uppercase;">03</div>
            <h3>リスト成形</h3>
            <p>FileMakerデータをAIテレアポ投入用CSVに変換。社名・電話番号・住所統合を整形。</p>
        </div>
        <div class="home-card home-card-wip">
            <div class="tag">COMING SOON</div>
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;opacity:0.7;text-transform:uppercase;">04</div>
            <h3>ファイルメーカー返送</h3>
            <p>現在開発中です。</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-info" style="margin-top:1.5rem;">
        左のサイドバーから機能を選択してください。
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ページ: DS リスト成形
# ============================================================
def page_ds_list():
    st.markdown("""
    <div class="topbar-ds">
        <h2>ダイヤルシフト — リスト成形</h2>
        <p>Excelをアップロードして顧客名・電話番号・ID・住所を先頭に並び替え、電話番号バリデーション後にCSV出力</p>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown('<div class="card"><div class="card-label"><span class="step-num-ds">1</span>Excelファイルをアップロード</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "FileMakerからエクスポートしたExcel (.xlsx / .xls) を選択",
            type=['xlsx', 'xls'],
            key="ds_list_upload",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded:
            file_bytes = uploaded.read()
            st.markdown(f"""
            <div class="alert-success">
                読み込み完了 — {uploaded.name} ({len(file_bytes)//1024:,} KB)
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-label"><span class="step-num-ds">2</span>成形を実行</div>', unsafe_allow_html=True)
            if st.button("成形を実行", type="primary", key="ds_list_run"):
                with st.spinner("処理中..."):
                    try:
                        csv_bytes, kept_rows, removed_rows, total_rows = process_ds_list(file_bytes)

                        data_in  = total_rows - 1
                        data_out = len(kept_rows) - 1
                        deleted  = len(removed_rows)

                        st.markdown(f"""
                        <div class="alert-success">
                            成形完了 — 入力: {data_in:,} 件 / 出力: {data_out:,} 件 / 削除: {deleted:,} 件
                        </div>
                        """, unsafe_allow_html=True)

                        if removed_rows:
                            with st.expander(f"削除された行の詳細 ({deleted} 件)"):
                                del_df = pd.DataFrame(removed_rows, columns=["行番号", "削除理由"])
                                st.dataframe(del_df, use_container_width=True, hide_index=True)

                        preview_df = pd.DataFrame(kept_rows[1:6], columns=kept_rows[0])
                        with st.expander("出力データプレビュー（先頭5件）"):
                            st.dataframe(preview_df, use_container_width=True, hide_index=True)

                        base = uploaded.name.rsplit('.', 1)[0]
                        date_str = datetime.datetime.now().strftime("%Y%m%d")
                        out_name = f"{base}_{date_str}_整形済.csv"

                        st.markdown("---")
                        st.download_button(
                            label="CSVをダウンロード",
                            data=csv_bytes,
                            file_name=out_name,
                            mime="text/csv",
                            key="ds_list_dl"
                        )
                    except Exception as e:
                        st.error(f"処理エラー: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="card">
            <div class="card-label">処理内容</div>
            <table class="stat-table">
                <tr><td>列の並び替え</td></tr>
                <tr><td>顧客名・電話番号・ID・住所を先頭に移動</td></tr>
                <tr><td>電話番号バリデーション（0始まり 10〜11桁）</td></tr>
                <tr><td>空白行・顧客名未入力行を削除</td></tr>
                <tr><td>A〜N列（14列）を保持</td></tr>
                <tr><td>UTF-8 BOM付きCSVで出力</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# ページ: DS FM返送
# ============================================================
def page_ds_fm():
    st.markdown("""
    <div class="topbar-ds">
        <h2>ダイヤルシフト — ファイルメーカー返送</h2>
        <p>ダイヤルシフトの履歴CSVをアップロードしてコール結果変換・有効無効判定を付与してCSV出力</p>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown('<div class="card"><div class="card-label"><span class="step-num-ds">1</span>ダイヤルシフト履歴CSVをアップロード</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "ダイヤルシフトからエクスポートしたCSVを選択",
            type=['csv'],
            key="ds_fm_upload",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded:
            raw = uploaded.read()
            st.markdown(f"""
            <div class="alert-success">
                読み込み完了 — {uploaded.name} ({len(raw)//1024:,} KB)
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="card"><div class="card-label"><span class="step-num-ds">2</span>変換を実行</div>', unsafe_allow_html=True)
            if st.button("変換を実行", type="primary", key="ds_fm_run"):
                with st.spinner("処理中..."):
                    try:
                        csv_bytes, result_df, rows_before, rows_after, used_enc = process_ds_fm(raw)

                        st.markdown(f"""
                        <div class="alert-success">
                            変換完了 — 入力: {rows_before:,} 件 / 出力: {rows_after:,} 件 / 削除: {rows_before - rows_after:,} 件
                            &nbsp;&nbsp;|&nbsp;&nbsp; 文字コード: {used_enc}
                        </div>
                        """, unsafe_allow_html=True)

                        if "コール結果" in result_df.columns:
                            dist = result_df["コール結果"].value_counts().reset_index()
                            dist.columns = ["コール結果", "件数"]
                            with st.expander("コール結果の分布"):
                                st.dataframe(dist, use_container_width=True, hide_index=True)

                        with st.expander("出力データプレビュー（先頭5件）"):
                            st.dataframe(result_df.head(5), use_container_width=True)

                        base = uploaded.name.rsplit('.', 1)[0]
                        date_str = datetime.datetime.now().strftime("%Y%m%d")
                        out_name = f"{base}_{date_str}_formatted.csv"

                        st.markdown("---")
                        st.download_button(
                            label="CSVをダウンロード",
                            data=csv_bytes,
                            file_name=out_name,
                            mime="text/csv",
                            key="ds_fm_dl"
                        )
                    except Exception as e:
                        st.error(f"処理エラー: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="card">
            <div class="card-label">処理内容</div>
            <table class="stat-table">
                <tr><td>コール日時 → コール日 / コール時間 に分割</td></tr>
                <tr><td>お題成立・紐づけ行を削除</td></tr>
                <tr><td>コール結果を変換マップで置換</td></tr>
                <tr><td>有効無効判定を自動付与</td></tr>
                <tr><td>不要列（通話時間・住所など）を削除</td></tr>
                <tr><td>UTF-8 BOM付きCSVで出力</td></tr>
            </table>
        </div>
        <div class="card" style="margin-top:0.5rem;">
            <div class="card-label">変換マップ（主要）</div>
            <table class="stat-table">
                <tr><th>元の値</th><th>変換後</th></tr>
                <tr><td>AI終話</td><td>NG</td></tr>
                <tr><td>応答なし</td><td>留守</td></tr>
                <tr><td>AI対応不可</td><td>留守電</td></tr>
                <tr><td>留守番電話</td><td>留守電</td></tr>
                <tr><td>転送　NG</td><td>NG</td></tr>
                <tr><td>転送　再コール</td><td>再コール・転送成功</td></tr>
                <tr><td>受電　電話APO</td><td>受電電話APO</td></tr>
                <tr><td>AIホットリード</td><td>再コール・転送成功</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# ページ: AI リスト成形
# ============================================================
def page_ai_list():
    st.markdown("""
    <div class="topbar-ai">
        <h2>AIテレアポ — リスト成形</h2>
        <p>FileMakerデータをAIテレアポ投入用CSVに変換（社名・電話番号・住所統合を整形）</p>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown('<div class="card"><div class="card-label"><span class="step-num-ai">1</span>FileMakerデータ（Excel）をアップロード</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "FileMakerから出力したExcelファイルを選択",
            type=['xlsx', 'xls'],
            key="ai_list_upload",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded:
            file_bytes = uploaded.read()
            st.markdown(f"""
            <div class="alert-success">
                読み込み完了 — {uploaded.name} ({len(file_bytes)//1024:,} KB)
            </div>
            """, unsafe_allow_html=True)

            try:
                preview_df = pd.read_excel(BytesIO(file_bytes))
                st.markdown(f"""
                <div class="alert-info">
                    {len(preview_df):,} 件のデータを検出しました
                </div>
                """, unsafe_allow_html=True)

                with st.expander("元データプレビュー（先頭5件）"):
                    st.dataframe(preview_df.head(5), use_container_width=True)

            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")
                return

            st.markdown('<div class="card"><div class="card-label"><span class="step-num-ai">2</span>成形を実行</div>', unsafe_allow_html=True)
            if st.button("成形を実行", type="primary", key="ai_list_run"):
                with st.spinner("処理中..."):
                    try:
                        csv_bytes, result_df = process_ai_list(file_bytes, uploaded.name)

                        st.markdown(f"""
                        <div class="alert-success">
                            成形完了 — {len(result_df):,} 件
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander("出力データプレビュー（先頭5件）"):
                            st.dataframe(result_df.head(5), use_container_width=True)

                        base = uploaded.name.rsplit('.', 1)[0]
                        date_str = datetime.datetime.now().strftime("%Y%m%d")
                        out_name = f"{base}_{date_str}_AIテレアポリスト.csv"

                        st.markdown("---")
                        st.download_button(
                            label="CSVをダウンロード",
                            data=csv_bytes,
                            file_name=out_name,
                            mime="text/csv",
                            key="ai_list_dl"
                        )
                    except Exception as e:
                        st.error(f"処理エラー: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="card">
            <div class="card-label">処理内容</div>
            <table class="stat-table">
                <tr><td>顧客名 → 社名 に列名変換</td></tr>
                <tr><td>社名を50文字でカット</td></tr>
                <tr><td>社名・電話番号・住所統合を抽出</td></tr>
                <tr><td>IDの頭にID列を付与</td></tr>
                <tr><td>Shift-JIS / UTF-8 BOMで出力</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# ページ: AI FM返送（工事中）
# ============================================================
def page_ai_fm():
    st.markdown("""
    <div class="topbar-ai">
        <h2>AIテレアポ — ファイルメーカー返送</h2>
        <p>現在開発中です</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="wip-block">
        <h2>工事中</h2>
        <p>
            AIテレアポ用ファイルメーカー返送機能は現在開発中です。<br>
            完成次第、こちらのページでご利用いただけます。<br><br>
            現在ご利用可能な機能<br>
            01 — ダイヤルシフト用リスト成形<br>
            02 — ダイヤルシフト用ファイルメーカー返送<br>
            03 — AIテレアポ用リスト成形
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# メイン
# ============================================================
def main():
    init_session()
    render_sidebar()

    page = st.session_state.get('page', 'home')

    if page == 'home':
        page_home()
    elif page == 'ds_list':
        page_ds_list()
    elif page == 'ds_fm':
        page_ds_fm()
    elif page == 'ai_list':
        page_ai_list()
    elif page == 'ai_fm':
        page_ai_fm()
    else:
        page_home()


if __name__ == "__main__":
    main()
