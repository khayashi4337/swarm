import json

from swarm import Swarm

# ストリーミング応答を処理して出力する関数
# 受け取ったストリーミングレスポンスを処理し、必要に応じて内容を出力します
def process_and_print_streaming_response(response):
    content = ""  # 現在のメッセージの内容を保持
    last_sender = ""  # 最後のメッセージ送信者を保持

    for chunk in response:
        # 送信者が含まれている場合、最後の送信者として記録
        if "sender" in chunk:
            last_sender = chunk["sender"]

        # メッセージ内容が含まれている場合、それを出力
        if "content" in chunk and chunk["content"] is not None:
            # 最初のメッセージ部分の場合、送信者を表示
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]

        # ツール呼び出しが含まれている場合、その情報を出力
        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")

        # 応答メッセージの終わりが来た場合、新しい行を表示
        if "delim" in chunk and chunk["delim"] == "end" and content:
            print()  # 応答メッセージの終わり
            content = ""

        # 完全なレスポンスが含まれている場合、それを返す
        if "response" in chunk:
            return chunk["response"]

# メッセージをきれいに出力する関数
# 会話メッセージを整形して表示します
def pretty_print_messages(messages) -> None:
    for message in messages:
        # アシスタントからのメッセージのみを処理
        if message["role"] != "assistant":
            continue

        # エージェント名を青色で出力
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # 応答がある場合はその内容を表示
        if message["content"]:
            print(message["content"])

        # ツール呼び出しがある場合は紫色で表示
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")

# デモループを実行する関数
# Swarmクライアントを使用してインタラクティブなデモループを実行します
def run_demo_loop(
    starting_agent, context_variables=None, stream=False, debug=False
) -> None:
    client = Swarm()  # Swarmクライアントのインスタンス化
    print("Swarm CLI を開始します 🐝")

    messages = []  # メッセージの履歴を保持
    agent = starting_agent  # 開始エージェントを設定

    while True:
        # ユーザー入力を取得し、メッセージリストに追加
        user_input = input("\033[90mユーザー\033[0m: ")
        messages.append({"role": "user", "content": user_input})

        # Swarmクライアントを使用してエージェントを実行
        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )

        # ストリーミング応答を処理するか、メッセージを整形して表示
        if stream:
            response = process_and_print_streaming_response(response)
        else:
            pretty_print_messages(response.messages)

        # 新しいメッセージを履歴に追加し、エージェントを更新
        messages.extend(response.messages)
        agent = response.agent
