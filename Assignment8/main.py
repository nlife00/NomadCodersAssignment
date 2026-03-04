import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio 
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool

client = OpenAI()

VECTOR_STORE_ID = "vs_69a78b75dc848191937000577a3e10e1"

# session_state에 agent 생성.
if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name = "Life Coach",
        instructions="""
        당신은 사용자에게 동기부여, 자기개발, 좋은 습관형성에 대한 조언을 전문으로 하는 라이프 코치입니다.
        모든 질문에 대해서는 라이프코치 입장에서 답변을 해야 하고 전혀 관련이 없는 경우에는 답변을 정중히 거절합니다.

        당신은 아래 도구들을 사용하여 답변할 수 있습니다. 
            - Web Search Tool: 사용자의 질문에 **항상** 웹 검색을 통해 답변을 합니다. 
            - File Search Tool: 사용자가 본인과 관련된 사실을 질문하거나 특정 파일을 언급하면 이 도구로 검색합니다.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            )
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
        'response.file_search_call.completed': ("✅ File search completed.","complete"),
        'response.file_search_call.in_progress': ("🗂️ File search in progress...","running"),
        'response.file_search_call.searching': ("🗂️ Starting file search...", "running"),
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
        
        if "type" in message:
            if message["type"] == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔍 Searched the web")
            elif message["type"] == "file_search_call":
                with st.chat_message("ai"):
                    st.write("🗂️ Searched your file")

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
prompt = st.chat_input(
    "당신의 인생 코치입니다. 오늘도 발전하는 당신을 위해 조언을 드릴 수 있어요",
    accept_file=True,
    file_type=["txt","pdf"],
)

if prompt:

    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("⏳ Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data"
                    )

                    status.update(label="⏳ Attaching file...")
                    
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id
                    )
                    status.update(label="✅ File uploaded", state = "complete")

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))

with st.sidebar:
    reset = st.button("Reset Memory")
    if reset:
        asyncio.run(session.clear_session())

    st.write(asyncio.run(session.get_items()))