import pytest
from swarm import Swarm, Agent
from tests.mock_client import MockOpenAIClient, create_mock_response
from unittest.mock import Mock
import json

DEFAULT_RESPONSE_CONTENT = "サンプルレスポンス内容"

# MockOpenAIClientを用いたテストで共通して使用するfixture
@pytest.fixture
def mock_openai_client():
    m = MockOpenAIClient()
    m.set_response(
        create_mock_response({"role": "assistant", "content": DEFAULT_RESPONSE_CONTENT})
    )
    return m

# シンプルなメッセージを使ったrun関数のテスト
def test_run_with_simple_message(mock_openai_client: MockOpenAIClient):
    agent = Agent()
    # クライアントを設定し実行
    client = Swarm(client=mock_openai_client)
    messages = [{"role": "user", "content": "こんにちは、調子はどうですか？"}]
    response = client.run(agent=agent, messages=messages)

    # レスポンス内容をアサート
    assert response.messages[-1]["role"] == "assistant"
    assert response.messages[-1]["content"] == DEFAULT_RESPONSE_CONTENT

# ツール呼び出しのテスト
def test_tool_call(mock_openai_client: MockOpenAIClient):
    expected_location = "サンフランシスコ"

    # モックを設定し、関数呼び出しを記録
    get_weather_mock = Mock()

    def get_weather(location):
        get_weather_mock(location=location)
        return "今日は晴れです。"

    agent = Agent(name="テストエージェント", functions=[get_weather])
    messages = [
        {"role": "user", "content": "サンフランシスコの天気はどうですか？"}
    ]

    # 関数呼び出しをトリガーするレスポンスを返すようモックを設定
    mock_openai_client.set_sequential_responses(
        [
            create_mock_response(
                message={"role": "assistant", "content": ""},
                function_calls=[
                    {"name": "get_weather", "args": {"location": expected_location}}
                ],
            ),
            create_mock_response(
                {"role": "assistant", "content": DEFAULT_RESPONSE_CONTENT}
            ),
        ]
    )

    # クライアントを設定し実行
    client = Swarm(client=mock_openai_client)
    response = client.run(agent=agent, messages=messages)

    get_weather_mock.assert_called_once_with(location=expected_location)
    assert response.messages[-1]["role"] == "assistant"
    assert response.messages[-1]["content"] == DEFAULT_RESPONSE_CONTENT

# execute_toolsをFalseに設定した際のツール呼び出しテスト
def test_execute_tools_false(mock_openai_client: MockOpenAIClient):
    expected_location = "サンフランシスコ"

    # モックを設定し、関数呼び出しを記録
    get_weather_mock = Mock()

    def get_weather(location):
        get_weather_mock(location=location)
        return "今日は晴れです。"

    agent = Agent(name="テストエージェント", functions=[get_weather])
    messages = [
        {"role": "user", "content": "サンフランシスコの天気はどうですか？"}
    ]

    # 関数呼び出しをトリガーするレスポンスを返すようモックを設定
    mock_openai_client.set_sequential_responses(
        [
            create_mock_response(
                message={"role": "assistant", "content": ""},
                function_calls=[
                    {"name": "get_weather", "args": {"location": expected_location}}
                ],
            ),
            create_mock_response(
                {"role": "assistant", "content": DEFAULT_RESPONSE_CONTENT}
            ),
        ]
    )

    # クライアントを設定し実行（ツールを実行しない設定）
    client = Swarm(client=mock_openai_client)
    response = client.run(agent=agent, messages=messages, execute_tools=False)
    print(response)

    # 関数が呼び出されていないことをアサート
    get_weather_mock.assert_not_called()

    # 最後のレスポンスにツール呼び出しが含まれていることをアサート
    tool_calls = response.messages[-1].get("tool_calls")
    assert tool_calls is not None and len(tool_calls) == 1
    tool_call = tool_calls[0]
    assert tool_call["function"]["name"] == "get_weather"
    assert json.loads(tool_call["function"]["arguments"]) == {
        "location": expected_location
    }

# エージェント間の引き継ぎのテスト
def test_handoff(mock_openai_client: MockOpenAIClient):
    def transfer_to_agent2():
        return agent2

    agent1 = Agent(name="テストエージェント1", functions=[transfer_to_agent2])
    agent2 = Agent(name="テストエージェント2")

    # 引き継ぎをトリガーするレスポンスを返すようモックを設定
    mock_openai_client.set_sequential_responses(
        [
            create_mock_response(
                message={"role": "assistant", "content": ""},
                function_calls=[{"name": "transfer_to_agent2"}],
            ),
            create_mock_response(
                {"role": "assistant", "content": DEFAULT_RESPONSE_CONTENT}
            ),
        ]
    )

    # クライアントを設定し実行
    client = Swarm(client=mock_openai_client)
    messages = [{"role": "user", "content": "エージェント2と話したい"}]
    response = client.run(agent=agent1, messages=messages)

    assert response.agent == agent2
    assert response.messages[-1]["role"] == "assistant"
    assert response.messages[-1]["content"] == DEFAULT_RESPONSE_CONTENT
