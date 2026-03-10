import streamlit as st
from agents import (
    SQLiteSession,
)

from config import (
    DB_PATH,
    SESSION_KEY,
)

from ui import paint_history, run_agent
from agent import create_agent
from file_handler import handle_text_file, handle_image_file
from utils import run_async


def main():
    # 에이전트 객체 자체는 그냥 매번 새로 만들기
    agent = create_agent()

    # session_state에 SQLiteSession 생성.
    if "session" not in st.session_state:
        st.session_state["session"] = SQLiteSession(SESSION_KEY, DB_PATH)

    # 새로 렌더링할때도 세션 유지
    session = st.session_state["session"]

    run_async(paint_history(session))

    # 최초 실행. 사용자 입력 받기
    prompt = st.chat_input(
        "당신의 인생 코치입니다. 오늘도 발전하는 당신을 위해 조언을 드릴 수 있어요",
        accept_file=True,
        file_type=["txt", "jpeg", "jpg", "png"],
    )

    if prompt:
        for file in prompt.files:
            if file.type.startswith("text/"):
                handle_text_file(file)
            elif file.type.startswith("image/"):
                handle_image_file(file, session)

        if prompt.text:
            with st.chat_message("human"):
                st.write(prompt.text)
            run_async(run_agent(agent, prompt.text, session))

    with st.sidebar:
        reset = st.button("Reset Memory")
        if reset:
            run_async(session.clear_session())

        st.write(run_async(session.get_items()))


if __name__ == "__main__":
    main()
