from swarm import Swarm, Agent

# Swarm クライアントを作成
client = Swarm()

# エージェントの設定
# ユーザーに対して親切に応答するエージェントです。
my_agent = Agent(
    name="エージェント",
    instructions="あなたは親切なエージェントです。",
)

# メッセージをきれいに出力する関数
# 各メッセージの内容をフォーマットして表示します。
def pretty_print_messages(messages):
    for message in messages:
        if message["content"] is None:
            continue
        print(f"{message['sender']}: {message['content']}")

# ユーザーとの対話のための設定
messages = []
agent = my_agent
while True:
    user_input = input("> ")
    messages.append({"role": "user", "content": user_input})

    # エージェントにメッセージを送信し、応答を受け取る
    response = client.run(agent=agent, messages=messages)
    messages = response.messages
    agent = response.agent
    # 会話内容を表示
    pretty_print_messages(messages)
