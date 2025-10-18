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
    page_title="AIテレアポ管理システム",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 白背景で見やすい青ベースのカスタムCSS
st.markdown("""
<style>
    /* 全体の背景を白に */
    .stApp {
        background-color: #ffffff;
        color: #333333;
    }
    
    /* メインコンテンツエリア */
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        max-width: 1200px;
    }
    
    /* サイドバー */
    .css-1d391kg {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* ヘッダー */
    .main-header {
        font-size: 2.5rem;
        color: #1e40af;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        padding: 1rem 0;
        border-bottom: 3px solid #3b82f6;
    }
    
    /* ジョブカード - 清潔感のあるデザイン */
    .job-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        border-color: #3b82f6;
    }
    
    .job-card-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .job-info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .job-info-item {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        border: 1px solid #e2e8f0;
    }
    
    .job-info-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    
    .job-info-value {
        font-size: 1rem;
        color: #1e293b;
        font-weight: 600;
    }
    
    /* 成功ボックス */
    .success-box {
        background: #f0fdf4;
        border: 2px solid #22c55e;
        color: #15803d;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(34, 197, 94, 0.1);
    }
    
    .success-box h4 {
        color: #15803d;
        margin-bottom: 0.5rem;
    }
    
    /* 警告ボックス */
    .warning-box {
        background: #fffbeb;
        border: 2px solid #f59e0b;
        color: #d97706;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
    }
    
    .warning-box h4 {
        color: #d97706;
        margin-bottom: 0.5rem;
    }
    
    /* 情報ボックス */
    .info-box {
        background: #eff6ff;
        border: 2px solid #3b82f6;
        color: #1d4ed8;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
    }
    
    .info-box h4 {
        color: #1d4ed8;
        margin-bottom: 0.5rem;
    }
    
    /* メトリクスカード */
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        border-color: #3b82f6;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.3rem;
    }
    
    /* サイドバーセクション */
    .sidebar-section {
        background: #ffffff;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .sidebar-section h4 {
        color: #1e40af;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .sidebar-section p, .sidebar-section li {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .sidebar-section ol li {
        margin-bottom: 0.5rem;
    }
    
    /* ステータスバッジ */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-created {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #22c55e;
    }
    
    .status-processing {
        background-color: #fef3c7;
        color: #d97706;
        border: 1px solid #f59e0b;
    }
    
    .status-completed {
        background-color: #dbeafe;
        color: #1d4ed8;
        border: 1px solid #3b82f6;
    }
    
    /* 小さなアイコン */
    .small-icon {
        font-size: 0.8rem;
        margin-right: 0.2rem;
    }
    
    /* セクションヘッダー */
    .section-header {
        color: #1e40af;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Streamlitコンポーネントのスタイル調整 */
    .stSelectbox > div > div {
        border: 2px solid #e2e8f0;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        border: none;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* ファイルアップローダー */
    .stFileUploader > div {
        border: 2px dashed #3b82f6;
        border-radius: 12px;
        background: #f8fafc;
        padding: 2rem;
        text-align: center;
    }
    
    .stFileUploader > div:hover {
        background: #eff6ff;
        border-color: #1d4ed8;
    }
    
    /* データフレーム */
    .stDataFrame {
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* エキスパンダー */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        color: #1e40af;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #eff6ff;
        border-color: #3b82f6;
    }
    
    /* ダウンロードボタンの強調 */
    .download-section {
        background: #f0fdf4;
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* ダウンロードボタンのカスタムスタイル */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 1rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(34, 197, 94, 0.2) !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(34, 197, 94, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ファイルベースのジョブ履歴管理
class JobHistoryManager:
    def __init__(self):
        self.history_file = Path("job_history.json")
        self.download_cache_dir = Path("download_cache")
        self.download_cache_dir.mkdir(exist_ok=True)
    
    def save_jobs(self, jobs):
        """ジョブ履歴をファイルに保存"""
        try:
            # datetime オブジェクトを文字列に変換
            serializable_jobs = []
            for job in jobs:
                job_copy = job.copy()
                if isinstance(job_copy.get('created_at'), datetime):
                    job_copy['created_at'] = job_copy['created_at'].isoformat()
                serializable_jobs.append(job_copy)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_jobs, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"ジョブ履歴保存エラー: {str(e)}")
            return False
    
    def load_jobs(self):
        """ジョブ履歴をファイルから読み込み"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                
                # 文字列をdatetimeオブジェクトに変換
                for job in jobs:
                    if isinstance(job.get('created_at'), str):
                        try:
                            job['created_at'] = datetime.fromisoformat(job['created_at'])
                        except:
                            job['created_at'] = datetime.now()
                
                return jobs
            return []
        except Exception as e:
            st.error(f"ジョブ履歴読み込みエラー: {str(e)}")
            return []
    
    def clear_jobs(self):
        """ジョブ履歴をクリア"""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            return True
        except Exception as e:
            st.error(f"ジョブ履歴クリアエラー: {str(e)}")
            return False
    
    def save_download_file(self, file_id, data, filename):
        """ダウンロード用ファイルをキャッシュに保存"""
        try:
            cache_file = self.download_cache_dir / f"{file_id}.pkl"
            cache_data = {
                'data': data,
                'filename': filename,
                'created_at': datetime.now().isoformat()
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            return True
        except Exception as e:
            st.error(f"ダウンロードファイル保存エラー: {str(e)}")
            return False
    
    def get_download_file(self, file_id):
        """ダウンロード用ファイルをキャッシュから取得"""
        try:
            cache_file = self.download_cache_dir / f"{file_id}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                return cache_data
            return None
        except Exception as e:
            st.error(f"ダウンロードファイル取得エラー: {str(e)}")
            return None

# セッション状態の初期化
def initialize_session_state():
    """セッション状態を初期化"""
    if 'jobs' not in st.session_state:
        # ファイルからジョブ履歴を読み込み
        history_manager = JobHistoryManager()
        st.session_state.jobs = history_manager.load_jobs()
    
    if 'current_job' not in st.session_state:
        st.session_state.current_job = None
    
    if 'history_manager' not in st.session_state:
        st.session_state.history_manager = JobHistoryManager()

class AITeleapoManager:
    def __init__(self):
        self.base_dir = Path("teleapo_jobs")
        self.base_dir.mkdir(exist_ok=True)
        
    def generate_job_id(self):
        """ジョブIDを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:5].upper()
        return f"{timestamp}_{random_suffix}"
    
    def normalize_phone(self, phone_str):
        """電話番号を正規化（+81形式を0始まりに変換）"""
        if pd.isna(phone_str):
            return ""
        phone_str = str(phone_str).replace("+81", "0").replace(" ", "").replace("-", "")
        return re.sub(r'\D', '', phone_str)
    
    def normalize_text(self, text):
        """テキストを正規化"""
        if pd.isna(text):
            return ""
        return str(text).strip()
    
    def create_row_key(self, company, phone):
        """行指紋を作成（社名ベース）"""
        # 社名を正規化してキーとして使用
        normalized_company = self.normalize_text(company)
        normalized_phone = self.normalize_phone(phone)
        base = f"{normalized_company}|{normalized_phone}"
        return hashlib.sha256(base.encode('utf-8')).hexdigest()[:16]
    
    def process_filemaker_data(self, df, job_id, output_filename):
        """FileMakerデータを処理"""
        job_dir = self.base_dir / job_id
        job_dir.mkdir(exist_ok=True)
        
        # 元データを保存
        original_path = job_dir / "fm_export.xlsx"
        df.to_excel(original_path, index=False)
        
        # AIテレアポ用にデータを変換
        upload_df = df.copy()
        if '顧客名' in upload_df.columns:
            upload_df = upload_df.rename(columns={'顧客名': '社名'})
        
        # 必要な列のみ抽出（AIテレアポ用）
        required_columns = ['社名', '電話番号', '住所統合']
        available_columns = [col for col in required_columns if col in upload_df.columns]
        
        if available_columns:
            upload_df = upload_df[available_columns].copy()
        
        # 社名を50文字でカット
        if '社名' in upload_df.columns:
            upload_df['社名'] = upload_df['社名'].astype(str).str[:50]
        
        # 行指紋を作成してrowmapを生成(社名ベース)
        rowmap_data = []
        for idx, row in df.iterrows():
            company = row.get('顧客名', '') if '顧客名' in df.columns else row.get('社名', '')
            phone = row.get('電話番号', '')
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
        rowmap_path = job_dir / "rowmap.csv"
        rowmap_df.to_csv(rowmap_path, index=False)
        
        # アップロード用CSVを保存（UTF-8 with BOM）
        upload_path = job_dir / f"{output_filename}.csv"
        try:
            # まずShift-JISを試す
            upload_df.to_csv(upload_path, index=False, encoding='shift_jis')
        except UnicodeEncodeError:
            # Shift-JISで保存できない場合はUTF-8 with BOMを使用
            upload_df.to_csv(upload_path, index=False, encoding='utf-8-sig')
        
        # マニフェストを作成
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
        
        manifest_path = job_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        return {
            'job_id': job_id,
            'upload_path': upload_path,
            'total_rows': len(df),
            'manifest': manifest
        }
    
    def analyze_call_results(self, df):
        """通話結果を分析"""
        # 電話番号を正規化
        df["電話番号"] = df["電話番号"].astype(str).str.replace(r'^\+81\s*', '0', regex=True)
        df["電話番号"] = df["電話番号"].str.replace(" ", "")
        
        # 通話時間を数値化
        df["通話時間_num"] = pd.to_numeric(df["通話時間"], errors="coerce")
        
        # 断り・終了系ワード
        ng_words = [
            "断り", "不要", "必要ない", "結構です", "結構",
            "電話が終了", "電話を切った", "切断", "応答なし", "応答無し",
            "切られ", "切られる", "切った", "通話が終了", "会話が終了",
            "進展しない", "通話を終了", "進まなかった", "切りました", "断念",
            "終了", "成立しなかった", "切", "進展はありま"
        ]
        
        # ステータス分類
        for idx, row in df.iterrows():
            status = str(row["ステータス"])
            result = str(row["架電結果"]) if pd.notna(row["架電結果"]) else ""
            summary = str(row["要約"]) if pd.notna(row["要約"]) else ""
            duration = row["通話時間_num"]
            
            # 既に結果が入っている場合はスキップ
            if result.strip() != "" and result.strip() != "nan":
                continue
            
            # 留守番電話 → 留守電
            if status.strip() == "留守番電話":
                df.at[idx, "架電結果"] = "留守電"
                continue
            
            # 応答なし → 留守
            if status.strip() in ["応答なし", "応答無し"]:
                df.at[idx, "架電結果"] = "留守"
                continue
            
            # 獲得 → AI電話APO
            if status.strip() == "獲得":
                df.at[idx, "架電結果"] = "AI電話APO"
                continue
            
            # 要約に断りワードが含まれる → NG
            if any(word in summary for word in ng_words):
                df.at[idx, "架電結果"] = "NG"
                continue
            
            # 通話時間が0 → 留守
            if duration == 0:
                df.at[idx, "架電結果"] = "留守"
                continue
            
            # ステータスが自動音声 → 留守電
            if status.strip() == "自動音声":
                df.at[idx, "架電結果"] = "留守電"
                continue
            
            # 要約に「応答なし」 → 留守
            if any(x in summary for x in ["応答なし", "応答無し"]):
                df.at[idx, "架電結果"] = "留守"
                continue
            
            # 要約に「転送」や「了承しました」など → 電話APO
            if any(x in summary for x in ["転送された", "了承しました", "転送されました"]):
                df.at[idx, "架電結果"] = "AI電話APO"
                continue
            
            # 通話時間あり & 転送でない → NG
            if pd.notna(duration) and duration > 0 and not any(x in summary for x in ["転送"]):
                df.at[idx, "架電結果"] = "NG"
        
        return df
    
    def merge_with_original(self, call_results_df, job_id):
        """元データとマージ（社名ベース）"""
        job_dir = self.base_dir / job_id
        
        # マニフェストを読み込み
        manifest_path = job_dir / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # rowmapを読み込み
        rowmap_path = job_dir / "rowmap.csv"
        rowmap_df = pd.read_csv(rowmap_path)
        
        # 元データを読み込み
        original_path = job_dir / "fm_export.xlsx"
        original_df = pd.read_excel(original_path)
        
        # 通話結果の社名を正規化
        call_results_df['社名_正規化'] = call_results_df['社名'].apply(self.normalize_text)
        
        # 架電時刻列を保持（存在する場合）
        has_call_time = '架電時刻' in call_results_df.columns
        
        # 架電時刻を日付と時間に分割
        if has_call_time:
            try:
                # 架電時刻を日時型に変換
                call_results_df['架電時刻_dt'] = pd.to_datetime(call_results_df['架電時刻'], errors='coerce')
                # 日付列を作成（YYYY/MM/DD形式）
                call_results_df['架電日'] = call_results_df['架電時刻_dt'].dt.strftime('%Y/%m/%d')
                # 時間列を作成（HH:MM:SS形式）
                call_results_df['架電時間'] = call_results_df['架電時刻_dt'].dt.strftime('%H:%M:%S')
                # 一時列を削除
                call_results_df = call_results_df.drop('架電時刻_dt', axis=1)
            except Exception as e:
                # エラーが発生した場合は元の架電時刻をそのまま使用
                pass
        
        # 社名ベースでマージ
        merged_df = pd.merge(
            call_results_df, 
            rowmap_df[['company_normalized', 'fm_id', 'company']], 
            left_on='社名_正規化', 
            right_on='company_normalized', 
            how='left'
        )
        
        # 元データの他の列も結合（IDをキーに）
        if 'fm_id' in merged_df.columns and 'IDの頭にID' in original_df.columns:
            # FileMakerのIDでさらに詳細情報を結合
            original_subset = original_df[['IDの頭にID', '住所統合', '最終トーク判定', '最終有効無効', '最終決済担当']].copy()
            original_subset = original_subset.rename(columns={'IDの頭にID': 'fm_id'})
            merged_df = pd.merge(merged_df, original_subset, on='fm_id', how='left')
        
        # 通話結果に行指紋を追加
        merged_df['row_key'] = merged_df.apply(
            lambda row: self.create_row_key(row.get('社名', ''), row.get('電話番号', '')), 
            axis=1
        )
        
        # 列の順序を整理（架電日・架電時間を含める）
        if has_call_time and '架電日' in merged_df.columns and '架電時間' in merged_df.columns:
            column_order = ['fm_id', '社名', '電話番号', '架電日', '架電時間', 'ステータス', '架電結果', '要約', '通話時間', 
                           '住所統合', '最終トーク判定', '最終有効無効', '最終決済担当', 'row_key']
        elif has_call_time:
            # 分割できなかった場合は元の架電時刻を使用
            column_order = ['fm_id', '社名', '電話番号', '架電時刻', 'ステータス', '架電結果', '要約', '通話時間', 
                           '住所統合', '最終トーク判定', '最終有効無効', '最終決済担当', 'row_key']
        else:
            column_order = ['fm_id', '社名', '電話番号', 'ステータス', '架電結果', '要約', '通話時間', 
                           '住所統合', '最終トーク判定', '最終有効無効', '最終決済担弰', 'row_key']
        
        # 存在する列のみを選択
        available_columns = [col for col in column_order if col in merged_df.columns]
        merged_df = merged_df[available_columns]
        
        return merged_df
    
    def calculate_statistics(self, df):
        """統計を計算"""
        def parse_duration(val):
            if pd.isna(val):
                return 0
            val = str(val).strip()
            if val in ["", "-", "nan"]:
                return 0
            parts = val.split(":")
            try:
                if len(parts) == 3:  # hh:mm:ss
                    h, m, s = map(int, parts)
                    return h*3600 + m*60 + s
                elif len(parts) == 2:  # mm:ss
                    m, s = map(int, parts)
                    return m*60 + s
                else:
                    return int(val)  # 秒数
            except:
                return 0
        
        # 通話時間を秒に変換
        df["通話時間_sec"] = df["通話時間"].apply(parse_duration)
        
        # 統計計算
        total_calls = len(df)
        result_counts = df["架電結果"].value_counts()
        valid_calls = df[~df["架電結果"].isin(["留守", "留守番電話"])].shape[0]
        total_time_sec = int(df["通話時間_sec"].sum())
        total_time_str = str(timedelta(seconds=total_time_sec))
        transfer_calls = df[df["架電結果"].str.contains("APO", na=False)].shape[0]
        
        # 無効番号
        df["電話番号_str"] = df["電話番号"].astype(str).str.replace(r"\D", "", regex=True)
        invalid_numbers = df[~df["電話番号_str"].str.match(r"^0\d{9,10}$", na=False)].shape[0]
        
        # エラー件数
        error_calls = df[df[["ステータス", "要約"]].astype(str).apply(
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

# 改良されたジョブカード表示関数
def display_job_card(job):
    """見やすいジョブカードを表示"""
    status_class = f"status-{job.get('status', 'created')}"
    created_at = job['created_at']
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    st.markdown(f"""
    <div class="job-card">
        <div class="job-card-header">
            <span>🎯 {job['job_id']} - {job['output_name']}</span>
            <span class="status-badge {status_class}">
                <span class="small-icon">●</span> {job['status']}
            </span>
        </div>
        <div class="job-info-grid">
            <div class="job-info-item">
                <div class="job-info-label">
                    <span class="small-icon">📅</span> 作成日時
                </div>
                <div class="job-info-value">{created_at.strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <div class="job-info-item">
                <div class="job-info-label">
                    <span class="small-icon">📄</span> 元ファイル
                </div>
                <div class="job-info-value">{job['filename']}</div>
            </div>
            <div class="job-info-item">
                <div class="job-info-label">
                    <span class="small-icon">🤖</span> レーン
                </div>
                <div class="job-info-value">{job['robot_count']} 番</div>
            </div>
            <div class="job-info-item">
                <div class="job-info-label">
                    <span class="small-icon">📊</span> 処理件数
                </div>
                <div class="job-info-value">{job['total_rows']:,} 件</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 統計メトリクス表示関数
def display_metrics(stats):
    """統計メトリクスを表示"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_calls']:,}</div>
            <div class="metric-label">
                <span class="small-icon">📞</span> 総架電数
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['valid_calls']:,}</div>
            <div class="metric-label">
                <span class="small-icon">✅</span> 有効通話
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['transfer_calls']:,}</div>
            <div class="metric-label">
                <span class="small-icon">🎯</span> APO獲得
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        apo_rate = (stats['transfer_calls'] / stats['valid_calls'] * 100) if stats['valid_calls'] > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{apo_rate:.1f}%</div>
            <div class="metric-label">
                <span class="small-icon">📈</span> APO率
            </div>
        </div>
        """, unsafe_allow_html=True)

# メインアプリケーション
def main():
    # セッション状態の初期化
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">📞 AIテレアポ管理システム</h1>', unsafe_allow_html=True)
    
    manager = AITeleapoManager()
    history_manager = st.session_state.history_manager
    
    # サイドバー
    st.sidebar.title("🎛️ 操作メニュー")
    
    # システム情報を表示
    st.sidebar.markdown(f"""
    <div class="sidebar-section">
        <h4><span class="small-icon">📊</span> システム情報</h4>
        <p><strong>作成済みジョブ数:</strong> {len(st.session_state.jobs)}</p>
        <p><strong>保存場所:</strong> {manager.base_dir.name}/</p>


    </div>
    """, unsafe_allow_html=True)
    
    menu = st.sidebar.selectbox(
        "機能を選択",
        ["📤 新規ジョブ作成", "📥 結果分析", "📊 ジョブ履歴", "⚙️ 設定"]
    )
    
    if menu == "📤 新規ジョブ作成":
        st.markdown('<h2 class="section-header"><span class="small-icon">📤</span> 新規ジョブ作成</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📁 FileMakerデータのアップロード")
            uploaded_file = st.file_uploader(
                "Excelファイルをアップロードしてください",
                type=['xlsx', 'xls'],
                help="FileMakerから出力したExcelファイルを選択してください"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_excel(uploaded_file)
                    st.markdown(f"""
                    <div class="success-box">
                        <h4>✅ ファイル読み込み完了</h4>
                        <p><strong>ファイル名:</strong> {uploaded_file.name}</p>
                        <p><strong>データ件数:</strong> {len(df):,} 件</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # データプレビュー
                    with st.expander("📋 データプレビュー"):
                        st.dataframe(df.head(10), use_container_width=True)
                    
                    # 出力ファイル名の指定（自動生成）
                    st.subheader("📝 出力設定")
                    # 元ファイル名から拡張子を除去
                    base_filename = uploaded_file.name.rsplit('.', 1)[0]
                    # 日付を追加
                    date_str = datetime.now().strftime("%Y%m%d")
                    # 自動生成されたファイル名を表示
                    output_name = f"{base_filename}_{date_str}_AIテレアポリスト"
                    st.text_input(
                        "出力ファイル名",
                        value=output_name,
                        disabled=True,
                        help="元ファイル名+日付+AIテレアポリストで自動生成されます"
                    )
                    
                    # ロボット台数選択
                    robot_count = st.selectbox(
                        "🤖 使用するロボット台数",
                        [1, 2, 3, 4, 5],
                        index=2,
                        help="同時に使用するAIテレアポロボットの台数"
                    )
                    
                    if st.button("🚀 ジョブを作成", type="primary"):
                        with st.spinner("ジョブを作成中..."):
                            job_id = manager.generate_job_id()
                            result = manager.process_filemaker_data(df, job_id, output_name)
                            
                            # セッション状態に保存
                            job_info = {
                                'job_id': job_id,
                                'created_at': datetime.now(),
                                'filename': uploaded_file.name,
                                'output_name': output_name,
                                'robot_count': robot_count,
                                'total_rows': result['total_rows'],
                                'status': 'created'
                            }
                            st.session_state.jobs.append(job_info)
                            
                            # ファイルに保存
                            history_manager.save_jobs(st.session_state.jobs)
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <h4>✅ ジョブ作成完了</h4>
                                <p><strong>ジョブID:</strong> {job_id}</p>
                                <p><strong>処理件数:</strong> {result['total_rows']:,} 件</p>
                                <p><strong>アップロード用ファイル:</strong> {result['upload_path']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # ダウンロードボタン
                            with open(result['upload_path'], 'rb') as f:
                                st.download_button(
                                    label="📤 AIテレアポ用CSVをダウンロード",
                                    data=f.read(),
                                    file_name=f"{output_name}.csv",
                                    mime="text/csv",
                                    type="primary"
                                )
                
                except Exception as e:
                    st.error(f"❌ ファイル処理エラー: {str(e)}")
        
        with col2:
            st.markdown("""
            <div class="sidebar-section">
                <h4><span class="small-icon">📋</span> 作成の流れ</h4>
                <ol>
                    <li><strong><span class="small-icon">📤</span> 新規ジョブ作成</strong><br>FileMakerから出力したExcelファイルを選択</li>
                    <li><strong><span class="small-icon">📤</span> 結果分析</strong><br>AIテレアポ結果の分析&ファイルメーカー返送用データ作成</li>
                    <li><strong><span class="small-icon">📊</span> ジョブ履歴</strong><br>保管されているファイルメーカーデータの管理</li>
                    <li><strong><span class="small-icon">⚙️</span> 設定</strong><br>ジョブの削除&再読み込み</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    elif menu == "📥 結果分析":
        st.markdown('<h2 class="section-header"><span class="small-icon">📥</span> 結果分析</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 通話結果の分析")
            
            # ジョブ選択
            if st.session_state.jobs:
                job_options = [f"{job['job_id']} - {job['output_name']}" for job in st.session_state.jobs]
                selected_job_str = st.selectbox("分析対象のジョブを選択", job_options)
                selected_job_id = selected_job_str.split(" - ")[0]
            else:
                st.markdown("""
                <div class="warning-box">
                    <h4>⚠️ ジョブが見つかりません</h4>
                    <p>作成されたジョブがありません。まず新規ジョブを作成してください。</p>
                </div>
                """, unsafe_allow_html=True)
                selected_job_id = None
            
            # 結果ファイルのアップロード
            results_file = st.file_uploader(
                "AIテレアポの結果CSVをアップロードしてください",
                type=['csv'],
                help="AIテレアポシステムからダウンロードした結果CSVファイル"
            )
            
            if results_file and selected_job_id:
                try:
                    # CSVファイルを読み込み（エンコーディング自動判定）
                    try:
                        df = pd.read_csv(results_file, encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            df = pd.read_csv(results_file, encoding='shift_jis')
                        except UnicodeDecodeError:
                            df = pd.read_csv(results_file, encoding='cp932')
                    
                    st.success(f"✅ ファイル読み込み完了: {results_file.name} ({len(df):,} 件)")
                    
                    # データプレビュー
                    with st.expander("📋 結果データプレビュー"):
                        st.dataframe(df.head(10), use_container_width=True)
                    
                    if st.button("🔍 結果を分析", type="primary"):
                        with st.spinner("結果を分析中..."):
                            # 通話結果を分析
                            analyzed_df = manager.analyze_call_results(df)
                            
                            # 統計を計算
                            stats = manager.calculate_statistics(analyzed_df)
                            
                            st.subheader("📊 分析結果")
                            
                            # 改良されたメトリクス表示
                            display_metrics(stats)
                            
                            # 詳細統計
                            st.subheader("📈 詳細統計")
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-value">{stats['total_time']}</div>
                                    <div class="metric-label">
                                        <span class="small-icon">⏱️</span> 総通話時間
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_b:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-value">{stats['invalid_numbers']}</div>
                                    <div class="metric-label">
                                        <span class="small-icon">❌</span> 無効番号
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_c:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-value">{stats['error_calls']}</div>
                                    <div class="metric-label">
                                        <span class="small-icon">⚠️</span> エラー件数
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # 結果分布
                            st.subheader("📊 架電結果分布")
                            result_df = pd.DataFrame(list(stats['result_counts'].items()), 
                                                   columns=['結果', '件数'])
                            st.dataframe(result_df, use_container_width=True)
                            
                            # 元データとマージ（社名ベース）
                            merged_df = manager.merge_with_original(analyzed_df, selected_job_id)
                            
                            # マージ結果の確認
                            st.subheader("🔗 マージ結果")
                            matched_count = merged_df['fm_id'].notna().sum()
                            match_rate = (matched_count / len(merged_df) * 100) if len(merged_df) > 0 else 0
                            
                            st.markdown(f"""
                            <div class="info-box">
                                <h4><span class="small-icon">📊</span> マッチング結果</h4>
                                <p><strong>マッチした件数:</strong> {matched_count:,} / {len(merged_df):,} 件</p>
                                <p><strong>マッチ率:</strong> {match_rate:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 出力ファイル名の指定（自動生成）
                            st.subheader("💾 結果保存")
                            # 選択されたジョブの元ファイル名を取得
                            selected_job = next((job for job in st.session_state.jobs if job['job_id'] == selected_job_id), None)
                            if selected_job:
                                base_filename = selected_job['filename'].rsplit('.', 1)[0]
                                date_str = datetime.now().strftime("%Y%m%d")
                                output_filename = f"{base_filename}_{date_str}_結果"
                            else:
                                output_filename = f"結果_{selected_job_id}"
                            
                            st.text_input(
                                "出力ファイル名",
                                value=output_filename,
                                disabled=True,
                                help="元ファイル名+日付+結果で自動生成されます"
                            )
                            
                            # 修正版：結果を保存ボタンをクリックしたら即座に自動ダウンロード
                            final_filename = f"{output_filename}.xlsx"
                            
                            # メモリ上でExcelファイルを作成
                            buffer = BytesIO()
                            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                merged_df.to_excel(writer, index=False, sheet_name='分析結果')
                            buffer.seek(0)
                            excel_data = buffer.getvalue()
                            
                            # 自動ダウンロード機能付きボタン
                            st.download_button(
                                label="💾 結果を保存",
                                data=excel_data,
                                file_name=final_filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"auto_download_{selected_job_id}",
                                type="primary",
                                help="クリックすると即座にExcelファイルがダウンロードされます"
                            )
                            

                            
                            # データプレビュー
                            with st.expander("📋 分析済みデータプレビュー"):
                                st.dataframe(merged_df.head(20), use_container_width=True)
                
                except Exception as e:
                    st.error(f"❌ 結果分析エラー: {str(e)}")
        

    
    elif menu == "📊 ジョブ履歴":
        st.markdown('<h2 class="section-header"><span class="small-icon">📊</span> ジョブ履歴</h2>', unsafe_allow_html=True)
        
        if st.session_state.jobs:
            st.subheader("📋 作成済みジョブ一覧")
            st.markdown(f"""
            <div class="info-box">
                <h4><span class="small-icon">💾</span> ファイルベース履歴管理</h4>
                <p>ジョブ履歴は job_history.json ファイルに保存されており、アプリケーション再起動時に自動で復元されます。</p>
                <p><strong>保存済みジョブ数:</strong> {len(st.session_state.jobs)} 件</p>
            </div>
            """, unsafe_allow_html=True)
            
            # ジョブを新しい順に表示
            for job in reversed(st.session_state.jobs):
                display_job_card(job)
        else:
            st.markdown("""
            <div class="info-box">
                <h4><span class="small-icon">📝</span> ジョブ履歴が空です</h4>
                <p>まだジョブが作成されていません。「📤 新規ジョブ作成」から最初のジョブを作成してください。</p>
                <p>作成されたジョブは自動的にファイルに保存され、次回起動時に復元されます。</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif menu == "⚙️ 設定":
        st.markdown('<h2 class="section-header"><span class="small-icon">⚙️</span> 設定</h2>', unsafe_allow_html=True)
        
        st.subheader("🗂️ ジョブデータ管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ ジョブ履歴をクリア", type="secondary"):
                st.session_state.jobs = []
                history_manager.clear_jobs()
                st.success("✅ ジョブ履歴をクリアしました。")
        
        with col2:
            if st.button("🔄 履歴を再読み込み", type="secondary"):
                st.session_state.jobs = history_manager.load_jobs()
                st.success("✅ ジョブ履歴を再読み込みしました。")
        
        st.subheader("ℹ️ システム情報")
        history_file_exists = history_manager.history_file.exists()
        cache_files = len(list(history_manager.download_cache_dir.glob("*.pkl")))
        
        st.markdown(f"""
        <div class="info-box">
            <h4><span class="small-icon">📊</span> システム詳細</h4>
            <p><strong>ジョブ保存場所:</strong> {manager.base_dir.absolute()}</p>
            <p><strong>履歴ファイル:</strong> {history_manager.history_file.absolute()}</p>
            <p><strong>履歴ファイル存在:</strong> {'✅ あり' if history_file_exists else '❌ なし'}</p>
            <p><strong>キャッシュファイル数:</strong> {cache_files} 個</p>
            <p><strong>作成済みジョブ数:</strong> {len(st.session_state.jobs)}</p>
            <p><strong>バージョン:</strong> 8.0.0 (5レーン対応版)</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
