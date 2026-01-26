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
        df["date"] = pd.to_datetime(df["date"])
        return df
    df = load_uploaded_data(uploaded_file)
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

# データ表示
st.subheader("データプレビュー")  # データプレビューの表示設定
st.dataframe(df.head(10))  # 最初の10行を表示

# 基本設計
col1, col2, col3, = st.columns(3)

with col1:
    st.metric("総売上", f"{df['sales_amount'].sum():,}円")  # 総売上を表示

with col2:
    st.metric("総件数", f"{len(df):,}件")  # 総件数を表示

with col3:
    st.metric("平均売上", f"{df['sales_amount'].mean():,.0f}円")  # 平均売上を表示

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
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{int(x/10000)}万"))

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
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{int(x/10000)}万"))

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
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{int(x/10000)}万"))

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
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{int(x/10000)}万"))

    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    st.pyplot(fig)