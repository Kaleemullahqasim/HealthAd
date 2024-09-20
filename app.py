import streamlit as st
from db_setup import init_db, add_user, authenticate_user, get_chat_history, add_chat_message
from callbacks import on_click_callback
import streamlit.components.v1 as components
import re

# Your Google AdSense code
adsense_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4035822500692729"
     crossorigin="anonymous"></script>
"""

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def load_js():
    with open("static/scripts.js", "r") as f:
        js = f.read()
        st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)

def initialize_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "human_prompt" not in st.session_state:
        st.session_state.human_prompt = ""
    if "view" not in st.session_state:
        st.session_state.view = "chat"

def is_valid_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    return re.search(regex, email)

def save_chat():
    st.session_state.view = "save_chat"

def view_chat_history():
    st.session_state.view = "view_history"

def handle_save_chat():
    email = st.text_input("Email", key="save_email")
    password = st.text_input("Password", type="password", key="save_password")
    if st.button("Save Chat"):
        if not is_valid_email(email):
            st.error("Invalid email format.")
            return
        if authenticate_user(email, password):
            st.error("Email already in use.")
        else:
            add_user(email, password)
            for chat in st.session_state.history:
                add_chat_message(email, chat['origin'], chat['message'])
            st.success("Chat saved successfully.")
            st.session_state.view = "chat"

def handle_view_history():
    email = st.text_input("Email", key="view_email")
    password = st.text_input("Password", type="password", key="view_password")
    if st.button("View Chat History"):
        if authenticate_user(email, password):
            st.session_state.email = email
            st.session_state.history = get_chat_history(email)
            # st.success("Chat history loaded successfully.")
            st.session_state.view = "chat"
        else:
            st.error("Incorrect email or password.")

def generate_response(user_email, user_input):
    if user_email:
        chat_history = get_chat_history(user_email)
    else:
        chat_history = st.session_state.history
    
    context = "\n".join([msg['message'] for msg in chat_history]) + "\n" + user_input
    
    response = on_click_callback(context)
    
    if user_email:
        add_chat_message(user_email, "human", user_input)
        add_chat_message(user_email, "ai", response)
    
    st.session_state.history.append({"origin": "human", "message": user_input})
    st.session_state.history.append({"origin": "ai", "message": response})

    return response

# Initialize
initialize_session_state()
load_css()
load_js()
init_db()

# Sidebar
st.sidebar.image("static/TeleiosLogo.png", use_column_width=True)

# Main content
st.title("Teleios - Optimized Health AI Advisor")
st.text("Welcome, type your questions about health and well-being below to start... ")

if st.session_state.view == "save_chat":
    handle_save_chat()
elif st.session_state.view == "view_history":
    handle_view_history()
else:
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    chat_placeholder = st.container()

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    with chat_placeholder:
        for chat in st.session_state.history:
            origin = chat['origin']
            message = chat['message']
            div = f"""
    <div class="chat-row {'row-reverse' if origin == 'human' else ''}">
        <div class="chat-icon {'human-avatar' if origin == 'human' else 'ai-avatar'}">
            {st.session_state.email[0].upper() if st.session_state.email and origin == 'human' else 'AI'}
        </div>
        <div class="chat-bubble {'human-bubble' if origin == 'human' else 'ai-bubble'}">
            {message}
        </div>
    </div>
            """
            st.markdown(div, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # JavaScript to scroll to the bottom
    st.markdown(
        """
        <script>
        const chatContainer = window.parent.document.querySelector('.chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
        </script>
        """,
        unsafe_allow_html=True
    )

    # Chat input box fixed at the bottom
    st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
    with st.form("chat-form", clear_on_submit=True):
        cols = st.columns((6, 1))
        cols[0].text_input(
            "Chat",
            value="",
            label_visibility="collapsed",
            key="human_prompt",
        )
        cols[1].form_submit_button(
            "Submit",
            type="primary",
            on_click=lambda: generate_response(st.session_state.email, st.session_state.human_prompt),
        )
    st.markdown("</div>", unsafe_allow_html=True)

# Save and View Chat History buttons
st.sidebar.button("SAVE THIS CHAT", on_click=save_chat)
st.sidebar.button("VIEW CHAT HISTORY", on_click=view_chat_history)
# Embed the AdSense code in the sidebar
with st.sidebar:
    components.html(adsense_code, height=200)  # Adjust the height as needed