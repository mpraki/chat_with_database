import uuid
from datetime import datetime

import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

from src.data_extractor_agent import stream_agent

nest_asyncio.apply()
load_dotenv()

# Header row with title (left) and action button (right)
col_title, col_action = st.columns([0.8, 0.2])
with col_title:
    st.title("Chat with your database")
with col_action:
    # Align the button vertically with the large H1 title
    st.markdown(
        """
        <style>
        div.stButton > button:first-child { margin-top: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _flow_button_clicked = st.button("Agent Flow", use_container_width=True)

# Initialize chat history and agent
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Add custom CSS for chat styling
st.markdown("""
<style>
.chat-container {
    margin-bottom: 20px;
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    max-width: 80%;
    margin-left: auto;
    margin-right: 0;
}

.assistant-message {
    background: #f8f9fa;
    color: #333;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    max-width: 80%;
    margin-left: 0;
    margin-right: auto;
    border-left: 4px solid #667eea;
}

.message-timestamp {
    font-size: 0.75rem;
    color: #666;
    margin-top: 4px;
    text-align: right;
}

.assistant-timestamp {
    text-align: left;
}

.data-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.message-separator {
    height: 1px;
    background: linear-gradient(to right, transparent, #e0e0e0, transparent);
    margin: 16px 0;
}

</style>
""", unsafe_allow_html=True)

# Initialize flow modal state
if "show_flow" not in st.session_state:
    st.session_state.show_flow = False
if "_fallback_flow" not in st.session_state:
    st.session_state._fallback_flow = False

# Resolve absolute path to the flow diagram image
FLOW_IMAGE_PATH = str((Path(__file__).resolve().parent / "langgraph_diagram.png").as_posix())

# Define a dialog (if supported by the installed Streamlit version)
if hasattr(st, "dialog"):
    @st.dialog("Agent Flow")
    def show_flow_dialog():
        st.image(FLOW_IMAGE_PATH, use_container_width=True)

# Button to show the agent flow diagram in a popup
if _flow_button_clicked:
    st.session_state.show_flow = True
    if hasattr(st, "dialog"):
        show_flow_dialog()
    else:
        st.session_state._fallback_flow = True

# Fallback rendering when dialogs are not available
if st.session_state._fallback_flow and not hasattr(st, "dialog"):
    with st.expander("Agent Flow", expanded=True):
        st.image(FLOW_IMAGE_PATH, use_container_width=True)
        if st.button("Close Agent Flow"):
            st.session_state._fallback_flow = False

# Display chat messages from history on app rerun
for i, message in enumerate(st.session_state.messages):
    # Add separator between messages (except before first message)
    if i > 0:
        st.markdown('<div class="message-separator"></div>', unsafe_allow_html=True)
    
    # Get timestamp
    timestamp = message.get("timestamp", datetime.now().strftime("%H:%M"))
    
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            {message["content"]}
            <div class="message-timestamp">{timestamp}</div>
        </div>
        """, unsafe_allow_html=True)
    else:  # assistant
        content = message["content"]
        if isinstance(content, list) and content and isinstance(content[0], dict):
            st.markdown(f"""
            <div class="assistant-message">
                <div class="data-card">
                    <strong>📊 Query Results</strong>
                </div>
                <div class="message-timestamp assistant-timestamp">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
            # Display the dataframe below the styled card
            st.dataframe(content)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                {content}
                <div class="message-timestamp assistant-timestamp">{timestamp}</div>
            </div>
            """, unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("What do you want to see in your data..."):
    # Add separator before new message
    if st.session_state.messages:
        st.markdown('<div class="message-separator"></div>', unsafe_allow_html=True)
    
    # Display user message with new styling
    timestamp = datetime.now().strftime("%H:%M")
    st.markdown(f"""
    <div class="user-message">
        {prompt}
        <div class="message-timestamp">{timestamp}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add user message to chat history with timestamp
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": timestamp
    })

    # response = run_agent(prompt, st.session_state.session_id)

    progress_update = ''
    # Get assistant response
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
                # Replace response content entirely for each new response
                response = chunk["content"]
                # Clear the placeholder
                placeholder.empty()

    # Only add to chat history if we have a valid response
    if response:
        # Add assistant response to chat history with timestamp
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Force a rerun to display the new message
        st.rerun()
