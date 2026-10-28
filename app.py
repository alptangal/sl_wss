import asyncio, websockets

async def _self_test(path):
    async with websockets.connect(f"ws://localhost:8501{path}") as ws:
        first = await asyncio.wait_for(ws.recv(), 5)
        await ws.send("hello")
        second = await asyncio.wait_for(ws.recv(), 5)
        return first, second

if st.button("Self-test"):
    for p in ["/ws-echo", "/_stcore/echo"]:
        try:
            st.write(p, "→", asyncio.run(_self_test(p)))
        except Exception as e:
            st.write(p, "→ lỗi:", repr(e))