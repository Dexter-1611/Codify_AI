import streamlit as st
from groq import Groq
import time

# --- 1. THEME & CYBERPUNK CSS ---
st.set_page_config(page_title="CODIFY AI // NEURAL LINK", layout="wide")

def inject_cyber_css():
    st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #05010a; color: #00ff41; font-family: 'Courier New', monospace; }
    
    /* Cyberpunk Card Container */
    .cyber-card {
        border: 2px solid #ff003c;
        padding: 40px;
        background: rgba(13, 2, 33, 0.9);
        box-shadow: 0 0 20px #ff003c, inset 0 0 10px #ff003c;
        border-radius: 2px;
        text-align: center;
        margin-top: 50px;
    }

    /* Transition Button with Custom Cursor */
    div.stButton > button:first-child {
        background-color: transparent;
        color: #00f3ff;
        border: 2px solid #00f3ff;
        font-weight: bold;
        letter-spacing: 3px;
        cursor: crosshair !important; 
        transition: 0.4s all ease;
        width: 100%;
    }

    div.stButton > button:first-child:hover {
        background-color: #00f3ff;
        color: #000;
        box-shadow: 0 0 30px #00f3ff;
        transform: scale(1.02);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0a0112;
        border-right: 1px solid #ff003c;
    }
    </style>
    """, unsafe_allow_html=True)

inject_cyber_css()

# --- 2. SESSION & AUTHENTICATION ---
if 'authorized' not in st.session_state:
    st.session_state.authorized = False

def handle_login():
    st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
    st.title("📟 CODIFY_AUTH.SYS")
    user_id = st.text_input("USER_IDENTIFIER", placeholder="Neural ID")
    access_token = st.text_input("ACCESS_KEY", type="password")
    
    if st.button("ESTABLISH NEURAL LINK"):
        if user_id == "admin" and access_token == "cyber2026":
            st.session_state.authorized = True
            st.success("LINK ESTABLISHED.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("ERROR: UNAUTHORIZED ACCESS ATTEMPT")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. MAIN INTERFACE ---
if not st.session_state.authorized:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        handle_login()
else:
    # --- SIDEBAR: DOCS & LANGUAGE SELECTOR ---
    with st.sidebar:
        st.header("📂 SYSTEM_CORE")
        st.markdown("---")
        
        # Multi-language support dropdown
        selected_lang = st.selectbox(
            "SELECT DATA_LANGUAGE",
            ["Python", "R", "SQL", "Julia"],
            index=0,
            help="Choose the neural language for code generation."
        )
        
        st.subheader("Documentation")
        st.write(f"- **Target:** {selected_lang}")
        st.write("- **Engine:** Groq LPU™")
        st.write("- **Model:** Llama 3.3 70B")
        
        st.markdown("---")
        if st.button("TERMINATE SESSION"):
            st.session_state.authorized = False
            st.rerun()

    # --- MAIN GENERATOR PAGE ---
    st.title(f"🚀 NEURAL_GEN // {selected_lang.upper()}")
    user_input = st.text_area(f"DESCRIBE {selected_lang.upper()} TASK >", height=150, placeholder="Enter your data science logic here...")
    
    if st.button("EXECUTE GENERATION"):
        if user_input:
            with st.spinner("⚡ BREACHING DATASTREAM..."):
                try:
                    # Initialize Groq Client (Ensure key is in .streamlit/secrets.toml)
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # Mapping for syntax highlighting in st.code
                    lang_map = {"Python": "python", "R": "r", "SQL": "sql", "Julia": "julia"}
                    
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system", 
                                "content": f"You are a professional Data Science script generator. Return ONLY clean {selected_lang} code. Do not include markdown formatting, explanations, or backticks. Just the code."
                            },
                            {"role": "user", "content": user_input},
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    
                    code_output = chat_completion.choices[0].message.content
                    
                    st.subheader(f"GENERATED {selected_lang.upper()} CODE:")
                    st.code(code_output, language=lang_map[selected_lang])
                    
                    # Download Button
                    st.download_button(
                        label=f"💾 DOWNLOAD {selected_lang.upper()}_CODE",
                        data=code_output,
                        file_name=f"codify_output.{lang_map[selected_lang]}",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"HARDWARE ERROR: {e}")
        else:
            st.warning("INPUT DATA REQUIRED.")