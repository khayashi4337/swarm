from swarm import Swarm, Agent

# Swarm クライアントを作成
client = Swarm()

# 英語エージェントの設定
# ユーザーとの対話は英語のみで行います。
english_agent = Agent(
    name="英語エージェント",
    instructions="あなたは英語のみを話します。",
)

# 日本語エージェントの設定
# ユーザーとの対話は日本語のみで行います。
spanish_agent = Agent(
    name="日本語エージェント",
    instructions="あなたは日本語のみを話します。",
)

# 日本語エージェントに移行する関数
# 日本語を話すユーザーを直ちに日本語エージェントに転送します。
def transfer_to_spanish_agent():
    return spanish_agent

# 英語エージェントに日本語エージェントへの転送機能を追加
english_agent.functions.append(transfer_to_spanish_agent)

# メッセージをエージェントに送信し、会話を実行
messages = [{"role": "user", "content": "こんにちは、お元気ですか？"}]
response = client.run(agent=english_agent, messages=messages)

# 最後のメッセージ内容を出力
print(response.messages[-1]["content"])
