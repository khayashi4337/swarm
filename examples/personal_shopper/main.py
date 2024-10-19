import datetime
import random

import database
from swarm import Agent
from swarm.agents import create_triage_agent
from swarm.repl import run_demo_loop

# 商品の返金処理を行う関数
def refund_item(user_id, item_id):
    """ユーザーIDとアイテムIDに基づいて返金を開始する関数。
    入力は、'{"user_id":"1","item_id":"3"}'の形式を取ります。
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT amount FROM PurchaseHistory
        WHERE user_id = ? AND item_id = ?
    """,
        (user_id, item_id),
    )
    result = cursor.fetchone()
    if result:
        amount = result[0]
        print(f"ユーザーID {user_id} のアイテムID {item_id} に対して {amount} ドルの返金を行います。")
    else:
        print(f"ユーザーID {user_id} およびアイテムID {item_id} の購入履歴が見つかりませんでした。")
    print("返金が開始されました。")

# 顧客に通知を送信する関数
def notify_customer(user_id, method):
    """指定された方法（電話またはメール）で顧客に通知を送信する関数。
    入力は、'{"user_id":"1","method":"email"}'の形式を取ります。
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT email, phone FROM Users
        WHERE user_id = ?
    """,
        (user_id,),
    )
    user = cursor.fetchone()
    if user:
        email, phone = user
        if method == "email" and email:
            print(f"顧客 {email} にメールで通知を送りました。")
        elif method == "phone" and phone:
            print(f"顧客 {phone} にテキストメッセージで通知を送りました。")
        else:
            print(f"ユーザーID {user_id} に対して {method} の連絡手段がありません。")
    else:
        print(f"ユーザーID {user_id} が見つかりませんでした。")

# 商品の注文を行う関数
def order_item(user_id, product_id):
    """ユーザーIDと商品IDに基づいて商品を注文する関数。
    入力は、'{"user_id":"1","product_id":"2"}'の形式を取ります。
    """
    date_of_purchase = datetime.datetime.now()
    item_id = random.randint(1, 300)

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT product_id, product_name, price FROM Products
        WHERE product_id = ?
    """,
        (product_id,),
    )
    result = cursor.fetchone()
    if result:
        product_id, product_name, price = result
        print(
            f"ユーザーID {user_id} に対して商品 {product_name} を注文します。価格は {price} ドルです。"
        )
        # 購入情報をデータベースに追加
        database.add_purchase(user_id, date_of_purchase, item_id, price)
    else:
        print(f"商品 {product_id} が見つかりませんでした。")

# データベースを初期化
database.initialize_database()

# テーブルのプレビュー
database.preview_table("Users")
database.preview_table("PurchaseHistory")
database.preview_table("Products")

# エージェントの定義
refunds_agent = Agent(
    name="Refunds Agent",
    description=f"""あなたは返金を担当するエージェントです。
    返金を開始するには、ユーザーIDとアイテムIDの両方が必要です。ユーザーIDとアイテムIDの両方を1つのメッセージで尋ねてください。
    顧客から通知を依頼された場合、通知の方法を尋ねてください。通知にはユーザーIDと方法を1つのメッセージで尋ねてください。
    """,
    functions=[refund_item, notify_customer],
)

sales_agent = Agent(
    name="Sales Agent",
    description=f"""あなたは販売を担当するエージェントです。
    注文を行うには、必ずユーザーIDと商品IDの両方が必要です。これら2つの情報がないと注文はできません。ユーザーIDと商品IDを1つのメッセージで尋ねてください。
    顧客から通知を依頼された場合、通知の方法を尋ねてください。通知にはユーザーIDと方法を1つのメッセージで尋ねてください。
    """,
    functions=[order_item, notify_customer],
)

triage_agent = create_triage_agent(
    name="Triage Agent",
    instructions=f"""ユーザーのリクエストを振り分け、適切な意図に基づいてツールを呼び出してください。
    ユーザーのリクエストが注文や商品の購入に関するものであれば、販売エージェントに転送してください。
    ユーザーのリクエストが商品の返金や返品に関するものであれば、返金エージェントに転送してください。
    振り分けに必要な情報を取得する際は、なぜ尋ねているかを説明せずに直接質問してください。
    ユーザーに考え方を共有せず、不合理な推測をしないようにしてください。
    """,
    agents=[sales_agent, refunds_agent],
    add_backlinks=True,
)

# triage_agentに定義されたすべての関数の名前を出力
for f in triage_agent.functions:
    print(f.__name__)

if __name__ == "__main__":
    # デモループを実行
    run_demo_loop(triage_agent, debug=False)


