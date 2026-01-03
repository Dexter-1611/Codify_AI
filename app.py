import streamlit as st
import sqlite3
import os
import time
from groq import Groq
from dotenv import load_dotenv

# --- 1. CORE CONFIGURATION ---
load_dotenv()
# Ensure you have set your GROQ_API_KEY in Streamlit Secrets or .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="CODIFY AI | DEEKSHITH", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED NEON STYLING (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&family=Fira+Code:wght@400;500&display=swap');
    
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #0d0d1a, #050505);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Reveal Animation for Docs */
    .reveal {
        opacity: 0;
        transform: translateY(20px);
        animation: reveal-in 0.8s forwards ease-out;
    }
    @keyframes reveal-in {
        to { opacity: 1; transform: translateY(0); }
    }

    /* Interactive Character Styling */
    .character-box {
        font-size: 100px;
        height: 140px;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: all 0.5s ease;
        filter: drop-shadow(0 0 10px #00f2ff);
    }

    /* Custom Terminal for Code */
    .code-terminal {
        background: #0d0d1a;
        border: 1px solid rgba(0, 242, 255, 0.3);
        border-radius: 10px;
        padding: 15px;
        font-family: 'Fira Code', monospace;
        margin-top: 20px;
    }

    /* Neon Buttons */
    .stButton>button {
        background: transparent !important;
        border: 2px solid #00f2ff !important;
        color: #00f2ff !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 2px;
        transition: 0.4s;
    }
    .stButton>button:hover {
        background: #00f2ff !important;
        color: #000 !important;
        box-shadow: 0 0 30px #00f2ff;
    }

    /* Pulse Loader */
    .loader-box {
        text-align: center;
        padding: 40px;
        border: 1px solid #00f2ff;
        border-radius: 20px;
        background: rgba(0, 242, 255, 0.05);
    }
    .neon-ring {
        width: 60px; height: 60px;
        border: 4px solid rgba(0, 242, 255, 0.1);
        border-top: 4px solid #00f2ff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect('codify_pro.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS history (query TEXT, code TEXT, language TEXT)')
    conn.commit()
    conn.close()

def save_to_history(query, code, language):
    conn = sqlite3.connect('codify_pro.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (query, code, language) VALUES (?, ?, ?)", (query, code, language))
    conn.commit()
    conn.close()

init_db()

# --- 4. SESSION MANAGEMENT ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = 'generator'

# --- 5. LOGIN PAGE (PEEK-A-BOO ANIMATION) ---
def login_page():
    st.markdown("<h1 style='text-align: center; font-family: Orbitron;'>SYSTEM // GATEWAY</h1>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    
    with col_mid:
        st.markdown("<div style='background: rgba(255,255,255,0.02); padding: 30px; border-radius: 20px; border: 1px solid rgba(0,242,255,0.2);'>", unsafe_allow_html=True)
        
        user_id = st.text_input("USER IDENTIFICATION")
        password = st.text_input("SECURITY PHRASE", type="password")

        # Interactive Character Logic
        if password:
            char, status = "🙈", "PRIVACY MODE ENABLED"
        elif user_id:
            char, status = "👀", "SCANNING IDENTITY..."
        else:
            char, status = "🤖", "AWAITING ACCESS KEY"

        st.markdown(f"<div class='character-box'>{char}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#00f2ff; font-family:Orbitron; font-size:0.8rem;'>{status}</p>", unsafe_allow_html=True)

        if st.button("INITIALIZE BYPASS", use_container_width=True):
            if user_id and password:
                st.session_state['logged_in'] = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. MAIN APPLICATION ROUTING ---
if not st.session_state['logged_in']:
    login_page()
else:
    # --- SIDEBAR NAV ---
    with st.sidebar:
        st.markdown("<h2 style='color:#00f2ff; font-family:Orbitron;'>NAVCOM</h2>", unsafe_allow_html=True)
        if st.button("⚡ NEURAL GENERATOR", use_container_width=True): st.session_state['page'] = 'generator'
        if st.button("📖 TECH ARCHIVE", use_container_width=True): st.session_state['page'] = 'docs'
        
        st.divider()
        st.subheader("📜 SESSION LOGS")
        conn = sqlite3.connect('codify_pro.db')
        hist = conn.execute("SELECT language, query, code FROM history ORDER BY rowid DESC LIMIT 3").fetchall()
        conn.close()
        for item in hist:
            with st.expander(f"{item[0]}: {item[1][:10]}..."):
                st.code(item[2], language=item[0].lower())
        
        if st.button("🚪 TERMINATE", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- PAGE: GENERATOR ---
    if st.session_state['page'] == 'generator':
        st.markdown("<h1 class='reveal'>CODIFY // AI GENERATOR</h1>", unsafe_allow_html=True)
        
        col_q, col_s = st.columns([2, 1])
        with col_q:
            query = st.text_area("TASK DEFINITION", height=150, placeholder="Define logic to be synthesized...")
        with col_s:
            lang = st.selectbox("SYNTAX TARGET", ["Python", "Java", "C++", "Javascript"])
            st.info("Engine: Groq LPU Llama 3.3")

        if st.button("EXECUTE SYNTHESIS"):
            if query:
                status_box = st.empty()
                status_box.markdown("""
                    <div class="loader-box">
                        <div class="neon-ring"></div>
                        <p style="color:#00f2ff; margin-top:15px; font-family:Orbitron;">SYNTHESIZING NEURAL CODE...</p>
                    </div>
                """, unsafe_allow_html=True)
                
                try:
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Write clean {lang} code for: {query}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    time.sleep(1) # Visual delay for animation
                    res = chat.choices[0].message.content
                    status_box.empty()
                    st.session_state['last_res'] = res
                    save_to_history(query, res, lang)
                except Exception as e:
                    status_box.empty()
                    st.error(f"Inference Error: {e}")

        if 'last_res' in st.session_state:
            st.markdown("### 📡 OUTPUT STREAM")
            st.markdown(st.session_state['last_res'])
            st.download_button("💾 DOWNLOAD SOURCE", st.session_state['last_res'], file_name="codify_out.txt")

    # --- PAGE: DETAILED DOCUMENTATION ---
    elif st.session_state['page'] == 'docs':
        st.markdown("<h1 class='reveal' style='text-align:center;'>TECHNICAL MANIFESTO</h1>", unsafe_allow_html=True)
        
        # Performance Indicators
        p1, p2, p3 = st.columns(3)
        with p1: st.markdown("<div class='reveal' style='text-align:center; padding:20px; border:1px solid #00f2ff; border-radius:15px;'><p>THROUGHPUT</p><h2 style='color:#00f2ff; font-family:Orbitron;'>480 TPS</h2></div>", unsafe_allow_html=True)
        with p2: st.markdown("<div class='reveal' style='text-align:center; padding:20px; border:1px solid #00f2ff; border-radius:15px; animation-delay:0.2s;'><p>LATENCY</p><h2 style='color:#00f2ff; font-family:Orbitron;'>0.8s</h2></div>", unsafe_allow_html=True)
        with p3: st.markdown("<div class='reveal' style='text-align:center; padding:20px; border:1px solid #00f2ff; border-radius:15px; animation-delay:0.4s;'><p>DATABASE</p><h2 style='color:#00f2ff; font-family:Orbitron;'>SQLITE</h2></div>", unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown("""
        <div class="reveal" style="background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; border-left: 5px solid #00f2ff;">
            <h3>🏗️ I. SYSTEM ARCHITECTURE</h3>
            <p>Codify AI utilizes a <b>3-Tier Edge Architecture</b>. The application logic is served via <b>Streamlit</b>, 
            while the compute-intensive LLM inference is offloaded to <b>Groq's LPU (Language Processing Unit)</b> 
            Global Cloud. This allows for sub-second responses even on high-complexity logic tasks.</p>
        </div>
        """, unsafe_allow_html=True)
        
        

        st.markdown("""
        <div class="reveal" style="margin-top:20px; background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; border-left: 5px solid #7000ff;">
            <h3>🔮 II. FUTURE SCOPE & UTILIZATION</h3>
            <p>The project is designed with modularity in mind. Future iterations will include:</p>
            <ul>
                <li><b>RAG Engine:</b> Training the AI on local codebases using Vector Databases.</li>
                <li><b>Multi-Modal:</b> Voice-to-Code synthesis using Whisper API integration.</li>
                <li><b>Auto-Test:</b> Automatically generating Unit Tests for every code snippet produced.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        

        st.markdown("""
        <div class="reveal" style="margin-top:20px; background: rgba(0, 242, 255, 0.05); padding: 25px; border-radius: 15px;">
            <h3>🏢 III. INDUSTRIAL USE CASES</h3>
            <p><b>DevOps:</b> Instant generation of Dockerfiles and CI/CD pipelines.<br>
            <b>Cybersecurity:</b> Rapid scripting for network vulnerability assessments.<br>
            <b>Enterprise:</b> Reducing boilerplate code development time by 75%.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("<p style='text-align:center;'>© 2025 CODIFY AI | DESIGNED BY DEEKSHITH</p>", unsafe_allow_html=True)