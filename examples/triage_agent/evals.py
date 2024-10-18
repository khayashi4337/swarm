from swarm import Swarm
from agents import triage_agent, sales_agent, refunds_agent
from evals_util import evaluate_with_llm_bool, BoolEvalResult
import pytest
import json

client = Swarm()

# 会話の評価用プロンプト
# ユーザーとエージェント間の会話が与えられ、その会話が主な目標を達成しているかどうかを評価します。
# エージェントが目標を達成しているかどうかを判断するために、目標内の指示とユーザーの反応を考慮します。
CONVERSATIONAL_EVAL_SYSTEM_PROMPT = """
あなたには、ユーザーとエージェントの会話と、その会話の主要な目標が提供されます。
あなたの目標は、その会話に基づいてエージェントが主要な目標を達成したかどうかを評価することです。

エージェントが主要な目標を達成できたかどうかを評価するために、主要な目標に含まれる指示と、ユーザーの反応を考慮してください。
ユーザーにとって答えが満足のいくものであったか、エージェントが目標に基づいてもっと良い対応ができたかどうかを考慮します。
ユーザーが答えに満足していない場合でも、エージェントが主要な目標に含まれる指示に従っているため、目標を達成したとみなされることがあります。
"""

# 会話が成功したかどうかを評価する関数
# 与えられた会話メッセージを基にエージェントが主な目標を達成したかどうかを評価します。
def conversation_was_successful(messages) -> bool:
    conversation = f"CONVERSATION: {json.dumps(messages)}"
    result: BoolEvalResult = evaluate_with_llm_bool(
        CONVERSATIONAL_EVAL_SYSTEM_PROMPT, conversation
    )
    return result.value

# エージェントに対してクエリを実行し、ツール呼び出しを取得する関数
# エージェントがどのツールを呼び出そうとしたかを確認します。
def run_and_get_tool_calls(agent, query):
    message = {"role": "user", "content": query}
    response = client.run(
        agent=agent,
        messages=[message],
        execute_tools=False,  # ツールの実行をせずに呼び出しを確認
    )
    return response.messages[-1].get("tool_calls")

# Pytestを使用してトリアージエージェントが正しい関数を呼び出すかどうかをテストする
@pytest.mark.parametrize(
    "query,function_name",
    [
        ("返金をしたいです！", "transfer_to_refunds"),  # 返金をリクエストした場合、返金エージェントへの移行を期待
        ("販売担当と話したい。", "transfer_to_sales"),  # 販売に関する問い合わせの場合、販売エージェントへの移行を期待
    ],
)
def test_triage_agent_calls_correct_function(query, function_name):
    tool_calls = run_and_get_tool_calls(triage_agent, query)

    assert len(tool_calls) == 1  # ツール呼び出しが1つであることを確認
    assert tool_calls[0]["function"]["name"] == function_name  # 呼び出された関数名が期待通りであることを確認

# Pytestを使用して会話が成功したかどうかをテストする
@pytest.mark.parametrize(
    "messages",
    [
        [
            {"role": "user", "content": "U2のリードシンガーは誰ですか？"},
            {"role": "assistant", "content": "U2のリードシンガーはボノです。"},
        ],
        [
            {"role": "user", "content": "こんにちは！"},
            {"role": "assistant", "content": "こんにちは！今日はどのようにお手伝いできますか？"},
            {"role": "user", "content": "返金をしたいです。"},
            {"role": "tool", "tool_name": "transfer_to_refunds"},
            {"role": "user", "content": "ありがとうございます！"},
            {"role": "assistant", "content": "どういたしまして！素晴らしい一日をお過ごしください！"},
        ],
    ],
)
def test_conversation_is_successful(messages):
    result = conversation_was_successful(messages)
    assert result == True  # 会話が成功していることを確認
