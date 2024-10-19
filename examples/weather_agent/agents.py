import json

from swarm import Agent

# 天気情報を取得する関数
def get_weather(location, time="now"):
    """指定された場所の現在の天気を取得します。場所は必ず都市である必要があります。"""
    return json.dumps({"location": location, "temperature": "65", "time": time})

# メールを送信する関数
def send_email(recipient, subject, body):
    print("メールを送信中...")
    print(f"宛先: {recipient}")
    print(f"件名: {subject}")
    print(f"本文: {body}")
    return "送信完了！"

# 天気情報エージェントの作成
weather_agent = Agent(
    name="天気情報エージェント",
    instructions="あなたは役に立つエージェントです。",
    functions=[get_weather, send_email],
)
