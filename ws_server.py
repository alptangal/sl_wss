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
PATHS = ["/ws-echo", "/_stcore/echo", "/_stcore/stream/echo"]

def install():
    found = [o for o in gc.get_objects() if _is_starlette(o)]
    if not found:
        return False, "Không tìm thấy Starlette app nào"
    for app in found:
        existing = {getattr(r, "path", None) for r in app.router.routes}
        for p in PATHS:
            if p not in existing:
                app.router.routes.insert(0, WebSocketRoute(p, ws_echo))
    return True, "paths: " + ", ".join(sorted(str(p) for p in {getattr(r, 'path', None) for r in found[0].router.routes} if p))

def _is_starlette(o):
    try:
        return isinstance(o, Starlette)
    except Exception:
        return False
def install_shared():
    apps = []
    for o in gc.get_objects():
        try:
            if isinstance(o, Starlette):
                apps.append(o)
        except Exception:
            continue

    for app in apps:
        for r in app.router.routes:
            if getattr(r, "path", None) == "/_stcore/stream":
                if getattr(r, "_wrapped", False):
                    return True, "Đã bọc từ trước"
                orig = r.app

                async def wrapper(scope, receive, send, orig=orig):
                    if scope["type"] == "websocket" and b"ws=echo" in scope.get("query_string", b""):
                        await ws_echo(WebSocket(scope, receive, send))
                    else:
                        await orig(scope, receive, send)

                r.app = wrapper
                r._wrapped = True
                return True, "Đã bọc /_stcore/stream"
    return False, "Không thấy route /_stcore/stream"