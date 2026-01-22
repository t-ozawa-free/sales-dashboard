from turtle import color
import pandas as pd  # pandasモジュールをインポート
import matplotlib.pyplot as plt

from generate_sample_data import sales_amount  # matplotlibモジュールをインポート

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

#  =========================
#  カテゴリ別分析
#  =========================

#  カテゴリ別の売上合計を集計
category_sales = df.groupby("category")["sales_amount"].sum().sort_values(ascending=False)  # カテゴリごとに売上金額を集計

print("=" * 50)
print("カテゴリ別売上")
print("=" * 50)
for category, sales in category_sales.items():
    print(f"{category}: {sales:,}円 ({sales/df['sales_amount'].sum()*100:.1f}%)")
print()

#  円グラフ作成
plt.figure(figsize=(10, 8)) #  グラフのサイズを指定
plt.pie(category_sales.values, labels=category_sales.index, autopct="%1.1f%%",
        startangle=90, textprops={"fontsize": 12})
plt.title("カテゴリ別売上構成比", fontsize=16)
plt.tight_layout()
plt.savefig("category_pie.png")
print("カテゴリ別円グラフを保存しました：category_pie.png")
plt.show()

#  棒グラフ作成
plt.figure(figsize=(10, 6))
plt.bar(category_sales.index, category_sales.values, color=["steelblue", "orange", "green"])
plt.title("カテゴリ別売上", fontsize=16)
plt.xlabel("カテゴリ", fontsize=12)
plt.ylabel("売上金額（円）", fontsize=12)

#  Y軸を見やすく（万単位で表示）
ax = plt.gca() #  現在の軸を取得
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x/10000:.0f}万")) #  万単位で表示

plt.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig("category_bar.png")
print("カテゴリ別棒グラフを保存しました：category_bar.png")
plt.show()

#  =========================
#  商品別売り上げランキング
#  =========================

#  商品別の売上合計を集計
product_sales = df.groupby("product_name")["sales_amount"].sum().sort_values(ascending=False)  # 商品ごとに売上金額を集計して、売上金額が高い順にソート

print("=" * 50)
print("商品別売上ランキング")
print("=" * 50)
for i, (product, sales) in enumerate(product_sales.items(), start=1):
    print(f"{i}位: {product} - {sales:,}円")
print()

#  商品別売上の棒グラフ
plt.figure(figsize=(12, 6))
plt.bar(product_sales.index, product_sales.values, color="steelblue")
plt.title("商品別売上", fontsize=16)
plt.xlabel("商品名", fontsize=12)
plt.ylabel("売上金額（円）", fontsize=12)
plt.xticks(rotation=45, ha="right")

#  Y軸を見やすく（万単位で表示）
ax = plt.gca() #  現在の軸を取得
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x/10000:.0f}万")) #  万単位で表示

plt.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig("product_bar.png")
print("商品別売上グラフを保存しました：product_bar.png")
plt.show()

#  =========================
#  月次レポート
#  =========================

print("=" * 60)
print("2024年 年間売上レポート")
print("=" * 60)
print()

#  総売上
total_sales = df["sales_amount"].sum()
print(f"【総売上】")
print(f"    {total_sales:,}円")
print()

#  月平均
monthly_avg = monthly_sales["sales_amount"].mean()
print(f"【月平均売上】")
print(f"    {monthly_avg:,.0f}円")
print()

#  最高売上月
max_month = monthly_sales.loc[monthly_sales["sales_amount"].idxmax()]
print(f"【最高売上月】")
print(f"    {max_month['year_month']} - {max_month['sales_amount']:,}円")

#  最低売上月
min_month = monthly_sales.loc[monthly_sales["sales_amount"].idxmin()]
print(f"【最低売上月】")
print(f"    {min_month['year_month']} - {min_month['sales_amount']:,}円")
print()

#  カテゴリ別構成比
print(f"【カテゴリ別構成比】")
for category, sales in category_sales.items():
    print(f"    {category}: {sales/total_sales*100:.1f}%")
print()

#  トップ3商品
print(f"【トップ3商品】")
for i, (product, sales) in enumerate(product_sales.head(3).items(), start=1):
    print(f"    {i}位: {product} - {sales:,}円")
print()

print("=" * 60)
