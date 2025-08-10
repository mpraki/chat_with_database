import uuid

import nest_asyncio
import streamlit as st
from dotenv import load_dotenv

from src.data_extractor_agent import stream_agent

nest_asyncio.apply()
load_dotenv()
st.title("Chat with your data")

# Initialize chat history and agent
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, list) and content and isinstance(content[0], dict):
            st.dataframe(content)
        else:
            st.markdown(content)

# React to user input
if prompt := st.chat_input("What do you want to see in your data..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # response = run_agent(prompt, st.session_state.session_id)

    progress_update = ''
    # Get assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("Thinking..."):
            response = ""
            for chunk in stream_agent(prompt, st.session_state.session_id):
                if chunk.get("type") == "progress":
                    progress_update = chunk["content"]
                    if progress_update:
                        placeholder.text(progress_update)
                elif chunk.get("type") == "error":
                    placeholder.markdown(chunk["content"])
                elif chunk.get("type") == "response":
                    progress_update = ''
                    response = chunk["content"]
                    if isinstance(response, list) and response and isinstance(response[0], dict):
                        placeholder.dataframe(response)
                    else:
                        placeholder.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
