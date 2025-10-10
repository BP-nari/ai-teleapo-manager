import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import time

# ページ設定
st.set_page_config(
    page_title="AIテレアポ管理システム",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .job-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'current_job' not in st.session_state:
    st.session_state.current_job = None

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
        return str(text).strip().lower()
    
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
        
        # 行指紋を作成してrowmapを生成（社名ベース）
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
        
        # 列の順序を整理
        column_order = ['fm_id', '社名', '電話番号', 'ステータス', '架電結果', '要約', '通話時間', 
                       '住所統合', '最終トーク判定', '最終有効無効', '最終決済担当', 'row_key']
        
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

# メインアプリケーション
def main():
    st.markdown('<h1 class="main-header">📞 AIテレアポ管理システム</h1>', unsafe_allow_html=True)
    
    manager = AITeleapoManager()
    
    # サイドバー
    st.sidebar.title("🎛️ 操作メニュー")
    menu = st.sidebar.selectbox(
        "機能を選択",
        ["📤 新規ジョブ作成", "📥 結果分析", "📊 ジョブ履歴", "⚙️ 設定"]
    )
    
    if menu == "📤 新規ジョブ作成":
        st.header("📤 新規ジョブ作成")
        
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
                    st.success(f"✅ ファイル読み込み完了: {uploaded_file.name}")
                    st.info(f"📊 データ件数: {len(df)} 件")
                    
                    # データプレビュー
                    with st.expander("📋 データプレビュー"):
                        st.dataframe(df.head(10))
                    
                    # 出力ファイル名の指定
                    st.subheader("📝 出力設定")
                    output_name = st.text_input(
                        "出力ファイル名を入力してください",
                        value="AIテレアポ用リスト",
                        help="AIテレアポシステムにアップロードするファイルの名前"
                    )
                    
                    # ロボット台数選択
                    robot_count = st.selectbox(
                        "🤖 使用するロボット台数",
                        [1, 2, 3, 4, 5],
                        index=0,
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
                            
                            st.markdown(f"""
                            <div class="success-box">
                                <h4>✅ ジョブ作成完了</h4>
                                <p><strong>ジョブID:</strong> {job_id}</p>
                                <p><strong>処理件数:</strong> {result['total_rows']} 件</p>
                                <p><strong>ロボット台数:</strong> {robot_count} 台</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # ダウンロードボタン
                            with open(result['upload_path'], 'rb') as f:
                                st.download_button(
                                    label="📥 AIテレアポ用CSVをダウンロード",
                                    data=f.read(),
                                    file_name=f"{output_name}_{job_id}.csv",
                                    mime="text/csv",
                                    help="日本語対応エンコーディングで保存されています"
                                )
                
                except Exception as e:
                    st.error(f"❌ ファイル処理エラー: {str(e)}")
        
        with col2:
            st.subheader("📋 処理の流れ")
            st.markdown("""
            1. **📁 ファイルアップロード**
               - FileMakerのExcelファイルを選択
            
            2. **⚙️ 設定**
               - 出力ファイル名を指定
               - ロボット台数を選択
            
            3. **🚀 ジョブ作成**
               - データを変換・保存
               - 社名ベースの行指紋を生成
            
            4. **📥 ダウンロード**
               - AIテレアポ用CSVを取得
               - システムにアップロード
            """)
    
    elif menu == "📥 結果分析":
        st.header("📥 結果分析")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 通話結果の分析")
            
            # ジョブ選択
            if st.session_state.jobs:
                job_options = [f"{job['job_id']} - {job['output_name']}" for job in st.session_state.jobs]
                selected_job_str = st.selectbox("分析対象のジョブを選択", job_options)
                selected_job_id = selected_job_str.split(" - ")[0]
            else:
                st.warning("⚠️ 作成されたジョブがありません。まず新規ジョブを作成してください。")
                selected_job_id = None
            
            # 結果ファイルのアップロード
            results_file = st.file_uploader(
                "AIテレアポの結果CSVをアップロードしてください",
                type=['csv'],
                help="AIテレアポシステムからダウンロードした通話結果CSVファイル"
            )
            
            if results_file and selected_job_id:
                try:
                    results_df = pd.read_csv(results_file)
                    st.success(f"✅ 結果ファイル読み込み完了: {results_file.name}")
                    st.info(f"📊 通話件数: {len(results_df)} 件")
                    
                    # 結果を分析
                    analyzed_df = manager.analyze_call_results(results_df)
                    
                    # 統計を計算
                    stats = manager.calculate_statistics(analyzed_df)
                    
                    # 統計表示
                    st.subheader("📈 通話統計")
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    
                    with col_stat1:
                        st.metric("総通話件数", stats['total_calls'])
                        st.metric("有効通話件数", stats['valid_calls'])
                    
                    with col_stat2:
                        st.metric("総通話時間", stats['total_time'])
                        st.metric("転送件数", stats['transfer_calls'])
                    
                    with col_stat3:
                        st.metric("無効番号", stats['invalid_numbers'])
                        st.metric("エラー件数", stats['error_calls'])
                    
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
                    st.info(f"📊 マッチした件数: {matched_count} / {len(merged_df)} 件")
                    
                    # 出力ファイル名の指定
                    st.subheader("💾 結果保存")
                    output_filename = st.text_input(
                        "出力ファイル名を入力してください",
                        value=f"結果_{selected_job_id}",
                        help="FileMakerに取り込むためのExcelファイル名"
                    )
                    
                    if st.button("💾 結果を保存", type="primary"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        final_filename = f"{output_filename}_{timestamp}.xlsx"
                        
                        # メモリ上でExcelファイルを作成
                        from io import BytesIO
                        buffer = BytesIO()
                        merged_df.to_excel(buffer, index=False, engine='openpyxl')
                        buffer.seek(0)
                        
                        # ダウンロードボタン
                        st.download_button(
                            label="📥 分析結果をダウンロード",
                            data=buffer.getvalue(),
                            file_name=final_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        st.success(f"✅ 分析完了！ファイル: {final_filename}")
                    
                    # データプレビュー
                    with st.expander("📋 分析済みデータプレビュー"):
                        st.dataframe(merged_df.head(20))
                
                except Exception as e:
                    st.error(f"❌ 結果分析エラー: {str(e)}")
        
        with col2:
            st.subheader("📋 分析の流れ")
            st.markdown("""
            1. **🎯 ジョブ選択**
               - 分析対象のジョブを選択
            
            2. **📊 結果アップロード**
               - AIテレアポの結果CSVを選択
            
            3. **🔍 自動分析**
               - 通話結果を自動判定
               - 統計情報を計算
            
            4. **🔗 データマージ**
               - 社名ベースで元データと結合
               - FileMaker用IDを復元
            
            5. **💾 結果保存**
               - Excelファイルとして出力
               - FileMakerに取り込み可能
            """)
    
    elif menu == "📊 ジョブ履歴":
        st.header("📊 ジョブ履歴")
        
        if st.session_state.jobs:
            st.subheader("📋 作成済みジョブ一覧")
            
            for job in reversed(st.session_state.jobs):  # 新しい順に表示
                with st.expander(f"🎯 {job['job_id']} - {job['output_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**作成日時:** {job['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**元ファイル:** {job['filename']}")
                        st.write(f"**出力名:** {job['output_name']}")
                    with col2:
                        st.write(f"**ロボット台数:** {job['robot_count']} 台")
                        st.write(f"**処理件数:** {job['total_rows']} 件")
                        st.write(f"**ステータス:** {job['status']}")
        else:
            st.info("📝 まだジョブが作成されていません。")
    
    elif menu == "⚙️ 設定":
        st.header("⚙️ 設定")
        
        st.subheader("🗂️ ジョブデータ管理")
        
        if st.button("🗑️ 全ジョブ履歴をクリア", type="secondary"):
            st.session_state.jobs = []
            st.success("✅ ジョブ履歴をクリアしました。")
        
        st.subheader("ℹ️ システム情報")
        st.info(f"""
        **ジョブ保存場所:** {manager.base_dir.absolute()}
        **作成済みジョブ数:** {len(st.session_state.jobs)}
        **バージョン:** 2.0.0 (社名ベースマージ対応)
        """)






if __name__ == "__main__":
    main()
