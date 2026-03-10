from models import getMockUser
import streamlit as st
import asyncio
from ui import paint_history
from agents import Runner, SQLiteSession, InputGuardrailTripwireTriggered
from config import SESSION_KEY, DB_PATH
from my_agents.triage_agent import triage_agent


async def run_agent(message, session, user_account_context):

    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""
        current_agent_name = triage_agent.name

        # sagent_label.caption(f"🤖 {current_agent_name}")
        st.session_state["text_placeholder"] = text_placeholder

        try:
            stream = Runner.run_streamed(
                triage_agent,
                message,
                session=session,
                context=user_account_context,
            )

            async for event in stream.stream_events():
                if event.type == "agent_updated_stream_event":
                    current_agent_name = event.new_agent.name
                    # agent_label.caption(f"🤖 {current_agent_name}")
                    st.write(f"➡️ {current_agent_name} 에이전트로 전환되었습니다.")
                    response = ""
                    text_placeholder = st.empty()
                elif event.type == "raw_response_event":
                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\$"))
        except InputGuardrailTripwireTriggered:
            st.write("당신을 도울 수 없는 영역입니다.")


def main():

    user_account_context = getMockUser()

    if "session" not in st.session_state:
        st.session_state["session"] = SQLiteSession(
            SESSION_KEY,
            DB_PATH,
        )
    session = st.session_state["session"]

    asyncio.run(paint_history(session))

    message = st.chat_input(
        "Write a message for your assistant",
    )

    if message:
        if "text_placeholder" in st.session_state:
            st.session_state["text_placeholder"].empty()

        if message:
            with st.chat_message("human"):
                st.write(message)
            asyncio.run(run_agent(message, session, user_account_context))

    with st.sidebar:
        reset = st.button("Reset memory")
        if reset:
            asyncio.run(session.clear_session())
        st.write(asyncio.run(session.get_items()))


if __name__ == "__main__":
    main()
