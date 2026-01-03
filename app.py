import streamlit as st
import sqlite3
import os
import time
from groq import Groq
from dotenv import load_dotenv

# --- 1. CORE CONFIGURATION ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="CODIFY AI | DEEKSHITH", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED UI & ANIMATIONS (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&family=Fira+Code:wght@400;500&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #0d0d1a, #050505);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    @keyframes float-glow {
        0% { transform: translateY(0px); text-shadow: 0 0 5px #00f2ff; }
        50% { transform: translateY(-10px); text-shadow: 0 0 20px #7000ff; }
        100% { transform: translateY(0px); text-shadow: 0 0 5px #00f2ff; }
    }
    .dev-signature {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        text-align: center;
        margin-top: 50px;
        color: #00f2ff;
        animation: float-glow 4s ease-in-out infinite;
        letter-spacing: 5px;
    }

    .character-container {
        font-size: 100px;
        height: 150px;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: all 0.4s ease-in-out;
    }

    .manifesto-card {
        background: rgba(255,255,255,0.02);
        padding: 30px;
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 255, 0.1);
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .manifesto-card:hover {
        border-color: #00f2ff;
        background: rgba(0, 242, 255, 0.05);
    }

    .stButton>button {
        background: transparent !important;
        border: 2px solid #00f2ff !important;
        color: #00f2ff !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS history (query TEXT, code TEXT, language TEXT)')
    conn.commit()
    conn.close()

def save_to_history(query, code, language):
    conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO history (query, code, language) VALUES (?, ?, ?)", (query, code, language))
    conn.commit()
    conn.close()

init_db()

# --- 4. SESSION MANAGEMENT ---
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False
if 'page' not in st.session_state: 
    st.session_state['page'] = 'generator'

# --- 5. INTERACTIVE LOGIN PAGE ---
def login_page():
    st.markdown("<h1 style='text-align: center; font-family: Orbitron; margin-top: 50px;'>CORE // ACCESS</h1>", unsafe_allow_html=True)
    _, mid_col, _ = st.columns([1, 1.5, 1])
    
    with mid_col:
        st.markdown("<div style='background: rgba(255,255,255,0.02); padding: 40px; border-radius: 20px; border: 1px solid rgba(0,242,255,0.2);'>", unsafe_allow_html=True)
        
        user_id = st.text_input("IDENTIFICATION ID")
        password = st.text_input("SECURITY PHRASE", type="password")

        if password:
            char, msg = "🙈", "SYSTEM PRIVACY: ACTIVE"
        elif user_id:
            char, msg = "👀", "WATCHING INPUT..."
        else:
            char, msg = "🤖", "AWAITING CREDENTIALS"

        st.markdown(f"<div class='character-container'>{char}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#00f2ff; font-family:Orbitron; font-size:0.7rem;'>{msg}</p>", unsafe_allow_html=True)

        if st.button("INITIALIZE SYSTEM", use_container_width=True):
            st.session_state['logged_in'] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. MAIN APPLICATION ---
if not st.session_state['logged_in']:
    login_page()
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#00f2ff; font-family:Orbitron;'>NAVCOM</h2>", unsafe_allow_html=True)
        if st.button("⚡ NEURAL GENERATOR", use_container_width=True): 
            st.session_state['page'] = 'generator'
        if st.button("📖 TECH MANIFESTO", use_container_width=True): 
            st.session_state['page'] = 'docs'
        
        st.divider()
        st.subheader("📜 SESSION LOGS")
        
        conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
        hist = conn.execute("SELECT language, query, code FROM history ORDER BY rowid DESC LIMIT 3").fetchall()
        conn.close()
        
        for item in hist:
            with st.expander(f"{item[0]}: {item[1][:10]}..."):
                st.code(item[2], language=item[0].lower())
        
        if st.button("🚪 TERMINATE", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    if st.session_state['page'] == 'generator':
        st.markdown("<h1>AI // ARCHITECT</h1>", unsafe_allow_html=True)
        q = st.text_area("TASK DEFINITION", placeholder="Describe software logic...")
        lang = st.selectbox("SYNTAX", ["Python", "Java", "C++", "Javascript"])
        
        if st.button("EXECUTE SYNTHESIS"):
            if q:
                with st.spinner("Processing on Groq LPU..."):
                    try:
                        chat = client.chat.completions.create(
                            messages=[{"role": "user", "content": f"Code for: {q} in {lang}"}],
                            model="llama-3.3-70b-versatile"
                        )
                        st.session_state['res'] = chat.choices[0].message.content
                        save_to_history(q, st.session_state['res'], lang)
                    except Exception as e:
                        st.error(f"Inference Failure: {e}")
        
        if 'res' in st.session_state:
            st.markdown(st.session_state['res'])

    elif st.session_state['page'] == 'docs':
        st.markdown("<h1 style='text-align:center;'>TECHNICAL MANIFESTO</h1>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="manifesto-card">
            <h3>🏗️ I. PROJECT ABSTRACT</h3>
            <p>Codify AI addresses the critical need for low-latency code synthesis in Agile environments. 
            By leveraging <b>LPU (Language Processing Units)</b>, the system reduces wait times by 80% compared to traditional 
            GPU-based architectures.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="manifesto-card">
            <h3>⚙️ II. SYSTEM ARCHITECTURE</h3>
            <p>Our infrastructure follows a <b>Decoupled 3-Tier Model</b>:</p>
            <ul>
                <li><b>Interface:</b> Streamlit 1.30 with Custom CSS Injection.</li>
                <li><b>Intelligence:</b> Groq Cloud Llama-3.3-70B model.</li>
                <li><b>Audit Layer:</b> Local SQLite database for persistent history.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="manifesto-card">
            <h3>🔮 III. FUTURE SCOPE</h3>
            <p><b>Phase 2:</b> Integration of <b>RAG (Retrieval Augmented Generation)</b> to allow the AI to 
            reference private local repositories securely.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- DYNAMIC FLOATING SIGNATURE ---
    st.markdown("<div class='dev-signature'>DEVELOPED BY DEEKSHITH</div>", unsafe_allow_html=True)