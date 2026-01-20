import pandas as pd  # pandasモジュールをインポート
from faker import Faker  # Fakerモジュールをインポート
import random  # randomモジュールをインポート
from datetime import datetime, timedelta  # datetimeモジュールをインポート

# Fakerの初期化（日本語）
fake = Faker('ja_JP') # Fakerを日本語に設定

# 商品マスタ（カテゴリごとに商品と単価を定義）
product_master = {
    "電子機器":[
        {"name":"ノートパソコン", "price":80000},
        {"name":"マウス", "price":2000},
        {"name":"キーボード", "price":5000},
    ],
    "文房具":[
        {"name":"ボールペン", "price":150},
        {"name":"ノート", "price":300},
        {"name":"ファイル", "price":500}, 
    ],
    "書籍":[
        {"name":"ビジネス書", "price":1800},
        {"name":"小説", "price":1500},
        {"name":"技術書", "price":3500}, 
    ],
}

# データ生成
data = []  # 作成したデータを格納するリスト
start_date = datetime(2024, 1, 1)  # 開始日を設定
end_date = datetime(2024, 12, 31)  # 終了日を設定

# 365日分のデータを生成
current_date = start_date  # 現在の年月日を開始日に設定
while current_date <= end_date:  # 終了日まで繰り返す
    #  1日あたり3～5件の売上データを生成
    num_records = random.randint(3, 5)  # 1日あたりの売上データ数を3～5件でランダムに生成

    for _ in range(num_records):  # num_records回（3 or 4 or 5）繰り返す
        #  ランダムにカテゴリを選択
        category = random.choice(list(product_master.keys()))  # カテゴリをランダムに選択：カテゴリ名のリストを取得
        #  そのカテゴリから商品を選択
        product = random.choice(product_master[category])  # 商品をランダムに選択：カテゴリ名から商品リストを取得し、その中から商品をランダムに選択
        #  数量を1～10個でランダムに生成
        quantity = random.randint(1, 10)  # 数量を1～10個でランダムに生成
        #  売上金額を生成（単価 × 数量）
        sales_amount = product['price'] * quantity  # 売上金額を生成（単価 × 数量）
        #  顧客IDを生成（100件程度）
        customer_id = f"customer_{random.randint(1, 100):03d}"  # 顧客IDを生成：customer_3桁の整数

        data.append({
            "date": current_date.strftime("%Y-%m-%d"),  # 購入日を年月日の形式で追加：str
            "product_name": product['name'],  # 商品名を追加：str
            "category": category,  # カテゴリを追加：str
            "unit_price": product['price'],  # 単価を追加：int
            "quantity": quantity,  # 数量を追加：int
            "sales_amount": sales_amount,  # 売上金額を追加：int
            "customer_id": customer_id,  # 顧客IDを追加：str
        })
    #  次の日へ
    current_date += timedelta(days=1)  # 現在の日付に1日加算

#  DataFrameに変換
df = pd.DataFrame(data)  # データをDataFrameに変換

#  CSVファイルに保存
df.to_csv("sample_sales_data.csv", index=False, encoding="utf-8")  # データをCSVファイルに保存

print("サンプルデータを生成しました。")
print(f"総件数：{len(df)}件")
print(f"\n最初の5件：")
print(df.head())

