from groq import Groq
import streamlit as st

st.set_page_config(page_title="AI chatbot xàm l", page_icon="🤖", layout="centered")
st.title("🤖 Chat với AI (via Groq)")
st.caption("AI đỉnh cao ko đến từ vùng đất 36 mà từ vùng đất 88")

if "GROQ_API_KEY" in st.secrets:
    API_KEY = st.secrets["GROQ_API_KEY"]
else:
    st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit Cloud!")
    st.stop()

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
