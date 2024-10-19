from swarm import Swarm, Agent

# Swarm クライアントを作成
client = Swarm()

# エージェントの設定
# ユーザーに対して親切に応答するエージェントです。
agent = Agent(
    name="エージェント",
    instructions="あなたは親切なエージェントです。",
)

# メッセージをエージェントに送信し、会話を実行
messages = [{"role": "user", "content": "こんにちは！"}]
response = client.run(agent=agent, messages=messages)

# 最後のメッセージ内容を出力
print(response.messages[-1]["content"])
