import streamlit as st  # streamlitモジュールをインポート
import pandas as pd  # pandasモジュールをインポート
import matplotlib.pyplot as plt  # matplotlibモジュールをインポート

# 日本語フォント設定
plt.rcParams["font.sans-serif"] = ["MS Gothic"]  # Windowsのデフォルトシステムフォントを設定
plt.rcParams["axes.unicode_minus"] = False  # マイナス符号の表示を有効にする

# ページ設定
st.set_page_config(
    page_title="売上分析ダッシュボード",
    page_icon="📊",
    layout="wide"
)

# タイトル
st.title("📊 売上分析ダッシュボード")  # タイトルの表示設定
st.markdown("---")  # 区切り線の表示設定

# サイドバー
st.sidebar.header("設定")  # サイドバーのタイトル表示設定
st.sidebar.markdown("CSVファイルをアップロードしてください")  # サイドバーのテキスト表示設定

# ファイルのアップロード
uploaded_file = st.sidebar.file_uploader(
    "CSVファイルをアップロード",
    type=["csv"],
    help="売上データのCSVファイルを選択してください"
)

# データ読込処理
if uploaded_file is not None:  # ファイルがアップロードされた場合
    # アップロードされたファイルを使用
    @st.cache_data  # キャッシュ機能を使用してデータを読み込む
    def load_uploaded_data(file):
        df = pd.read_csv(file)
        #df["date"] = pd.to_datetime(df["date"])  # 不正な日付が入っていると、エラーになってしまうので、この行を削除
        return df
    try:
        df = load_uploaded_data(uploaded_file)
    except Exception:
        st.error("❌ ファイルが空または読み込めません。データが含まれるCSVをアップロードしてください。")
        st.stop()
    # ====== バリデーション ======
    # 空ファイルチェック
    if len(df) == 0:
        st.error("❌ ファイルが空です。データが含まれるCSVをアップロードしてください。")
        st.stop()
    
    # 必須列の存在確認
    required_columns = ["date", "sales_amount"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ 必須列が見つかりません: {missing_columns}。正しいCSVファイルをアップロードしてください。")
        st.stop()

    st.sidebar.success("✅ ファイルを読み込みました")
else:
    # サンプルデータを使用
    @st.cache_data  # キャッシュ機能を使用してデータを読み込む
    def load_sample_data():
        df = pd.read_csv("sample_sales_data.csv")
        df["date"] = pd.to_datetime(df["date"])
        return df
    df = load_sample_data()
    st.sidebar.info("📂 サンプルデータを表示中")


# IQR法で異常値の上限・下限を計算する関数
def calc_iqr_bounds(series):
    Q1 = series.quantile(0.25)  # 第一四分位数を計算
    Q3 = series.quantile(0.75)  # 第三四分位数を計算
    IQR = Q3 - Q1  # 四分位範囲を計算
    lower_bound = Q1 - 1.5 * IQR  # 下限を計算
    upper_bound = Q3 + 1.5 * IQR  # 上限を計算
    return lower_bound, upper_bound  # 下限と上限を返す

# 
def format_yaxis_man(ax):
    # Y軸を万単位で表示する
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{int(x/10000)}万"))


def preprocess_data(df):
    """
    データの前処理を実行

    Parmeters:
    ----------
    df : DataFrame
        前処理を行うデータ
    
    Returns:
    ----------
    df_clean : DataFrame
        前処理後のデータ
    report_data : dict
        レポート用のデータ
    """

    # 前処理前の情報を保存
    df_before = df.copy()
    df_clean = df.copy()

    # --------- 異常値対応 ---------
    # date列：不正な日付をNaNに変更k
    df_clean["date"] = pd.to_datetime(df_clean["date"], errors="coerce")

    # unit_price列：マイナス値・IQR上限異常を中央値に置き換え
    unit_price_median = df_clean["unit_price"].median()  # 中央値を計算
    unit_price_lower, unit_price_uppper = calc_iqr_bounds(df_clean["unit_price"])  # IQR法で異常値の上限・下限を計算
    df_clean.loc[df_clean["unit_price"] < 0, "unit_price"] = unit_price_median  # マイナス値を中央値に置き換え
    df_clean.loc[df_clean["unit_price"] > unit_price_uppper, "unit_price"] = unit_price_median  # 上限を中央値に置き換え

    # quantity列：マイナス値を中央値に置き換え
    quantity_median = df_clean["quantity"].median()  # 中央値を計算
    df_clean.loc[df_clean["quantity"] < 0, "quantity"] = quantity_median  # マイナス値を中央値に置き換え

    # sales_amount列：マイナス値・IQR上限異常を中央値に置き換え
    sales_amount_median = df_clean["sales_amount"].median()  # 中央値を計算
    sales_amount_lower, sales_amount_uppper = calc_iqr_bounds(df_clean["sales_amount"])  # IQR法で異常値の上限・下限を計算
    df_clean.loc[df_clean["sales_amount"] < 0, "sales_amount"] = sales_amount_median  # マイナス値を中央値に置き換え
    df_clean.loc[df_clean["sales_amount"] > sales_amount_uppper, "sales_amount"] = sales_amount_median  # 上限を中央値に置き換え

    # --------- 欠損値対応 ---------
    # date列：欠損値の行を削除
    df_clean = df_clean.dropna(subset=["date"])

    # product_name列：欠損値を最頻値で補完
    df_clean["product_name"] = df_clean["product_name"].fillna(df_clean["product_name"].mode()[0])  # 最頻値で補完

    # category列：欠損値を最頻値で補完
    df_clean["category"] = df_clean["category"].fillna(df_clean["category"].mode()[0])  # 最頻値で補完

    # unit_price列：欠損値を中央値で補完
    df_clean["unit_price"] = df_clean["unit_price"].fillna(unit_price_median)  # 中央値で補完

    # quantity列：欠損値を中央値で補完
    df_clean["quantity"] = df_clean["quantity"].fillna(quantity_median)  # 中央値で補完

    # sales_amount列：欠損値を中央値で補完
    df_clean["sales_amount"] = df_clean["sales_amount"].fillna(sales_amount_median)  # 中央値で補完

    # customer_id列: 欠損値の行を削除
    df_clean = df_clean.dropna(subset=["customer_id"])

    # --------- レポートデータ作成 ---------
    # 欠損値レポート
    missing_before = df_before.isnull().sum()  # 前処理前行数の欠損値を計算
    missing_after = df_clean.isnull().sum()  # 後処理後行数の欠損値を計算

    # 異常値レポート
    invalid_date_count = df_before["date"].astype(str).str.contains("INVALID_DATE").sum()  # INVALID_DATEが含まれる行数を計算
    unit_price_negative = (df_before["unit_price"] < 0).sum()  # マイナス値の行数を計算
    unit_price_large = (df_before["unit_price"] > unit_price_uppper).sum()  # IQR法による異常値の行数を計算
    quantity_negative = (df_before["quantity"] < 0).sum()  # マイナス値の行数を計算
    sales_amount_negative = (df_before["sales_amount"] < 0).sum()  # マイナス値の行数を計算
    sales_amount_large = (df_before["sales_amount"] > sales_amount_uppper).sum()  # IQR法による異常値の行数を計算

    # レポートデータをまとめる
    report_data = {
        "rows_before": len(df_before),
        "rows_after": len(df_clean),
        "rows_deleted": len(df_before) - len(df_clean),
        "missing_before": missing_before,
        "missing_after": missing_after,
        "anomaly_counts": {
            "invalid_date": invalid_date_count,
            "unit_price_negative": unit_price_negative,
            "unit_price_large": unit_price_large,
            "quantity_negative": quantity_negative,
            "sales_amount_negative": sales_amount_negative,
            "sales_amount_large": sales_amount_large
        }
    }

    return df_clean, report_data

# ========================================
# データ前処理
# ========================================
df, report_data = preprocess_data(df)

# --------- データ品質レポート ---------
st.header("📋 データ品質レポート")

# 前後比較
col1, col2, col3 = st.columns(3)  # 3列のカラムを作成
with col1:
    st.metric("処理前行数", f"{report_data["rows_before"]:,}件")
with col2:
    st.metric("処理後行数", f"{report_data["rows_after"]:,}件")
with col3:
    st.metric("削除行数", f"{report_data["rows_deleted"]:,}件")

# 欠損値対応結果
with st.expander("📊 欠損値対応結果"):
    missing_report = pd.DataFrame({
        "列名": report_data["missing_before"].index,
        "前処理前行数": report_data["missing_before"].values,
        "後処理後行数": report_data["missing_after"].values,
        "対応内容": [
            "不正日付・欠損業を削除",
            "最頻値で補完",
            "最頻値で補完",
            "中央値で補完",
            "中央値で補完",
            "中央値で補完",
            "欠損業を削除"
        ]
    })
    st.dataframe(missing_report, width="stretch")

# 異常値対応結果
with st.expander("📊 異常値対応結果"):
    # レポートデータを作成
    anomaly_report = pd.DataFrame({
        "列名": ["date", "unit_price", "unit_price", "quantity", "sales_amount", "sales_amount"],
        "異常値種類": [
            "INVALID_DATE",
            "マイナス値",
            "IQR法による異常値",
            "マイナス値",
            "マイナス値",
            "IQR法による異常値"
        ],
        "検出件数": [
            report_data["anomaly_counts"]["invalid_date"],
            report_data["anomaly_counts"]["unit_price_negative"],
            report_data["anomaly_counts"]["unit_price_large"],
            report_data["anomaly_counts"]["quantity_negative"],
            report_data["anomaly_counts"]["sales_amount_negative"],
            report_data["anomaly_counts"]["sales_amount_large"]
        ],
        "対応内容": [
            "不正業を削除",
            "中央値で置換",
            "中央値で置換",
            "中央値で置換",
            "中央値で置換",
            "中央値で置換"
        ]
    })
    st.dataframe(anomaly_report, width="stretch")

st.markdown("---")


# データ表示
st.subheader("データプレビュー")  # データプレビューの表示設定
st.dataframe(df.head(10))  # 最初の10行を表示

# 基本設計
col1, col2, col3, = st.columns(3)

with col1:
    st.metric("総売上", f"{df["sales_amount"].sum():,}円")  # 総売上を表示

with col2:
    st.metric("総件数", f"{len(df):,}件")  # 総件数を表示

with col3:
    st.metric("平均売上", f"{df["sales_amount"].mean():,.0f}円")  # 平均売上を表示

st.markdown("---")  # 区切り線の表示設定
st.success("✅ Streamlitアプリが正常に動作しています!")

# ========================================
# グラフ表示
# ========================================

st.header("売上推移")

# タブで切り替え
tab1, tab2 = st.tabs(["日別売上", "月別売上"])

with tab1:
    st.subheader("日別売上推移")

    # 日別の売上合計を集計
    daily_sales = df.groupby("date")["sales_amount"].sum().reset_index()

    # グラフの作成
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_sales["date"], daily_sales["sales_amount"], linewidth=1)
    ax.set_title("日別売上推移", fontsize=16)
    ax.set_xlabel("日付", fontsize=12)
    ax.set_ylabel("売上金額（円）", fontsize=12)

    # Y軸を見やすく（万単位で表示）
    format_yaxis_man(ax)

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    # Streamlitにグラフを表示
    st.pyplot(fig)

