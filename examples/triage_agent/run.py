from swarm.repl import run_demo_loop  # swarmパッケージのreplモジュールからrun_demo_loop関数をインポート
from agents import triage_agent  # agentsモジュールからtriage_agent（トリアージエージェント）をインポート

# メインスクリプトとして実行される場合の処理
# トリアージエージェントを使用してデモループを実行します。
# run_demo_loop関数はREPL（対話型の読み取り・評価・出力ループ）を実行し、
# ユーザーとエージェントの対話を模擬します。
if __name__ == "__main__":
    run_demo_loop(triage_agent)
