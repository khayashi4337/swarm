# OpenAIのAPIクライアントを作成し、それをinstructorライブラリで使用します。
__client = instructor.from_openai(OpenAI())

# ブール評価の結果を格納するデータモデル
# valueは評価結果を示し、reasonはオプションで評価の理由を記述するためのフィールドです。
class BoolEvalResult(BaseModel):
    value: bool  # 評価の結果（TrueまたはFalse）
    reason: Optional[str]  # 評価結果の理由（オプション）

# 指定された指示とデータを使用してLLM（大規模言語モデル）で評価を行い、ブール結果を返す関数
# instruction: 評価のための指示
# data: 評価するデータ（例：会話など）
def evaluate_with_llm_bool(instruction, data) -> BoolEvalResult:
    # LLMを使用して評価を行い、結果をBoolEvalResultとして取得します。
    eval_result, _ = __client.chat.completions.create_with_completion(
        model="gpt-4o",  # 使用するモデルを指定
        messages=[
            {"role": "system", "content": instruction},  # システムメッセージとして評価指示を提供
            {"role": "user", "content": data},  # ユーザーメッセージとして評価対象のデータを提供
        ],
        response_model=BoolEvalResult,  # レスポンスをBoolEvalResultとしてパース
    )
    return eval_result  # 評価結果を返す
