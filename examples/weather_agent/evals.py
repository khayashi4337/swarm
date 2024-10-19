from swarm import Swarm
from agents import weather_agent
import pytest

# Swarmクライアントのインスタンス化
client = Swarm()

# エージェントにクエリを送信し、ツール呼び出しを取得する関数
def run_and_get_tool_calls(agent, query):
    message = {"role": "user", "content": query}
    response = client.run(
        agent=agent,
        messages=[message],
        execute_tools=False,
    )
    return response.messages[-1].get("tool_calls")

# テストケース1：天気を尋ねられたときにget_weather関数が呼び出されるかどうかを確認
@pytest.mark.parametrize(
    "query",
    [
        "NYCの天気はどうですか？",
        "ロンドンの天気を教えてください。",
        "今日傘が必要ですか？私はシカゴにいます。",
    ],
)
def test_calls_weather_when_asked(query):
    tool_calls = run_and_get_tool_calls(weather_agent, query)

    assert len(tool_calls) == 1
    assert tool_calls[0]["function"]["name"] == "get_weather"

# テストケース2：天気の質問ではない場合、get_weather関数が呼び出されないかどうかを確認
@pytest.mark.parametrize(
    "query",
    [
        "アメリカ合衆国の大統領は誰ですか？",
        "現在の時間は何ですか？",
        "こんにちは！",
    ],
)
def test_does_not_call_weather_when_not_asked(query):
    tool_calls = run_and_get_tool_calls(weather_agent, query)

    assert not tool_calls
