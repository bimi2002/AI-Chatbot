import streamlit as st
import requests
import re
from PIL import Image  # For handling images

API_KEY = "contact mazrekajshkumbim@gmail.com for the key"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
bot_icon="bot.png"

def create_title():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("bot.png", use_container_width=True)
    with col2:
        st.title("Chatbot")


def divide_thinking_and_response(ai_reply):
    thinking = ""
    response = ai_reply
    thinking_end = ai_reply.find("</think>")
    if thinking_end != -1:
        thinking = ai_reply[:thinking_end].strip()
        response = ai_reply[thinking_end + 8:].strip()
    return {"thinking": thinking, "response": response}

def get_ai_reply(user_input):
    try:
        payload = {
            "model": "deepseek/deepseek-r1-distill-llama-70b:free",
            "messages": st.session_state.messages
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        ai_reply = (
            response.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        return divide_thinking_and_response(ai_reply)

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return {"thinking": "", "response": ""}


def render_latex(text):
    """
    Helper function to render LaTeX cleanly in Streamlit.
    Converts LaTeX delimiters into MathJax-compatible delimiters.
    """
    # Convert block math \[ ... \] to $$ ... $$
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)

    # Convert inline math \( ... \) to $ ... $
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)

    # Handle stray square brackets (ensure they are not mistaken for LaTeX delimiters)
    # This step is optional and depends on your use case
    text = re.sub(r'\[([^\[\]]+)\]', r'[\1]', text)

    # Ensure all block math is properly wrapped in $$
    # This step ensures consistency but should be used cautiously
    text = re.sub(r'\$\$(.*?)\$\$', r'$$\1$$', text, flags=re.DOTALL)

    return text



def main():
    create_title()
    with st.sidebar:
        st.markdown(
            """
            <h1 style="font-size: 32px; color: white; margin-bottom: 20px;">
                Deepseek R1
            </h1>
            """,
            unsafe_allow_html=True
        )
    

    # Added MathJax configuration to support amsmath
    st.markdown(
        """
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <script>
        MathJax = {
            tex: {
                packages: ['base', 'ams']
            }
        };
        </script>
        """,
        unsafe_allow_html=True
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            }
        ]
    if "question_history" not in st.session_state:
        st.session_state.question_history = []


    show_thinking = st.sidebar.checkbox("Show Thinking", value=True)


    # Sidebar for question history
    with st.sidebar:
        st.markdown(
            """
            <h2 style="color: gray;">Question History</h2>
            """,
            unsafe_allow_html=True
        )
        for i, question in enumerate(st.session_state.question_history):
            if st.button(question, key=f"question_{i}"):
                # Truncate messages to the point where this question was asked
                st.session_state.messages = st.session_state.messages[:1]  # Keep system message
                st.session_state.messages.append({"role": "user", "content": question})
                # Simulate the assistant's response
                with st.spinner("🤖 Thinking..."):
                    ai_reply = get_ai_reply(question)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_reply["response"],
                        "thinking": ai_reply["thinking"]
                    })


    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                if show_thinking and msg.get("thinking"):  # Safely access "thinking"
                    st.markdown(
                        f"""
                        <div style="background-color: #333333; padding: 10px; border-radius: 10px; color: white;">
                            🤔 **Thinking:** {render_latex(msg['thinking'])}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                st.markdown(render_latex(msg["content"]))
        elif msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(render_latex(msg["content"]))

    user_input = st.chat_input("Type your message...")

    if user_input:
        # Check for exit keywords
        exit_keywords = ["bye", "goodbye", "exit", "quit", "see you"]
        if any(word in user_input.lower() for word in exit_keywords):
            st.success("👋 Goodbye!")
            st.stop()

        # Add user input to question history
        if user_input not in st.session_state.question_history:
            st.session_state.question_history.append(user_input)

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.spinner("🤖 Thinking..."):
            ai_reply = get_ai_reply(user_input)

        # Store both thinking and response separately
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_reply["response"],
            "thinking": ai_reply["thinking"] 
        })

        # Display output based on checkbox
        with st.chat_message("assistant"):
            if show_thinking and ai_reply["thinking"]:
                st.markdown(
                    f"""
                    <div style="background-color: #333333; padding: 10px; border-radius: 10px; color: white;">
                        🤔 **Thinking:** {render_latex(ai_reply['thinking'])}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown(render_latex(ai_reply["response"]))

if __name__ == "__main__":
    main()