with tab2:
    st.subheader("月別売上推移")

    # 月別の売上合計を集計
    df["year_month"] = df["date"].dt.to_period("M")
    monthly_sales = df.groupby("year_month")["sales_amount"].sum().reset_index()
    monthly_sales["year_month"] = monthly_sales["year_month"].astype(str)

    # グラフの作成
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(monthly_sales["year_month"], monthly_sales["sales_amount"], linewidth=1, color="steelblue")
    ax.set_title("月別売上推移", fontsize=16)
    ax.set_xlabel("年月", fontsize=12)
    ax.set_ylabel("売上金額（円）", fontsize=12)

    # Y軸を見やすく（万単位で表示）
    format_yaxis_man(ax)

    plt.xticks(rotation=45)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    # Streamlitにグラフを表示
    st.pyplot(fig)

st.markdown("---")  # 区切り線の表示設定
st.header("カテゴリ・商品分析")

# タブで切り替え
tab3, tab4 = st.tabs(["カテゴリ別", "商品別"])

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("カテゴリ別売上構成比")

        # カテゴリ別の売上合計を集計
        category_sales = df.groupby("category")["sales_amount"].sum().sort_values(ascending=False)
        
        # 円グラフの作成
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(category_sales.values, labels=category_sales.index, autopct="%1.1f%%",
               startangle=90, textprops={"fontsize": 12})
        ax.set_title("カテゴリ別売上構成比", fontsize=16)
        plt.tight_layout()

        st.pyplot(fig)

    with col2:
        st.subheader("カテゴリ別売上")

        # 棒グラフの作成
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(category_sales.index, category_sales.values, color=["steelblue", "orange", "green"])
        ax.set_title("カテゴリ別売上", fontsize=16)
        ax.set_xlabel("カテゴリ", fontsize=12)
        ax.set_ylabel("売上金額（円）", fontsize=12)

        # Y軸を見やすく（万単位で表示）
        format_yaxis_man(ax)

        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()

        st.pyplot(fig)

with tab4:
    st.subheader("商品別売上ランキング")

    # 商品別の売上合計を集計
    product_sales = df.groupby("product_name")["sales_amount"].sum().sort_values(ascending=False)

    # 棒グラフの作成
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(product_sales.index, product_sales.values, color="steelblue")
    ax.set_title("商品別売上ランキング", fontsize=16)
    ax.set_xlabel("商品名", fontsize=12)
    ax.set_ylabel("売上金額（円）", fontsize=12)
    plt.xticks(rotation=45, ha="right")

    # Y軸を見やすく（万単位で表示）
    format_yaxis_man(ax)

    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    st.pyplot(fig)