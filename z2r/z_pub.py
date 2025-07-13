import time
from typing import Optional
from std_msgs.msg import String  # 送信したいROS 2メッセージの型をインポート
from rclpy.serialization import serialize_message # シリアライズ用

import zenoh


def main(
    conf: zenoh.Config, key: str, payload: str, iter: Optional[int], interval: int
):
    # initiate logging
    zenoh.init_log_from_env_or("info")

    print("Opening session...")
    with zenoh.open(conf) as session:
        print(f"Declaring Publisher on '{key}'...")
        pub = session.declare_publisher(key)

        print("Press CTRL-C to quit...")
        for idx in itertools.count() if iter is None else range(iter):
            time.sleep(interval)
            msg = String()
            msg.data = f"[{idx:4d}] {payload}"
            print(f"Putting Data ('{key}': '{msg.data}')...")
            msg_payload = serialize_message(msg)
            pub.put(msg_payload)


# --- Command line argument parsing --- --- --- --- --- ---
if __name__ == "__main__":
    import argparse
    import itertools

    import common

    parser = argparse.ArgumentParser(prog="z_pub", description="zenoh pub example")
    common.add_config_arguments(parser)
    parser.add_argument(
        "--key",
        "-k",
        dest="key",
        default="chatter",
        type=str,
        help="The key expression to publish onto.",
    )
    parser.add_argument(
        "--payload",
        "-p",
        dest="payload",
        default="Pub from Python!",
        type=str,
        help="The payload to publish.",
    )
    parser.add_argument(
        "--iter", dest="iter", type=int, help="How many puts to perform"
    )
    parser.add_argument(
        "--interval",
        dest="interval",
        type=float,
        default=1.0,
        help="Interval between each put",
    )

    args = parser.parse_args()
    conf = common.get_config_from_args(args)

    main(conf, args.key, args.payload, args.iter, args.interval)