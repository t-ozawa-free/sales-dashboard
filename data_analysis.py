from turtle import color
import pandas as pd  # pandasモジュールをインポート
import matplotlib.pyplot as plt  # matplotlibモジュールをインポート

# 日本語フォント設定
plt.rcParams["font.sans-serif"] = ["MS Gothic"]  # Windowsのデフォルトシステムフォントを設定
plt.rcParams["axes.unicode_minus"] = False  # マイナス符号の表示を有効にする

# CSVファイルの読み込み（売上データの読み込み）
df = pd.read_csv("sample_sales_data.csv")  # CSVファイルを読み込み

# データの基本情報を確認
print("=" * 50)
print("データの基本情報")
print("=" * 50)
print(f"データ件数：{len(df)}件")
print(f"カラム数：{len(df.columns)}列")

#  最初の5件を表示
print("最初の5件：")
print(df.head())
print()

#  データ型の確認
print("各列のデータ型：")
print(df.dtypes)
print()

#  基本統計量
print("=" * 50)
print("基本統計量")
print("=" * 50)
print(df.describe())

#  日付をdatetime型に変換
df["date"] = pd.to_datetime(df["date"])

#  年月を追加（あとで月別集計に使うため）
df["year_month"] = df["date"].dt.to_period("M")

print("=" * 50)
print("日付変換後のデータ型")
print("=" * 50)
print(df.dtypes)
print()

#  月別の売上件数を確認
print("月別の売上件数：")
print(df["year_month"].value_counts().sort_index())

#  日別の売上合計を集計
daily_sales = df.groupby("date")["sales_amount"].sum().reset_index()

#  グラフの作成
plt.figure(figsize=(12, 6)) #  グラフのサイズを指定
plt.plot(daily_sales["date"], daily_sales["sales_amount"], linewidth=1)
plt.title("日別売上推移", fontsize=16)
plt.xlabel("日付", fontsize=12)
plt.ylabel("売上金額（円）", fontsize=12)

#  Y軸を見やすく（万単位で表示）
ax = plt.gca() #  現在の軸を取得
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x/10000:.0f}万")) #  万単位で表示

plt.grid(True, alpha=0.3)
plt.tight_layout()

#  グラフを保存
plt.savefig("daily_sales.png")
print("日別売上推移グラフを保存しました：daily_sales.png")
plt.show()

#  月別の売上合計を集計
monthly_sales = df.groupby("year_month")["sales_amount"].sum().reset_index() # 月別の売上合計を算出
monthly_sales["year_month"] = monthly_sales["year_month"].astype(str) # 年月を文字列に変換

#  グラフの作成
plt.figure(figsize=(12, 6)) #  グラフのサイズを指定
plt.plot(monthly_sales["year_month"], monthly_sales["sales_amount"], color="steelblue")
plt.title("月別売上推移", fontsize=16)
plt.xlabel("年月", fontsize=12)
plt.ylabel("売上金額（円）", fontsize=12)

#  Y軸を見やすく（万単位で表示）
ax = plt.gca() #  現在の軸を取得
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x/10000:.0f}万")) #  万単位で表示

plt.xticks(rotation=45)
plt.grid(True, alpha=0.3, axis="y")
plt.tight_layout()

#  グラフを保存
plt.savefig("monthly_sales.png")
print("月別売上推移グラフを保存しました：monthly_sales.png")
plt.show()