import dotenv

dotenv.load_dotenv()
import asyncio 
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool

# session_state에 agent 생성.
if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name = "Life Coach",
        instructions="""
        당신은 사용자에게 동기부여, 자기개발, 좋은 습관형성에 대한 조언을 전문으로 하는 라이프 코치입니다.
        모든 질문에 대해서는 라이프코치 입장에서 답변을 해야 하고 전혀 관련이 없는 경우에는 답변을 정중히 거절합니다.

        모든 답변은 항상 아래 도구를 이용하여 웹 검색을 하고 검색 결과를 포함한 답변을 제공합니다. 
        항상 먼저 아래 도구를 사용하세요.
            - Web Search Tool: 사용자의 질문에 웹 검색을 통해 답변을 합니다. 
        """,
        tools=[
            WebSearchTool(),
        ]
    )

# 새로 동작할때도 에이전트 유지
agent = st.session_state["agent"]

# session_state에 SQLiteSession 생성.
if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "lift-coache-memory.db"
    )

# 새로 렌더링할때도 세션 유지
session = st.session_state["session"]

# status_container에 상태 업데이트.
def update_status(status_container, event):
    status_messages = {
        'response.web_search_call.completed': ("✅ Web search completed.","complete"),
        'response.web_search_call.in_progress': ("🔍 Web search in progress...","running"),
        'response.web_search_call.searching': ("🔍 Starting web search...", "running"),
        # "response.completed": (" ", "complete"),
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)

# 새로 렌더링할때 세션 내용으로 대화 내용 출력.
async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                # 사용자 입력 출력.
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    # 사용자 입력이 아닌 경우 출력 (답변) 
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])
        
        if "type" in message and message["type"] == "web_search_call":
            with st.chat_message("ai"):
                st.write("🔍 Search the web...")

asyncio.run(paint_history())

async def run_agent(message):
    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        response=""

        stream = Runner.run_streamed(
            agent,
            message,
            session=session,
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)

# 최초 실행. 사용자 입력 받기
prompt = st.chat_input("당신의 인생 코치입니다. 오늘도 발전하는 당신을 위해 조언을 드릴 수 있어요")

if prompt:
    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))



with st.sidebar:
    reset = st.button("Reset Memory")
    if reset:
        asyncio.run(session.clear_session())

    st.write(asyncio.run(session.get_items()))