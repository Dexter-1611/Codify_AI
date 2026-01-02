import streamlit as st
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="CODIFY AI | DEEKSHITH", page_icon="⚡", layout="wide")

# --- 2. FUTURISTIC NEON STYLING (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #0d0d1a, #050505);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00f2ff;
        text-shadow: 0 0 10px #00f2ff;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Glassmorphism Design */
    div[data-testid="stExpander"], .stTextArea, .stSelectbox, .stTab, .stMarkdown div {
        border-radius: 15px !important;
    }

    .stButton>button {
        background: linear-gradient(45deg, #00f2ff, #7000ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px 30px !important;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
    }

    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px #00f2ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE LAYER ---
def init_db():
    conn = sqlite3.connect('codify_history.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS history (query TEXT, code TEXT, language TEXT)')
    conn.commit()
    conn.close()

def save_to_history(query, code, language):
    conn = sqlite3.connect('codify_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (query, code, language) VALUES (?, ?, ?)", (query, code, language))
    conn.commit()
    conn.close()

init_db()

# --- 4. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_page():
    st.markdown("<h1 style='text-align: center;'>🔒 SYSTEM ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background: rgba(0, 242, 255, 0.05); padding: 40px; border-radius: 20px; border: 1px solid #00f2ff;'>", unsafe_allow_html=True)
        user = st.text_input("User Identification")
        pw = st.text_input("Security Phrase", type="password")
        if st.button("INITIALIZE SYSTEM"):
            # This is "for show" - you can add real logic here if needed
            st.session_state['logged_in'] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN APPLICATION (LOGGED IN ONLY) ---
if not st.session_state['logged_in']:
    login_page()
else:
    # Sidebar Navigation Controls
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CORE SYSTEM</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#00f2ff;'>Lead Developer: <b>Deekshith</b></p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation Buttons
        if 'nav_state' not in st.session_state:
            st.session_state['nav_state'] = 'generator'
            
        if st.sidebar.button("⚡ AI GENERATOR", use_container_width=True):
            st.session_state['nav_state'] = 'generator'
            
        if st.sidebar.button("📖 DOCUMENTATION", use_container_width=True):
            st.session_state['nav_state'] = 'docs'
            
        st.markdown("---")
        
        # History Archive
        conn = sqlite3.connect('codify_history.db')
        history_data = conn.execute("SELECT language, query, code FROM history ORDER BY rowid DESC LIMIT 5").fetchall()
        conn.close()

        if history_data:
            st.subheader("📜 ARCHIVE")
            for item in history_data:
                with st.expander(f"{item[0]}: {item[1][:15]}..."):
                    st.code(item[2], language=item[0].lower())
        
        if st.button("🚪 LOGOUT"):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- CONTENT ROUTING ---
    if st.session_state['nav_state'] == 'generator':
        st.markdown("<h1 style='text-align: center;'>CODIFY AI // ARCHITECT</h1>", unsafe_allow_html=True)
        m_col1, m_col2 = st.columns([2, 1])
        with m_col1:
            user_query = st.text_area("TASK DEFINITION", height=150, placeholder="E.g. Create a Python script for real-time data cleaning...")
        with m_col2:
            st.markdown("### CONFIG")
            selected_lang = st.selectbox("SYNTAX", ["Python", "Java", "C", "C++"])
            st.info("Engine: Groq Llama 3.3 70B")

        if st.button("EXECUTE NEURAL GENERATION"):
            if user_query:
                with st.spinner("⚡ Processing on Groq LPU..."):
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "system", "content": "Expert developer. clean code only."},
                                     {"role": "user", "content": f"Language: {selected_lang}. Task: {user_query}"}],
                            model="llama-3.3-70b-versatile",
                        )
                        res = chat_completion.choices[0].message.content
                        st.session_state['last_output'] = res
                        save_to_history(user_query, res, selected_lang)
                    except Exception as e:
                        st.error(f"Error: {e}")

        if 'last_output' in st.session_state:
            st.markdown(f"### OUTPUT LOG")
            st.markdown(st.session_state['last_output'])
            st.download_button("💾 DOWNLOAD SOURCE", st.session_state['last_output'], file_name="codify_source.txt")

    elif st.session_state['nav_state'] == 'docs':
        st.markdown(f"""
            <div style="background: rgba(0, 242, 255, 0.05); padding: 25px; border-radius: 15px; border: 1px solid #00f2ff; text-align: center;">
                <h1 style="margin:0;">OFFICIAL PROJECT REPORT</h1>
                <p style="color: #00f2ff; font-size: 1.2rem;">PROJECT: <b>CODIFY AI</b> | DEVELOPER: <b>DEEKSHITH</b></p>
            </div>
        """, unsafe_allow_html=True)

        col_doc1, col_doc2 = st.columns(2)
        with col_doc1:
            with st.expander("📝 1. PROBLEM STATEMENT", expanded=True):
                st.write("Modern software engineering often suffers from 'Boilerplate Fatigue'...")
            with st.expander("🏗️ 2. SYSTEM ARCHITECTURE", expanded=True):
                st.write("**Codify AI** uses a 3-Tier Architecture...")

        with col_doc2:
            with st.expander("🎯 3. PROJECT OBJECTIVES", expanded=True):
                st.write("- Reduce code generation latency to < 1 second...")
            with st.expander("⚡ 4. TECHNICAL STACK", expanded=True):
                st.markdown("- **Framework:** Python / Streamlit...")

        st.subheader("🚀 5. METHODOLOGY & RESULTS")
        st.write("The project follows an Agile Development Methodology...")
        
        st.divider()
        st.markdown(f"<p style='text-align:center;'>© 2025 Codify AI Project | Designed & Developed by <b>Deekshith</b></p>", unsafe_allow_html=True)