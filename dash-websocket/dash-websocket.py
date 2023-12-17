from websockets import connect
import sqlite3
import asyncio
import sys
import json
import aiosqlite
# from pprint import pprint
conn = sqlite3.connect('./data.db')
cursor=conn.cursor()
cursor.execute("DROP TABLE IF EXISTS trades")
cursor.execute("""CREATE TABLE trades(
  id int PRIMARY KEY,
  time int,
  quantity int,
  price float)""")
cursor.execute("CREATE INDEX index_time ON trades (time)")
conn.commit()
conn.close()

url = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade"
# url = "wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m/bnbusdt@kline_1m/ethbtc@kline_1m"


async def save_down(url):
    async with connect(url) as websocket:
        trades_buffer = []
        while True:
            data = await websocket.recv()
            data = json.loads(data)
            trades_buffer.append((data["a"], data["T"], data["q"], data["p"]))

            print(data)

            if len(trades_buffer) > 10:

                print("Printing into DB...")

                async with aiosqlite.connect("./data.db") as db:
                    await db.executemany(
                        """INSERT INTO trades
								(id, time, quantity, price) VALUES(?,?, ?, ?)""",
                        trades_buffer,
                    )

                    await db.commit()
                trades_buffer = []


asyncio.run(save_down(url))
