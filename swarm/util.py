import inspect
from datetime import datetime

# デバッグメッセージを出力する関数
# デバッグモードが有効な場合にのみメッセージを出力します。
def debug_print(debug: bool, *args: str) -> None:
    if not debug:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = " ".join(map(str, args))
    print(f"\033[97m[\033[90m{timestamp}\033[97m]\033[90m {message}\033[0m")

# 対象オブジェクトにソースオブジェクトのフィールドをマージする関数
# target に source の値を追加します。
def merge_fields(target, source):
    for key, value in source.items():
        if isinstance(value, str):
            target[key] += value
        elif value is not None and isinstance(value, dict):
            merge_fields(target[key], value)

# レスポンスと差分をマージする関数
# final_response に delta の値をマージします。
def merge_chunk(final_response: dict, delta: dict) -> None:
    delta.pop("role", None)
    merge_fields(final_response, delta)

    tool_calls = delta.get("tool_calls")
    if tool_calls and len(tool_calls) > 0:
        index = tool_calls[0].pop("index")
        merge_fields(final_response["tool_calls"][index], tool_calls[0])

# Pythonの関数をJSON形式の辞書に変換する関数
# 関数の名前、説明、およびパラメータを含む関数のシグネチャをJSON形式で表現します。
def function_to_json(func) -> dict:
    """
    Python関数をJSONシリアライズ可能な辞書に変換します。
    この辞書には、関数のシグネチャ（名前、説明、パラメータなど）が含まれます。

    引数:
        func: 変換する関数。

    戻り値:
        関数のシグネチャをJSON形式で表した辞書。
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"関数 {func.__name__} のシグネチャの取得に失敗しました: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"パラメータ {param.name} の型アノテーション {param.annotation} が不明です: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }
