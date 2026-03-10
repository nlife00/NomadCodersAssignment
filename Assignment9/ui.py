import base64
import streamlit as st
from agents import Runner

STATUS_MESSAGES = {
    "response.web_search_call.completed": ("✅ Web search completed.", "complete"),
    "response.web_search_call.in_progress": ("🔍 Web search in progress...", "running"),
    "response.web_search_call.searching": ("🔍 Starting web search...", "running"),
    "response.file_search_call.completed": ("✅ File search completed.", "complete"),
    "response.file_search_call.in_progress": ("🗂️ File search in progress...", "running"),
    "response.file_search_call.searching": ("🗂️ Starting file search...", "running"),
    "response.image_generation_call.completed": ("🎨 Image generation completed.", "complete"),
    "response.image_generation_call.generating": ("🎨 Drawing image...", "running"),
    "response.image_generation_call.progress": ("🎨 Drawing image...", "running"),
}


# status_container에 상태 업데이트.
def update_status(status_container, event):
    if event in STATUS_MESSAGES:
        label, state = STATUS_MESSAGES[event]
        status_container.update(label=label, state=state)


# 새로 렌더링할때 세션 내용으로 대화 내용 출력.
async def paint_history(session):
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                # 사용자 입력 출력.
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.image(part["image_url"])

                else:
                    # 사용자 입력이 아닌 경우 출력 (답변)
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])

        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔍 Searched the web")
            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("🗂️ Searched your file")
            elif message_type == "image_generation_call":
                image = base64.b64decode(message["result"])
                with st.chat_message("ai"):
                    st.image(image)


async def run_agent(agent, message, session):
    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        image_placeholder = st.empty()
        response = ""

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
                elif event.data.type == "response.image_generation_call.partial_image":
                    image = base64.b64decode(event.data.partial_image_b64)
                    image_placeholder.image(image)
                elif event.data.type == "response.completed":
                    image_placeholder.empty()
