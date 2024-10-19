from swarm.util import function_to_json

# 基本的な関数のテスト
def test_basic_function():
    # 基本的な引数を受け取り、その合計を返す関数
    def basic_function(arg1, arg2):
        return arg1 + arg2

    result = function_to_json(basic_function)
    assert result == {
        "type": "function",
        "function": {
            "name": "basic_function",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "arg1": {"type": "string"},
                    "arg2": {"type": "string"},
                },
                "required": ["arg1", "arg2"],
            },
        },
    }

# 型と説明を含む複雑な関数のテスト
def test_complex_function():
    # デフォルト値と型を持つ引数を含む複雑な関数
    def complex_function_with_types_and_descriptions(
        arg1: int, arg2: str, arg3: float = 3.14, arg4: bool = False
    ):
        """この関数はドキュメンテーション文字列を持つ複雑な関数です。"""
        pass

    result = function_to_json(complex_function_with_types_and_descriptions)
    assert result == {
        "type": "function",
        "function": {
            "name": "complex_function_with_types_and_descriptions",
            "description": "この関数はドキュメンテーション文字列を持つ複雑な関数です。",
            "parameters": {
                "type": "object",
                "properties": {
                    "arg1": {"type": "integer"},
                    "arg2": {"type": "string"},
                    "arg3": {"type": "number"},
                    "arg4": {"type": "boolean"},
                },
                "required": ["arg1", "arg2"],
            },
        },
    }
