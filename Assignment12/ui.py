import streamlit as st


async def paint_history(session):
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message.get("role")):
                if message.get("role") == "user":
                    st.write(message.get("content"))
                else:
                    if message.get("type") == "message":
                        source = message.get("source", "")
                        if source:
                            st.caption(f"🤖 {source}")
                        st.write(message["content"][0]["text"].replace("$", "\$"))
