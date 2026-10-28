import gc
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

PATH = "/ws-echo"
clients = set()


async def ws_echo(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        await ws.send_text("connected")
        while True:
            msg = await ws.receive_text()
            for c in list(clients):
                try:
                    await c.send_text(f"echo: {msg}")
                except Exception:
                    clients.discard(c)
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)


def install():
    """Trả về (ok, thông tin chẩn đoán)."""
    found = []
    for obj in gc.get_objects():
        try:
            if isinstance(obj, Starlette):
                found.append(obj)
        except Exception:
            continue

    if not found:
        return False, "Không tìm thấy Starlette app nào"

    installed = 0
    for app in found:
        routes = app.router.routes
        if any(getattr(r, "path", None) == PATH for r in routes):
            installed += 1  # đã cài rồi
            continue
        routes.insert(0, WebSocketRoute(PATH, ws_echo))
        installed += 1
    return True, f"Đã cài vào {installed}/{len(found)} Starlette app"