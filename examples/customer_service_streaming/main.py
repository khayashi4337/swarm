import shlex
import argparse
from src.swarm.swarm import Swarm
from src.tasks.task import Task
from configs.general import test_root, test_file, engine_name, persist
from src.validator import validate_all_tools, validate_all_assistants
from src.arg_parser import parse_args

# メイン関数
# Swarm のデプロイメントやタスクの追加など、インタラクティブな操作を管理します。
def main():
    # コマンドライン引数を解析
    args = parse_args()
    try:
        # ツールとアシスタントの検証
        validate_all_tools(engine_name)
        validate_all_assistants()
    except:
        raise Exception("検証に失敗しました")

    # Swarm のインスタンスを作成
    swarm = Swarm(
        engine_name=engine_name, persist=persist)

    # テストモードの処理
    if args.test is not None:
        test_files = args.test
        if len(test_files) == 0:
            test_file_paths = [f"{test_root}/{test_file}"]
        else:
            test_file_paths = [f"{test_root}/{file}" for file in test_files]
        swarm = Swarm(engine_name='local')
        swarm.deploy(test_mode=True, test_file_paths=test_file_paths)

    # インタラクティブモードでタスクを追加
    elif args.input:
        while True:
            print("タスクを入力してください（'exit'で終了）:")
            task_input = input()

            # 'exit' コマンドのチェック
            if task_input.lower() == 'exit':
                break

            # shlex を使用してタスクの説明と引数を解析
            task_args = shlex.split(task_input)
            task_parser = argparse.ArgumentParser()
            task_parser.add_argument("description", type=str, nargs='?', default="")
            task_parser.add_argument("--iterate", action="store_true", help="新しいタスクに対して iterate フラグを設定します。")
            task_parser.add_argument("--evaluate", action="store_true", help="新しいタスクに対して evaluate フラグを設定します。")
            task_parser.add_argument("--assistant", type=str, default="user_interface", help="新しいタスクに使用するアシスタントを指定します。")

            # タスクの引数を解析
            task_parsed_args = task_parser.parse_args(task_args)

            # 新しいタスクを作成して追加
            new_task = Task(description=task_parsed_args.description,
                            iterate=task_parsed_args.iterate,
                            evaluate=task_parsed_args.evaluate,
                            assistant=task_parsed_args.assistant)
            swarm.add_task(new_task)

            # Swarm に新しいタスクをデプロイ
            swarm.deploy()
            swarm.tasks.clear()

    # 事前定義されたタスクを読み込んでデプロイ
    else:
        swarm.load_tasks()
        swarm.deploy()

    print("\n\n🍯🐝🍯 Swarm の操作が完了しました 🍯🐝🍯\n\n")

# スクリプトが直接実行された場合にメイン関数を呼び出します。
if __name__ == "__main__":
    main()
