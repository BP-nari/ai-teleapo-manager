import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import time
from io import BytesIO
import pickle

# ページ設定
st.set_page_config(
    page_title="架電管理システム",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# カスタムCSS
# ============================================================
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; color: #1e293b; }
    .main .block-container { background-color: #f0f4f8; padding: 2rem; max-width: 1300px; }

    /* ヒーロー */
    .hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #0ea5e9 100%);
        border-radius: 20px; padding: 2.5rem 3rem; margin-bottom: 2rem;
        color: white; text-align: center;
        box-shadow: 0 8px 32px rgba(30,58,138,0.25);
    }
    .hero h1 { font-size: 2.4rem; font-weight: 800; margin: 0 0 0.5rem 0; }
    .hero p  { font-size: 1.05rem; opacity: 0.9; margin: 0; }

    /* 機能カードグリッド */
    .card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
    .func-card {
        border-radius: 16px; padding: 2rem 1.8rem; color: white;
        transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden;
    }
    .func-card:hover { transform: translateY(-4px); box-shadow: 0 12px 36px rgba(0,0,0,0.2); }
    .func-card .badge {
        position: absolute; top: 1rem; right: 1rem;
        background: rgba(255,255,255,0.25); border-radius: 20px;
        padding: 0.2rem 0.7rem; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.05em;
    }
    .func-card .icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
    .func-card h3 { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.4rem 0; }
    .func-card p  { font-size: 0.88rem; opacity: 0.88; margin: 0; line-height: 1.55; }
    .ds-card  { background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%); }
    .ai-card  { background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%); }
    .wip-card { background: linear-gradient(135deg, #475569 0%, #64748b 100%); }

    /* ページヘッダー */
    .page-header-ds {
        background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
        border-radius: 14px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
        color: white; display: flex; align-items: center; gap: 1rem;
    }
    .page-header-ai {
        background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
        border-radius: 14px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
        color: white; display: flex; align-items: center; gap: 1rem;
    }
    .page-header-ds h2, .page-header-ai h2 { font-size: 1.6rem; font-weight: 700; margin: 0; }
    .page-header-ds p,  .page-header-ai p  { font-size: 0.9rem; opacity: 0.88; margin: 0.3rem 0 0 0; }
    .page-header-icon { font-size: 2.2rem; }

    /* パネル */
    .panel {
        background: white; border-radius: 14px; padding: 1.8rem;
        margin-bottom: 1.2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    .panel h4 { font-size: 1.05rem; font-weight: 700; margin: 0 0 1rem 0; color: #1e293b; }

    /* ステップバッジ */
    .step-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 28px; height: 28px; border-radius: 50%;
        font-size: 0.8rem; font-weight: 700; color: white; margin-right: 0.5rem;
    }
    .step-ds { background: #1d4ed8; }
    .step-ai { background: #0284c7; }

    /* 結果ボックス */
    .result-success {
        background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px;
        padding: 1.2rem 1.5rem; margin: 1rem 0; color: #15803d;
    }
    .result-warning {
        background: #fffbeb; border: 2px solid #f59e0b; border-radius: 12px;
        padding: 1.2rem 1.5rem; margin: 1rem 0; color: #b45309;
    }
    .result-info {
        background: #eff6ff; border: 2px solid #3b82f6; border-radius: 12px;
        padding: 1.2rem 1.5rem; margin: 1rem 0; color: #1d4ed8;
    }

    /* 工事中バナー */
    .wip-banner {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        border-radius: 16px; padding: 4rem 2rem; text-align: center; color: white; margin: 2rem 0;
    }
    .wip-banner .wip-icon { font-size: 4rem; margin-bottom: 1rem; }
    .wip-banner h2 { font-size: 2rem; font-weight: 800; margin: 0 0 0.8rem 0; }
    .wip-banner p  { font-size: 1rem; opacity: 0.85; margin: 0; line-height: 1.8; }

    /* サイドバー */
    section[data-testid="stSidebar"] { background: #1e293b !important; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .sidebar-logo {
        text-align: center; padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid #334155; margin-bottom: 1rem;
    }
    .sidebar-logo .logo-icon { font-size: 2.5rem; }
    .sidebar-logo h3 { font-size: 1rem; font-weight: 700; margin: 0.5rem 0 0 0; color: #f1f5f9 !important; }
    .nav-section-title {
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
        color: #94a3b8 !important; text-transform: uppercase;
        padding: 0.8rem 0 0.3rem 0; margin: 0;
    }

    /* ボタン */
    .stButton > button { border-radius: 8px; font-weight: 600; transition: all 0.2s; border: none; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important; border: none !important; border-radius: 8px !important;
        font-weight: 700 !important; font-size: 1rem !important;
        padding: 0.8rem 2rem !important; width: 100% !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        transform: translateY(-1px) !important;
    }

    /* ファイルアップローダー */
    .stFileUploader > div {
        border: 2px dashed #94a3b8; border-radius: 12px; background: white; padding: 1.5rem; text-align: center;
    }
    .stFileUploader > div:hover { border-color: #3b82f6; background: #eff6ff; }

    /* ジョブカード */
    .job-card {
        background: white; border-radius: 12px; padding: 1.2rem 1.5rem;
        margin: 0.8rem 0; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .job-card-title { font-weight: 700; color: #1e293b; font-size: 0.95rem; }
    .job-card-meta  { font-size: 0.82rem; color: #64748b; margin-top: 0.3rem; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# ジョブ履歴マネージャー
# ============================================================
class JobHistoryManager:
    def __init__(self):
        self.history_file = Path("job_history.json")
        self.download_cache_dir = Path("download_cache")
        self.download_cache_dir.mkdir(exist_ok=True)

    def save_jobs(self, jobs):
        try:
            serializable = []
            for job in jobs:
                j = job.copy()
                if isinstance(j.get('created_at'), datetime):
                    j['created_at'] = j['created_at'].isoformat()
                serializable.append(j)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"保存エラー: {e}")
            return False

    def load_jobs(self):
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                for job in jobs:
                    if isinstance(job.get('created_at'), str):
                        try:
                            job['created_at'] = datetime.fromisoformat(job['created_at'])
                        except Exception:
                            job['created_at'] = datetime.now()
                return jobs
            return []
        except Exception as e:
            st.error(f"読み込みエラー: {e}")
            return []

    def clear_jobs(self):
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            return True
        except Exception as e:
            st.error(f"クリアエラー: {e}")
            return False


# ============================================================
# AIテレアポ マネージャー（既存ロジック継承）
# ============================================================
class AITeleapoManager:
    def __init__(self):
        self.base_dir = Path("teleapo_jobs")
        self.base_dir.mkdir(exist_ok=True)

    def generate_job_id(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:5].upper()
        return f"{timestamp}_{suffix}"

    def normalize_phone(self, phone_str):
        if pd.isna(phone_str):
            return ""
        s = str(phone_str)
        s = re.sub(r'^\+81\s*', '0', s)
        s = re.sub(r'[\s\-\(\)]', '', s)
        return s

    def normalize_text(self, text):
        if pd.isna(text):
            return ""
        return str(text).strip()

    def create_row_key(self, company, phone):
        nc  = self.normalize_text(company)
        np_ = self.normalize_phone(phone)
        base = f"{nc}|{np_}"
        return hashlib.sha256(base.encode('utf-8')).hexdigest()[:16]

    def process_filemaker_data(self, df, job_id, output_filename):
        job_dir = self.base_dir / job_id
        job_dir.mkdir(exist_ok=True)

        original_path = job_dir / "fm_export.xlsx"
        df.to_excel(original_path, index=False)

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

        rowmap_data = []
        for idx, row in df.iterrows():
            company = row.get('顧客名', '') if '顧客名' in df.columns else row.get('社名', '')
            phone   = row.get('電話番号', '')
            row_key = self.create_row_key(company, phone)
            rowmap_data.append({
                'row_key': row_key,
                'company': company,
                'company_normalized': self.normalize_text(company),
                'phone': phone,
                'fm_id': row.get('IDの頭にID', ''),
                'index_in_fm': idx
            })

        rowmap_df = pd.DataFrame(rowmap_data)
        rowmap_df.to_csv(job_dir / "rowmap.csv", index=False)

        upload_path = job_dir / f"{output_filename}.csv"
        try:
            upload_df.to_csv(upload_path, index=False, encoding='shift_jis')
        except UnicodeEncodeError:
            upload_df.to_csv(upload_path, index=False, encoding='utf-8-sig')

        manifest = {
            'job_id': job_id,
            'created_at': datetime.now().isoformat(),
            'original_filename': output_filename,
            'total_rows': len(df),
            'files': {
                'fm_export': 'fm_export.xlsx',
                'upload': f'{output_filename}.csv',
                'rowmap': 'rowmap.csv'
            }
        }
        with open(job_dir / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        return {'job_id': job_id, 'upload_path': upload_path, 'total_rows': len(df), 'manifest': manifest}

    def analyze_call_results(self, df):
        df["電話番号"] = df["電話番号"].astype(str).str.replace(r'^\+81\s*', '0', regex=True)
        df["電話番号"] = df["電話番号"].str.replace(" ", "")

        def parse_duration(val):
            if pd.isna(val): return 0
            val = str(val).strip()
            if val in ["", "-", "nan"]: return 0
            parts = val.split(":")
            try:
                if len(parts) == 3:
                    h, m, s = map(int, parts); return h*3600+m*60+s
                elif len(parts) == 2:
                    m, s = map(int, parts); return m*60+s
                else:
                    return int(val)
            except Exception:
                return 0

        df["通話時間_num"] = df["通話時間"].apply(parse_duration)

        ng_words = [
            "断り","不要","必要ない","結構です","結構",
            "電話が終了","電話を切った","切断","応答なし","応答無し",
            "切られ","切られる","切った","通話が終了","会話が終了",
            "進展しない","通話を終了","進まなかった","切りました","断念",
            "終了","成立しなかった","切","進展はありま"
        ]

        for idx, row in df.iterrows():
            status   = str(row.get("ステータス", ""))
            result   = str(row.get("架電結果", "")) if pd.notna(row.get("架電結果")) else ""
            summary  = str(row.get("要約", ""))     if pd.notna(row.get("要約"))     else ""
            duration = row["通話時間_num"]

            if result.strip() not in ["", "nan"]:
                continue
            if status.strip() == "留守番電話":
                df.at[idx, "架電結果"] = "留守電"; continue
            if status.strip() in ["応答なし", "応答無し"]:
                df.at[idx, "架電結果"] = "留守"; continue
            if status.strip() == "獲得":
                df.at[idx, "架電結果"] = "AI電話APO"; continue
            if any(w in summary for w in ng_words):
                df.at[idx, "架電結果"] = "NG"; continue
            if pd.isna(duration) or duration == 0:
                df.at[idx, "架電結果"] = "留守"; continue
            if status.strip() == "自動音声":
                df.at[idx, "架電結果"] = "留守電"; continue
            if any(x in summary for x in ["応答なし", "応答無し"]):
                df.at[idx, "架電結果"] = "留守"; continue
            if any(x in summary for x in ["転送された", "了承しました", "転送されました"]):
                df.at[idx, "架電結果"] = "AI電話APO"; continue
            if pd.notna(duration) and duration > 0:
                df.at[idx, "架電結果"] = "NG"

        return df

    def merge_with_original(self, call_results_df, job_id):
        job_dir = self.base_dir / job_id
        with open(job_dir / "manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        rowmap_df   = pd.read_csv(job_dir / "rowmap.csv")
        original_df = pd.read_excel(job_dir / "fm_export.xlsx")

        call_results_df['社名_正規化'] = call_results_df['社名'].apply(self.normalize_text)

        has_call_time = '架電時刻' in call_results_df.columns
        if has_call_time:
            try:
                call_results_df['架電時刻_dt'] = pd.to_datetime(call_results_df['架電時刻'], errors='coerce')
                call_results_df['架電日']   = call_results_df['架電時刻_dt'].dt.strftime('%Y/%m/%d')
                call_results_df['架電時間'] = call_results_df['架電時刻_dt'].dt.strftime('%H:%M:%S')
                call_results_df = call_results_df.drop('架電時刻_dt', axis=1)
            except Exception:
                pass

        merged_df = pd.merge(
            call_results_df,
            rowmap_df[['company_normalized', 'fm_id', 'company']],
            left_on='社名_正規化', right_on='company_normalized', how='left'
        )

        if 'fm_id' in merged_df.columns and 'IDの頭にID' in original_df.columns:
            original_subset = original_df[['IDの頭にID', '住所統合', '最終トーク判定', '最終有効無効', '最終決済担当']].copy()
            original_subset = original_subset.rename(columns={'IDの頭にID': 'fm_id'})
            merged_df = pd.merge(merged_df, original_subset, on='fm_id', how='left')

        merged_df['row_key'] = merged_df.apply(
            lambda r: self.create_row_key(r.get('社名', ''), r.get('電話番号', '')), axis=1
        )

        if has_call_time and '架電日' in merged_df.columns:
            col_order = ['fm_id','社名','電話番号','架電日','架電時間','ステータス','架電結果','要約','通話時間',
                         '住所統合','最終トーク判定','最終有効無効','最終決済担当','row_key']
        else:
            col_order = ['fm_id','社名','電話番号','ステータス','架電結果','要約','通話時間',
                         '住所統合','最終トーク判定','最終有効無効','最終決済担当','row_key']

        available = [c for c in col_order if c in merged_df.columns]
        return merged_df[available]

    def calculate_statistics(self, df):
        def parse_duration(val):
            if pd.isna(val): return 0
            val = str(val).strip()
            if val in ["", "-", "nan"]: return 0
            parts = val.split(":")
            try:
                if len(parts) == 3:
                    h, m, s = map(int, parts); return h*3600+m*60+s
                elif len(parts) == 2:
                    m, s = map(int, parts); return m*60+s
                else:
                    return int(val)
            except Exception:
                return 0

        df["通話時間_sec"] = df["通話時間"].apply(parse_duration)
        total_calls    = len(df)
        result_counts  = df["架電結果"].value_counts()
        valid_calls    = df[~df["架電結果"].isin(["留守","留守番電話"])].shape[0]
        total_time_sec = int(df["通話時間_sec"].sum())
        total_time_str = str(timedelta(seconds=total_time_sec))
        transfer_calls = df[df["架電結果"].str.contains("APO", na=False)].shape[0]

        df["電話番号_str"] = df["電話番号"].astype(str).str.replace(r"\D", "", regex=True)
        invalid_numbers = df[~df["電話番号_str"].str.match(r"^0\d{9,10}$", na=False)].shape[0]

        error_calls = df[df[["ステータス","要約"]].astype(str).apply(
            lambda x: any("エラー" in v for v in x), axis=1
        )].shape[0]

        return {
            'total_calls': total_calls,
            'valid_calls': valid_calls,
            'total_time': total_time_str,
            'transfer_calls': transfer_calls,
            'invalid_numbers': invalid_numbers,
            'error_calls': error_calls,
            'result_counts': result_counts.to_dict()
        }


# ============================================================
# ダイヤルシフト リスト成形ロジック
# ============================================================
def process_dialshift_list(df: pd.DataFrame) -> pd.DataFrame:
    if "コール日時" in df.columns:
        call_datetime = pd.to_datetime(df["コール日時"], errors="coerce")
        loc = df.columns.get_loc("コール日時")
        df.insert(loc + 1, "コール日",   call_datetime.dt.strftime("%Y-%m-%d"))
        df.insert(loc + 2, "コール時間", call_datetime.dt.strftime("%H:%M:%S"))
        df = df.drop(columns=["コール日時"])

    if "コール結果" in df.columns:
        original_result = df["コール結果"].astype("string").str.strip().str.replace(" ", "\u3000", regex=False)

        drop_flags = {"\u8ee2\u9001\u3000\u304a\u984c\u6210\u7acb", "\u8ee2\u9001\u3000\u7d10\u3065\u3051",
                      "\u53d7\u96fb\u3000\u304a\u984c\u6210\u7acb", "\u53d7\u96fb\u3000\u7d10\u3065\u3051"}
        df = df[~original_result.isin(drop_flags)].copy()
        original_result = df["コール結果"].astype("string").str.strip().str.replace(" ", "\u3000", regex=False)

        conversion_map = {
            "AI終話":              "NG",
            "応答なし":            "留守",
            "AI対応不可":          "留守電",
            "AI同時接続":          "再コール・転送成功",
            "留守番電話":          "留守電",
            "コール結果記録中":    "再コール・転送成功",
            "手動受信_未対応":     "受電あり",
            "トスアップ応答前終了":"再コール・転送成功",
            "コール結果未登録":    "再コール・転送成功",
            "転送\u3000NG":        "NG",
            "転送\u3000再コール":  "再コール・転送成功",
            "転送\u3000アポ禁":    "アポ禁",
            "転送\u3000留守電":    "留守電",
            "受電\u3000NG":        "NG",
            "受電\u3000再コール":  "再コール",
            "受電\u3000アポ禁":    "アポ禁",
            "受電\u3000電話APO":   "受電電話APO",
            "受電\u3000留守電":    "留守電",
            "AIコールNG":          "NG",
            "AIホットリード":      "再コール・転送成功",
        }

        validity_map = {
            "AI終話":              "有効",
            "応答なし":            "無効",
            "AI対応不可":          "有効",
            "AI同時接続":          "有効",
            "留守番電話":          "有効",
            "コール結果記録中":    "有効",
            "手動受信_未対応":     "",
            "トスアップ応答前終了":"有効",
            "コール結果未登録":    "有効",
            "転送\u3000NG":        "有効",
            "転送\u3000再コール":  "有効",
            "転送\u3000アポ禁":    "有効",
            "転送\u3000留守電":    "有効",
            "受電\u3000NG":        "有効",
            "受電\u3000再コール":  "有効",
            "受電\u3000アポ禁":    "有効",
            "受電\u3000電話APO":   "有効",
            "受電\u3000留守電":    "有効",
            "AIコールNG":          "無効",
            "AIホットリード":      "有効",
        }

        df["コール結果"]   = original_result.map(conversion_map).fillna(original_result)
        df["有効無効判定"] = original_result.map(validity_map).fillna("")

    drop_columns = [
        "次回コール予定日時", "次回コール予定日", "次回コール予定日時 (AI)",
        "通話時間", "通話時間(秒)", "ステータス", "方向", "コール担当者",
        "コールリスト", "通話ID", "文字起こし", "住所", "住所統合",
    ]
    df = df.drop(columns=[c for c in drop_columns if c in df.columns])
    return df


# ============================================================
# セッション初期化
# ============================================================
def init_session():
    if 'jobs' not in st.session_state:
        hm = JobHistoryManager()
        st.session_state.jobs = hm.load_jobs()
    if 'history_manager' not in st.session_state:
        st.session_state.history_manager = JobHistoryManager()
    if 'page' not in st.session_state:
        st.session_state.page = 'home'


# ============================================================
# ページ：ホーム
# ============================================================
def page_home():
    st.markdown("""
    <div class="hero">
        <h1>📞 架電管理システム</h1>
        <p>ダイヤルシフト・AIテレアポ のリスト成形とファイルメーカー返送をワンストップで処理</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card-grid">
        <div class="func-card ds-card">
            <div class="badge">DIAL SHIFT</div>
            <div class="icon">📋</div>
            <h3>① ダイヤルシフト用<br>リスト成形</h3>
            <p>CSVをアップロードしてコール結果・有効無効判定を自動変換。不要列を削除してダウンロード。</p>
        </div>
        <div class="func-card ds-card">
            <div class="badge">DIAL SHIFT</div>
            <div class="icon">🔄</div>
            <h3>② ダイヤルシフト用<br>ファイルメーカー返送</h3>
            <p>成形済みデータをFileMakerの元データとマージして返送用Excelを生成。</p>
        </div>
        <div class="func-card ai-card">
            <div class="badge">AI TELEAPO</div>
            <div class="icon">🤖</div>
            <h3>③ AIテレアポ用<br>リスト成形</h3>
            <p>FileMakerデータをAIテレアポ投入用CSVに変換。社名・電話番号・住所を整形。</p>
        </div>
        <div class="func-card wip-card">
            <div class="badge">COMING SOON</div>
            <div class="icon">🚧</div>
            <h3>④ AIテレアポ用<br>ファイルメーカー返送</h3>
            <p>現在開発中です。もうしばらくお待ちください。</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info("👈 サイドバーのメニューから機能を選択してください")


# ============================================================
# ページ：① ダイヤルシフト リスト成形
# ============================================================
def page_ds_list():
    st.markdown("""
    <div class="page-header-ds">
        <div class="page-header-icon">📋</div>
        <div>
            <h2>ダイヤルシフト用 リスト成形</h2>
            <p>CSVをアップロード → コール結果変換・不要列削除 → ダウンロード</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="panel"><h4><span class="step-badge step-ds">1</span> CSVファイルをアップロード</h4>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "ダイヤルシフトからエクスポートしたCSVを選択",
            type=['csv'],
            key="ds_list_upload",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded:
            encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
            df = None
            used_enc = None
            raw = uploaded.read()
            for enc in encodings:
                try:
                    df = pd.read_csv(BytesIO(raw), encoding=enc)
                    used_enc = enc
                    break
                except Exception:
                    continue

            if df is None:
                st.error("❌ CSVを読み込めませんでした。文字コードを確認してください。")
                return

            st.markdown(f"""
            <div class="result-success">
                ✅ <strong>読み込み完了</strong>　{uploaded.name}　|　{len(df):,} 件　|　文字コード: {used_enc}
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📋 元データプレビュー（先頭10件）"):
                st.dataframe(df.head(10), use_container_width=True)

            st.markdown('<div class="panel"><h4><span class="step-badge step-ds">2</span> 成形処理を実行</h4>', unsafe_allow_html=True)
            if st.button("🔧 リスト成形を実行", type="primary", key="ds_list_run"):
                with st.spinner("処理中..."):
                    try:
                        result_df = process_dialshift_list(df.copy())

                        st.markdown(f"""
                        <div class="result-success">
                            ✅ <strong>成形完了</strong>　処理後: {len(result_df):,} 件（削除行: {len(df)-len(result_df):,} 件）
                        </div>
                        """, unsafe_allow_html=True)

                        if "コール結果" in result_df.columns:
                            dist = result_df["コール結果"].value_counts().reset_index()
                            dist.columns = ["コール結果", "件数"]
                            st.markdown("**📊 コール結果分布**")
                            st.dataframe(dist, use_container_width=True, hide_index=True)

                        with st.expander("📋 成形後データプレビュー（先頭10件）"):
                            st.dataframe(result_df.head(10), use_container_width=True)

                        base = uploaded.name.rsplit('.', 1)[0]
                        date_str = datetime.now().strftime("%Y%m%d")
                        out_name = f"{base}_{date_str}_formatted.csv"
                        csv_bytes = result_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

                        st.markdown("---")
                        st.download_button(
                            label="⬇️ 成形済みCSVをダウンロード",
                            data=csv_bytes,
                            file_name=out_name,
                            mime="text/csv",
                            key="ds_list_dl"
                        )

                    except Exception as e:
                        st.error(f"❌ 処理エラー: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="panel">
            <h4>📌 処理内容</h4>
            <p style="font-size:0.85rem;color:#475569;line-height:1.7;">
            ✔ コール日時 → コール日 / コール時間 に分割<br>
            ✔ コール結果を変換マップで置換<br>
            ✔ 有効無効判定を自動付与<br>
            ✔ 削除対象行（お題成立・紐づけ）を除外<br>
            ✔ 不要列（通話時間・住所など）を削除<br>
            ✔ UTF-8 BOM付きCSVで出力
            </p>
        </div>
        <div class="panel">
            <h4>📋 変換マップ（主要）</h4>
            <table style="font-size:0.78rem;width:100%;border-collapse:collapse;">
            <tr style="background:#1e3a8a;color:white;"><th style="padding:4px 6px;text-align:left;">元の値</th><th style="padding:4px 6px;text-align:left;">変換後</th></tr>
            <tr><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">AI終話</td><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">NG</td></tr>
            <tr><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">応答なし</td><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">留守</td></tr>
            <tr><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">AI対応不可</td><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">留守電</td></tr>
            <tr><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">留守番電話</td><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">留守電</td></tr>
            <tr><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">転送　NG</td><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">NG</td></tr>
            <tr><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">受電　電話APO</td><td style="padding:3px 6px;border-bottom:1px solid #e2e8f0;">受電電話APO</td></tr>
            <tr><td style="padding:3px 6px;">AIホットリード</td><td style="padding:3px 6px;">再コール・転送成功</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# ページ：② ダイヤルシフト FM返送
# ============================================================
def page_ds_fm():
    st.markdown("""
    <div class="page-header-ds">
        <div class="page-header-icon">🔄</div>
        <div>
            <h2>ダイヤルシフト用 ファイルメーカー返送</h2>
            <p>成形済みCSV × FileMaker元データ をマージして返送用Excelを生成</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="panel"><h4><span class="step-badge step-ds">1</span> FileMaker元データ（Excel）をアップロード</h4>', unsafe_allow_html=True)
        fm_file = st.file_uploader(
            "FileMakerからエクスポートしたExcelを選択",
            type=['xlsx', 'xls'],
            key="ds_fm_original",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4><span class="step-badge step-ds">2</span> 成形済みCSVをアップロード</h4>', unsafe_allow_html=True)
        result_file = st.file_uploader(
            "ダイヤルシフト成形済みCSVを選択",
            type=['csv'],
            key="ds_fm_result",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if fm_file and result_file:
            try:
                fm_df = pd.read_excel(fm_file)
                st.markdown(f"""
                <div class="result-success">
                    ✅ FM元データ読み込み完了　{fm_file.name}　|　{len(fm_df):,} 件
                </div>
                """, unsafe_allow_html=True)

                encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
                res_df = None
                raw = result_file.read()
                for enc in encodings:
                    try:
                        res_df = pd.read_csv(BytesIO(raw), encoding=enc)
                        break
                    except Exception:
                        continue

                if res_df is None:
                    st.error("❌ 成形済みCSVを読み込めませんでした。")
                    return

                st.markdown(f"""
                <div class="result-success">
                    ✅ 成形済みCSV読み込み完了　{result_file.name}　|　{len(res_df):,} 件
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="panel"><h4><span class="step-badge step-ds">3</span> マージキー設定</h4>', unsafe_allow_html=True)
                fm_cols  = list(fm_df.columns)
                res_cols = list(res_df.columns)

                c1, c2 = st.columns(2)
                with c1:
                    fm_key = st.selectbox(
                        "FM元データのキー列",
                        fm_cols,
                        index=fm_cols.index('IDの頭にID') if 'IDの頭にID' in fm_cols else 0,
                        key="ds_fm_key1"
                    )
                with c2:
                    default_res_key = next((c for c in ['電話番号','社名','顧客名'] if c in res_cols), res_cols[0])
                    res_key = st.selectbox(
                        "成形済みCSVのキー列",
                        res_cols,
                        index=res_cols.index(default_res_key),
                        key="ds_fm_key2"
                    )
                st.markdown('</div>', unsafe_allow_html=True)

                if st.button("🔄 マージ＆返送ファイル生成", type="primary", key="ds_fm_run"):
                    with st.spinner("マージ処理中..."):
                        try:
                            merged = pd.merge(fm_df, res_df, left_on=fm_key, right_on=res_key, how='left', suffixes=('_FM', '_結果'))
                            matched = merged[res_key].notna().sum() if res_key in merged.columns else len(merged)
                            match_rate = matched / len(merged) * 100 if len(merged) > 0 else 0

                            st.markdown(f"""
                            <div class="result-info">
                                📊 <strong>マージ完了</strong>　{len(merged):,} 件　|　マッチ率: {match_rate:.1f}%
                            </div>
                            """, unsafe_allow_html=True)

                            with st.expander("📋 マージ結果プレビュー（先頭10件）"):
                                st.dataframe(merged.head(10), use_container_width=True)

                            base = fm_file.name.rsplit('.', 1)[0]
                            date_str = datetime.now().strftime("%Y%m%d")
                            out_name = f"{base}_{date_str}_DS返送.xlsx"

                            buf = BytesIO()
                            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                                merged.to_excel(writer, index=False, sheet_name='返送データ')
                            buf.seek(0)

                            st.markdown("---")
                            st.download_button(
                                label="⬇️ 返送用Excelをダウンロード",
                                data=buf.getvalue(),
                                file_name=out_name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="ds_fm_dl"
                            )

                        except Exception as e:
                            st.error(f"❌ マージエラー: {e}")

            except Exception as e:
                st.error(f"❌ ファイル読み込みエラー: {e}")

        else:
            st.markdown("""
            <div class="result-warning">
                ⚠️ FM元データ（Excel）と成形済みCSVの両方をアップロードしてください
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="panel">
            <h4>📌 処理内容</h4>
            <p style="font-size:0.85rem;color:#475569;line-height:1.7;">
            ✔ FM元データ（Excel）と成形済みCSVをキー列でマージ<br>
            ✔ マッチ率を表示<br>
            ✔ 返送用Excelとして出力<br>
            ✔ キー列は自由に選択可能
            </p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# ページ：③ AIテレアポ リスト成形
# ============================================================
def page_ai_list():
    manager = AITeleapoManager()
    history_manager = st.session_state.history_manager

    st.markdown("""
    <div class="page-header-ai">
        <div class="page-header-icon">🤖</div>
        <div>
            <h2>AIテレアポ用 リスト成形</h2>
            <p>FileMakerデータ → AIテレアポ投入用CSV を生成（社名・電話番号・住所を整形）</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="panel"><h4><span class="step-badge step-ai">1</span> FileMakerデータ（Excel）をアップロード</h4>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "FileMakerから出力したExcelファイルを選択",
            type=['xlsx', 'xls'],
            key="ai_list_upload",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded:
            try:
                df = pd.read_excel(uploaded)
                st.markdown(f"""
                <div class="result-success">
                    ✅ <strong>読み込み完了</strong>　{uploaded.name}　|　{len(df):,} 件
                </div>
                """, unsafe_allow_html=True)

                with st.expander("📋 データプレビュー（先頭10件）"):
                    st.dataframe(df.head(10), use_container_width=True)

                st.markdown('<div class="panel"><h4><span class="step-badge step-ai">2</span> 出力設定</h4>', unsafe_allow_html=True)
                base = uploaded.name.rsplit('.', 1)[0]
                date_str = datetime.now().strftime("%Y%m%d")
                output_name = f"{base}_{date_str}_AIテレアポリスト"
                st.text_input("出力ファイル名（自動生成）", value=output_name, disabled=True, key="ai_list_outname")
                robot_count = st.selectbox("🤖 使用するロボット台数（レーン数）", [1, 2, 3, 4, 5], index=2, key="ai_list_robot")
                st.markdown('</div>', unsafe_allow_html=True)

                if st.button("🚀 リスト成形を実行", type="primary", key="ai_list_run"):
                    with st.spinner("処理中..."):
                        job_id = manager.generate_job_id()
                        result = manager.process_filemaker_data(df, job_id, output_name)

                        job_info = {
                            'job_id': job_id,
                            'created_at': datetime.now(),
                            'filename': uploaded.name,
                            'output_name': output_name,
                            'robot_count': robot_count,
                            'total_rows': result['total_rows'],
                            'status': 'created',
                            'type': 'ai_list'
                        }
                        st.session_state.jobs.append(job_info)
                        history_manager.save_jobs(st.session_state.jobs)

                        st.markdown(f"""
                        <div class="result-success">
                            ✅ <strong>ジョブ作成完了</strong><br>
                            ジョブID: {job_id}　|　処理件数: {result['total_rows']:,} 件
                        </div>
                        """, unsafe_allow_html=True)

                        with open(result['upload_path'], 'rb') as f:
                            csv_data = f.read()

                        st.markdown("---")
                        st.download_button(
                            label="⬇️ AIテレアポ用CSVをダウンロード",
                            data=csv_data,
                            file_name=f"{output_name}.csv",
                            mime="text/csv",
                            key="ai_list_dl"
                        )

            except Exception as e:
                st.error(f"❌ ファイル処理エラー: {e}")

    with col2:
        st.markdown("""
        <div class="panel">
            <h4>📌 処理内容</h4>
            <p style="font-size:0.85rem;color:#475569;line-height:1.7;">
            ✔ 顧客名 → 社名 に列名変換<br>
            ✔ 社名を50文字でカット<br>
            ✔ 社名・電話番号・住所統合を抽出<br>
            ✔ IDの頭にID列を付与<br>
            ✔ rowmap（マージ用）を自動生成・保存<br>
            ✔ Shift-JIS / UTF-8 BOMで出力
            </p>
        </div>
        """, unsafe_allow_html=True)

        ai_jobs = [j for j in st.session_state.jobs if j.get('type') == 'ai_list']
        if ai_jobs:
            st.markdown('<div class="panel"><h4>📂 最近のジョブ</h4>', unsafe_allow_html=True)
            for job in reversed(ai_jobs[-3:]):
                created = job['created_at']
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                st.markdown(f"""
                <div class="job-card">
                    <div class="job-card-title">🎯 {job['job_id']}</div>
                    <div class="job-card-meta">{created.strftime('%Y-%m-%d %H:%M')}　|　{job['total_rows']:,}件</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# ページ：④ AIテレアポ FM返送（工事中）
# ============================================================
def page_ai_fm():
    st.markdown("""
    <div class="page-header-ai">
        <div class="page-header-icon">🚧</div>
        <div>
            <h2>AIテレアポ用 ファイルメーカー返送</h2>
            <p>現在開発中です</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="wip-banner">
        <div class="wip-icon">🚧</div>
        <h2>工事中</h2>
        <p>AIテレアポ用ファイルメーカー返送機能は現在開発中です。<br>
        完成次第、こちらのページでご利用いただけます。<br><br>
        <strong>現在ご利用可能な機能</strong><br>
        ① ダイヤルシフト用リスト成形<br>
        ② ダイヤルシフト用FM返送<br>
        ③ AIテレアポ用リスト成形</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ページ：ジョブ履歴
# ============================================================
def page_history():
    st.markdown("""
    <div class="page-header-ai">
        <div class="page-header-icon">📂</div>
        <div>
            <h2>ジョブ履歴</h2>
            <p>AIテレアポ用リスト成形で作成したジョブの一覧</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    history_manager = st.session_state.history_manager

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 履歴を再読み込み", key="hist_reload"):
            st.session_state.jobs = history_manager.load_jobs()
            st.success("✅ 再読み込みしました")
    with c2:
        if st.button("🗑️ 履歴をクリア", key="hist_clear"):
            st.session_state.jobs = []
            history_manager.clear_jobs()
            st.success("✅ クリアしました")

    if st.session_state.jobs:
        for job in reversed(st.session_state.jobs):
            created = job['created_at']
            if isinstance(created, str):
                created = datetime.fromisoformat(created)
            st.markdown(f"""
            <div class="job-card">
                <div class="job-card-title">🎯 {job['job_id']}　—　{job['output_name']}</div>
                <div class="job-card-meta">
                    📅 {created.strftime('%Y-%m-%d %H:%M:%S')}　|　
                    📄 {job['filename']}　|　
                    📊 {job['total_rows']:,} 件　|　
                    🤖 {job.get('robot_count','—')} レーン
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="result-info">
            📝 ジョブ履歴がありません。AIテレアポ用リスト成形からジョブを作成してください。
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# サイドバー
# ============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div class="logo-icon">📞</div>
            <h3>架電管理システム</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="nav-section-title">🔵 ダイヤルシフト</p>', unsafe_allow_html=True)
        if st.button("📋　リスト成形", key="nav_ds_list", use_container_width=True):
            st.session_state.page = 'ds_list'
            st.rerun()
        if st.button("🔄　ファイルメーカー返送", key="nav_ds_fm", use_container_width=True):
            st.session_state.page = 'ds_fm'
            st.rerun()

        st.markdown('<p class="nav-section-title">🩵 AIテレアポ</p>', unsafe_allow_html=True)
        if st.button("🤖　リスト成形", key="nav_ai_list", use_container_width=True):
            st.session_state.page = 'ai_list'
            st.rerun()
        if st.button("🚧　ファイルメーカー返送（工事中）", key="nav_ai_fm", use_container_width=True):
            st.session_state.page = 'ai_fm'
            st.rerun()

        st.markdown('<p class="nav-section-title">📂 管理</p>', unsafe_allow_html=True)
        if st.button("📂　ジョブ履歴", key="nav_history", use_container_width=True):
            st.session_state.page = 'history'
            st.rerun()
        if st.button("🏠　ホーム", key="nav_home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <p style="font-size:0.75rem;color:#94a3b8;text-align:center;">
        v9.0.0　|　ジョブ数: {len(st.session_state.get('jobs', []))}
        </p>
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
    elif page == 'history':
        page_history()
    else:
        page_home()


if __name__ == "__main__":
    main()
