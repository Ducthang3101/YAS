import os
import subprocess
import sys

try:
    import groq
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])

try:
    import streamlit
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])

try:
    import ngrok
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ngrok"])
    import ngrok

if "STREAMLIT_RUN" not in os.environ:
    NGROK_TOKEN = "TOKEN"

    try:
        listener = ngrok.forward(8519, authtoken=NGROK_TOKEN)
        print("\n" + "=" * 50)
        print(f" LINK GỬI CHO BẠN BÈ ĐÂY NÈ: {listener.url()}")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"Lỗi khởi tạo đường truyền ngrok: {e}")

    os.environ["STREAMLIT_RUN"] = "1"
    script_path = os.path.abspath(__file__)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            script_path,
            "--server.port",
            "8519",
        ]
    )
    sys.exit()

from groq import Groq
import streamlit as st

st.set_page_config(page_title="AI chatbot xàm l", page_icon="🤖", layout="centered")
st.title("🤖 Chat với AI (via Groq)")
st.caption("AI đỉnh cao ko đến từ vùng đất 36 mà từ vùng đất 88")

API_KEY = "ITS BLANK XD"

try:
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Lỗi khởi tạo API Client: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Đang trả lời..."):
            try:
                formatted_messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=formatted_messages,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
