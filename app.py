import gc
import streamlit as st
import tornado.web
import tornado.websocket


class EchoHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def check_origin(self, origin):
        return True  # cho phép client từ domain khác

    def open(self):
        EchoHandler.clients.add(self)
        self.write_message("connected")

    def on_message(self, message):
        # broadcast cho mọi client đang kết nối
        for c in list(EchoHandler.clients):
            c.write_message(f"echo: {message}")

    def on_close(self):
        EchoHandler.clients.discard(self)


@st.cache_resource  # chỉ chạy 1 lần cho mỗi process
def install_ws():
    for obj in gc.get_objects():
        try:
            if isinstance(obj, tornado.web.Application):
                # add_handlers chèn rule TRƯỚC catch-all của Streamlit
                obj.add_handlers(r".*", [(r"/ws-echo", EchoHandler)])
                return True
        except Exception:
            continue
    return False


ok = install_ws()
st.write("WebSocket handler đã cài:", ok)
st.write("Số client đang kết nối:", len(EchoHandler.clients))