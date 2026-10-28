import asyncio, websockets

async def main():
    async with websockets.connect("wss://nh3zd2h49ramx3xbjec8jw.streamlit.app/ws-echo") as ws:
        print(await ws.recv())   # kỳ vọng: connected
        await ws.send("hello")
        print(await ws.recv())   # kỳ vọng: echo: hello

asyncio.run(main())