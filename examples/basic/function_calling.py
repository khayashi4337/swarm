from swarm import Swarm, Agent

# Swarm クライアントを作成
client = Swarm()

# コンテキスト変数を使用して挨拶の指示を作成する関数
# ユーザーの名前を取得し、挨拶に使用します。
def instructions(context_variables):
    name = context_variables.get("name", "ユーザー")
    return f"あなたは親切なエージェントです。ユーザーに名前（{name}）で挨拶してください。"

# アカウントの詳細を出力する関数
# ユーザーIDと名前を使用してアカウントの詳細を表示します。
def print_account_details(context_variables: dict):
    user_id = context_variables.get("user_id", None)
    name = context_variables.get("name", None)
    print(f"アカウント詳細: {name} {user_id}")
    return "成功"

# 天気情報を取得する関数
# 指定された場所の天気情報を返します。
def get_weather(location) -> str:
    return "{'temp':67, 'unit':'F'}"

# エージェントの設定
# 指示関数、アカウントの詳細表示、および天気情報を取得する機能を持つエージェントです。
agent = Agent(
    name="エージェント",
    instructions=instructions,
    functions=[print_account_details, get_weather],
)

# コンテキスト変数の設定
context_variables = {"name": "ジェームズ", "user_id": 123}

# メッセージをエージェントに送信し、会話を実行
response = client.run(
    messages=[{"role": "user", "content": "こんにちは！"}],
    agent=agent,
    context_variables=context_variables,
)
# 最後のメッセージ内容を出力
print(response.messages[-1]["content"])

# アカウントの詳細を表示するリクエストをエージェントに送信し、会話を実行
response = client.run(
    messages=[{"role": "user", "content": "私のアカウントの詳細を表示してください！"}],
    agent=agent,
    context_variables=context_variables,
)
# 最後のメッセージ内容を出力
print(response.messages[-1]["content"])

# 天気情報を取得するリクエストをエージェントに送信し、会話を実行
response = client.run(
    messages=[{"role": "user", "content": "NYCの天気はどうですか？"}],
    agent=agent,
    context_variables=context_variables,
)
# 最後のメッセージ内容を出力
print(response.messages[-1]["content"])
