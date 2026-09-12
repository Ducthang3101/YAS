import uuid
from groq import Groq
import streamlit as st

st.set_page_config(page_title="AI chatbot xàm l", page_icon="🤖", layout="wide")

# 1. Kiểm tra API Key
if "GROQ_API_KEY" in st.secrets:
    API_KEY = st.secrets["GROQ_API_KEY"]
else:
    st.error("NO API KEY FOUND")
    st.stop()

try:
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Lỗi khởi tạo API Client: {e}")
    st.stop()

# 2. Quản lý danh sách chat
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

MODEL_NAME = st.secrets.get("GROQ_MODEL", "groq/compound")


def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {
        "title": "Cuộc trò chuyện mới",
        "messages": [],
    }
    st.session_state.current_chat_id = new_id


def ensure_valid_chat():
    if not st.session_state.chats:
        create_new_chat()
        return
    if st.session_state.current_chat_id not in st.session_state.chats:
        st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))


ensure_valid_chat()

# 3. Sidebar
with st.sidebar:
    st.title("💬 Danh sách Chat")

    if st.button("➕ Tạo chat mới", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.divider()

    for chat_id, chat_data in list(st.session_state.chats.items()):
        is_active = chat_id == st.session_state.current_chat_id
        label = (
            f"🟢 {chat_data['title']}" if is_active else f"💬 {chat_data['title']}"
        )

        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(
                label, key=f"select_{chat_id}", use_container_width=True
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = (
                        next(iter(st.session_state.chats.keys()))
                        if st.session_state.chats
                        else None
                    )
                ensure_valid_chat()
                st.rerun()

# 4. Giao diện chính
st.title("🤖 Chat với AI (via Groq)")
st.caption("AI đỉnh cao ko đến từ vùng đất 36 mà từ vùng đất 88")

ensure_valid_chat()
current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Render lịch sử tin nhắn
for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý khi gửi câu hỏi
if prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    is_first_msg = len(current_chat["messages"]) == 0
    if is_first_msg:
        current_chat["title"] = prompt[:20] + ("..." if len(prompt) > 20 else "")

    with st.chat_message("user"):
        st.markdown(prompt)
    current_chat["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Đang trả lời..."):
            try:
                formatted_messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in current_chat["messages"]
                ]
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=formatted_messages,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                current_chat["messages"].append(
                    {"role": "assistant", "content": answer}
                )

                # Chỉ rerun khi gửi tin nhắn đầu tiên để đổi tên sidebar
                if is_first_msg:
                    st.rerun()

            except Exception as e:
                st.error(f"Lỗi Groq API: {e}")