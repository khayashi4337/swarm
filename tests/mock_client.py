from unittest.mock import MagicMock
from swarm.types import ChatCompletionMessage, ChatCompletionMessageToolCall, Function
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion, Choice
import json

# モックレスポンスを作成する関数
def create_mock_response(message, function_calls=[], model="gpt-4o"):
    role = message.get("role", "assistant")
    content = message.get("content", "")
    tool_calls = (
        [
            ChatCompletionMessageToolCall(
                id="mock_tc_id",
                type="function",
                function=Function(
                    name=call.get("name", ""),
                    arguments=json.dumps(call.get("args", {})),
                ),
            )
            for call in function_calls
        ]
        if function_calls
        else None
    )

    return ChatCompletion(
        id="mock_cc_id",
        created=1234567890,
        model=model,
        object="chat.completion",
        choices=[
            Choice(
                message=ChatCompletionMessage(
                    role=role, content=content, tool_calls=tool_calls
                ),
                finish_reason="stop",
                index=0,
            )
        ],
    )

# モックのOpenAIクライアントクラス
class MockOpenAIClient:
    def __init__(self):
        self.chat = MagicMock()
        self.chat.completions = MagicMock()

    # 特定のレスポンスを返すようにモックを設定する関数
    def set_response(self, response: ChatCompletion):
        """
        モックに特定のレスポンスを返すように設定します。
        :param response: 返すべきChatCompletionレスポンス。
        """
        self.chat.completions.create.return_value = response

    # 一連のレスポンスを順次返すようにモックを設定する関数
    def set_sequential_responses(self, responses: list[ChatCompletion]):
        """
        モックに異なるレスポンスを順次返すように設定します。
        :param responses: 順番に返すべきChatCompletionレスポンスのリスト。
        """
        self.chat.completions.create.side_effect = responses

    # create関数が呼ばれた際に期待される引数で呼ばれたかを検証する関数
    def assert_create_called_with(self, **kwargs):
        self.chat.completions.create.assert_called_with(**kwargs)


# モッククライアントの初期化
client = MockOpenAIClient()

# 一連のモックレスポンスを設定
client.set_sequential_responses(
    [
        create_mock_response(
            {"role": "assistant", "content": "最初のレスポンス"},
            [
                {
                    "name": "process_refund",
                    "args": {"item_id": "item_123", "reason": "高すぎる"},
                }
            ],
        ),
        create_mock_response({"role": "assistant", "content": "二番目のレスポンス"}),
    ]
)

# これは最初のモックレスポンスを返すべきです
first_response = client.chat.completions.create()
print(
    first_response.choices[0].message
)  # 出力: role='agent' content='最初のレスポンス'

# これは二番目のモックレスポンスを返すべきです
second_response = client.chat.completions.create()
print(
    second_response.choices[0].message
)  # 出力: role='agent' content='二番目のレスポンス'
