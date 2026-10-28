import streamlit as st
import ws_server

ok, info = ws_server.install()   # idempotent, an toàn khi rerun
st.write("Trạng thái:", ok, "-", info)
st.write("Số client đang kết nối:", len(ws_server.clients))
st.button("Refresh")