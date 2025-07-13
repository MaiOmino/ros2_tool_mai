import json
import zenoh
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import argparse # コマンドライン引数処理のため追加
import uvicorn  # スクリプトからのサーバー起動のため追加
from contextlib import asynccontextmanager
from geometry_msgs.msg import Twist
from rclpy.serialization import serialize_message # シリアライズ用

# --- Lifespanコンテキストマネージャ ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションの起動と終了のライフサイクルを管理します。
    """
    # ▼▼▼ 起動時の処理 (yieldの前) ▼▼▼
    print("Opening Zenoh session...")
    conf = (
        zenoh.Config.from_file(args.config)
        if args.config is not None
        else zenoh.Config()
    )

    # Zenohセッションをapp.stateに保存
    app.state.zenoh_session = zenoh.open(conf)

    # アプリケーション本体に処理を移す
    yield

    # ▼▼▼ 終了時の処理 (yieldの後) ▼▼▼
    if app.state.zenoh_session:
        print("Closing Zenoh session...")
        app.state.zenoh_session.close()


# --- FastAPIアプリケーションのインスタンスを作成 ---
# lifespan関数を登録します
app = FastAPI(lifespan=lifespan)

# アプリケーションのstateに引数を格納するための準備
app.state.args = None


# --- WebSocketエンドポイント ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接続を待ち受け、クライアントからのメッセージをZenohに転送する"""
    await websocket.accept()
    print("WebSocket client connected")

    # app.stateからZenohセッションとキーを取得
    zenoh_session = websocket.app.state.zenoh_session
    # Twistメッセージのキー
    key = "turtle1/cmd_vel"

    if not zenoh_session:
        print("Error: Zenoh session not available.")
        await websocket.close(code=1011, reason="Zenoh session not initialized")
        return
    
    try:
        while True:
            data_str = await websocket.receive_text()
            # JSON文字列をPythonの辞書に変換
            data = json.loads(data_str)
            # Twistメッセージのインスタンスを作成
            msg = Twist()
            # 辞書のデータを使ってTwistメッセージのフィールドに値を設定
            msg.linear.x = float(data['linear']['x'])
            msg.linear.y = float(data['linear']['y'])
            msg.linear.z = float(data['linear']['z'])
            msg.angular.x = float(data['angular']['x'])
            msg.angular.y = float(data['angular']['y'])
            msg.angular.z = float(data['angular']['z'])
            msg_payload = serialize_message(msg)
            zenoh_session.put(key, msg_payload)
            print(f"Published to Zenoh key '{key}': {data_str}, {type(data_str)}")

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a FastAPI WebSocket server that forwards messages to Zenoh."
    )
    parser.add_argument(
        "--config",
        "-c",
        dest="config",
        metavar="FILE",
        type=str,
        help="A configuration file.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="The host to bind the FastAPI server to."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="The port to run the FastAPI server on."
    )

    args = parser.parse_args()

    # 解析した引数をFastAPIアプリのstateに保存
    app.state.args = args

    # Uvicornサーバーをプログラムから起動
    print(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)