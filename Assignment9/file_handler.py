import asyncio
import base64
import streamlit as st
from openai import OpenAI
from config import VECTOR_STORE_ID

client = OpenAI()


def handle_text_file(file):
    with st.chat_message("ai"):
        with st.status("⏳ Uploading file...") as status:
            uploaded_file = client.files.create(
                file=(file.name, file.getvalue()),
                purpose="user_data",
            )

            status.update(label="⏳ Attaching file...")

            client.vector_stores.files.create(
                vector_store_id=VECTOR_STORE_ID,
                file_id=uploaded_file.id,
            )
            status.update(label="✅ File uploaded", state="complete")


def handle_image_file(file, session):
    with st.status("⏳ Uploading image...") as status:
        file_bytes = file.getvalue()
        base64_data = base64.b64encode(file_bytes).decode("utf-8")
        data_uri = f"data:{file.type};base64,{base64_data}"
        asyncio.run(
            session.add_items(
                [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "detail": "auto",
                                "image_url": data_uri,
                            }
                        ],
                    }
                ]
            )
        )
        status.update(label="✅ Image uploaded", state="complete")
    with st.chat_message("human"):
        st.image(data_uri)
