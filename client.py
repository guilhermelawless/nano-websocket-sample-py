#!/usr/bin/env python3

import asyncio
import websockets
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--host', dest='host', type=str, default='[::1]')
parser.add_argument('--port', dest='port', type=str, default='7078')
args = parser.parse_args()


def subscription(topic: str, ack: bool=False, options: dict=None):
    d = {"action": "subscribe", "topic": topic, "ack": ack}
    if options is not None:
        d["options"] = options
    return d


async def main():
    async with websockets.connect(f"ws://{args.host}:{args.port}") as websocket:

        # Subscribe to both confirmation and votes
        # You can also add options here following instructions in
        #   https://github.com/nanocurrency/nano-node/wiki/WebSockets

        await websocket.send(json.dumps(subscription("vote", ack=True)))
        print(await websocket.recv())  # ack
        await websocket.send(json.dumps(subscription("confirmation", ack=True)))
        print(await websocket.recv())  # ack

        while 1:
            rec = json.loads(await websocket.recv())
            topic = rec.get("topic", None)
            if topic:
                message = rec["message"]
                if topic == "vote":
                    print("Vote from {} for blocks:\n\t{}".format(message["account"], message["blocks"]))

                elif topic == "confirmation":
                    print("Block confirmed: {}".format(message))


try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass
except ConnectionRefusedError:
    print("Error connecting to websocket server. Make sure you have enabled it in ~/Nano/config.json and check "
          "./sample_client.py --help")
