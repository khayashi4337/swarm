from swarm import Agent

# 返金を処理する関数
# 指定された商品ID (item_id) のアイテムを返金します。返金の理由が指定されていない場合は "NOT SPECIFIED" として処理されます。
# 実際に返金処理を行う前に、ユーザーに確認を求めることが推奨されます。
def process_refund(item_id, reason="NOT SPECIFIED"):
    print(f"[mock] アイテム {item_id} を返金中。理由: {reason}...")
    return "成功しました！"

# ユーザーのカートに割引を適用する関数
# ユーザーのカートに割引を適用し、適用結果を返します。
def apply_discount():
    print("[mock] 割引を適用中...")
    return "11%の割引を適用しました"

# トリアージエージェントの作成
# ユーザーのリクエストを受け取り、最も適したエージェントに会話を引き継ぐエージェントです。
triage_agent = Agent(
    name="トリアージエージェント",
    instructions="ユーザーのリクエストを処理するのに最適なエージェントを決定し、そのエージェントに会話を引き継いでください。"
)

# 販売エージェントの作成
# ユーザーに商品（この場合は蜂）を積極的に売ることに特化したエージェントです。
sales_agent = Agent(
    name="販売エージェント",
    instructions="蜂を売ることにとても熱心になってください。"
)

# 返金エージェントの作成
# ユーザーの返金リクエストに対応するエージェントです。
# 「高すぎる」という理由の場合、返金コードを提供し、ユーザーが返金を強く希望する場合には返金処理を行います。
refunds_agent = Agent(
    name="返金エージェント",
    instructions="ユーザーに返金を手伝います。理由が「高すぎる」である場合は、返金コードを提供してください。ユーザーが強く希望する場合には返金を処理します。",
    functions=[process_refund, apply_discount]
)

# トリアージエージェントに戻す関数
# 現在のエージェントで対応できないトピックに関してユーザーが問い合わせた場合、この関数を呼び出してトリアージエージェントに戻します。
def transfer_back_to_triage():
    return triage_agent

# 販売エージェントに移行する関数
def transfer_to_sales():
    return sales_agent

# 返金エージェントに移行する関数
def transfer_to_refunds():
    return refunds_agent

# トリアージエージェントに販売エージェントと返金エージェントへの移行関数を設定
triage_agent.functions = [transfer_to_sales, transfer_to_refunds]

# 販売エージェントと返金エージェントにトリアージエージェントへの移行関数を追加
sales_agent.functions.append(transfer_back_to_triage)
refunds_agent.functions.append(transfer_back_to_triage)
