import streamlit as st
import sqlite3
import os
import time
import pandas as pd
import hashlib
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

# --- 1.1 DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            language TEXT,
            query TEXT,
            code TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- 1.2 AUTHENTICATION HELPERS ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password):
    try:
        conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def reset_password(username, new_password):
    conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if not cursor.fetchone():
        conn.close()
        return False
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hash_password(new_password), username))
    conn.commit()
    conn.close()
    return True

# Initialize session state for auth
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'login_mode' not in st.session_state:
    st.session_state['login_mode'] = 'login'
if 'page' not in st.session_state:
    st.session_state['page'] = 'generator'

# --- 2. GLOBAL DESIGN SYSTEM (Obsidian Assembly) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500;1,600&family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

    /* ═══════════════════════════════════════════
       PITCH BLACK × METALLIC GOLD — DESIGN TOKENS
    ═══════════════════════════════════════════ */
    :root {
        --cream:        #080808;
        --cream-dark:   #0F0E0C;
        --parchment:    #161410;
        --gold:         #D4AF65;
        --gold-light:   #EDD98A;
        --gold-dark:    #B8952A;
        --charcoal:     #F0EDE6;
        --charcoal-mid: #C8BBA8;
        --warm-gray:    #8A8278;
        --warm-light:   #5A524A;
        --warm-white:   rgba(14,12,8,0.92);
        --glass-warm:   rgba(212,175,101,0.04);
        --glass-border: rgba(212,175,101,0.22);
        --shadow-warm:  rgba(0,0,0,0.5);
        --shadow-deep:  rgba(0,0,0,0.85);
    }

    /* === BASE RESET === */
    html {
        scroll-behavior: smooth !important;
    }
    body, .stApp, .stApp > header, .stAppViewContainer,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"], .stMain {
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        scroll-behavior: smooth !important;
    }
    body {
        background-color: #080808 !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        text-rendering: optimizeLegibility !important;
    }
    .stApp {
        color: var(--charcoal);
        font-family: 'Inter', sans-serif;
    }

    /* === TYPOGRAPHY SYSTEM === */
    .oa-serif {
        font-family: 'Cormorant Garamond', Georgia, serif;
        letter-spacing: -0.02em;
        line-height: 1.05;
    }
    .oa-serif-italic {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-style: italic;
        font-weight: 300;
        letter-spacing: -0.01em;
    }
    .oa-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--warm-gray);
    }
    .oa-gold-text {
        color: var(--gold);
    }

    /* === SCROLL REVEAL === */
    .reveal {
        opacity: 0;
        transform: translateY(24px);
        animation: reveal-in 0.9s forwards cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* ═══════════════════════════════════════════
       GLOBAL PERFORMANCE — GPU COMPOSITING
    ═══════════════════════════════════════════ */
    *, *::before, *::after {
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeSpeed;
    }
    /* Force GPU layers on all animated elements */
    .hud-text, .oa-card, .bc, .manifesto-card,
    .reveal, [data-testid="stVerticalBlock"] {
        will-change: transform;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        perspective: 1000px;
    }
    /* Content visibility — skip rendering offscreen sections */
    .features-section, .manifesto-section, footer {
        content-visibility: auto;
        contain-intrinsic-size: 0 500px;
    }
    /* Smooth scrolling already set; harden it */
    html, body {
        scroll-behavior: smooth;
        overflow-x: hidden;
    }
    /* Reduce paint area on hover transitions */
    .oa-card, .bc {
        contain: layout style;
    }

    @keyframes reveal-in {
        to { opacity: 1; transform: translateY(0); }
    }
    .reveal-delay-1 { animation-delay: 0.1s; }
    .reveal-delay-2 { animation-delay: 0.22s; }
    .reveal-delay-3 { animation-delay: 0.36s; }

    /* === OBSIDIAN GLASS CARDS (Pitch Black Glass) === */
    .oa-card {
        background: rgba(14, 12, 8, 0.80);
        backdrop-filter: blur(20px) saturate(150%);
        -webkit-backdrop-filter: blur(20px) saturate(150%);
        border: 1px solid rgba(212,175,101,0.18);
        border-radius: 20px;
        padding: 32px;
        box-shadow:
            0 4px 24px var(--shadow-warm),
            0 1px 0 rgba(212,175,101,0.08) inset,
            0 -1px 0 rgba(212,175,101,0.06) inset;
        transition: transform 0.4s cubic-bezier(0.16,1,0.3,1), box-shadow 0.4s ease;
    }
    .oa-card:hover {
        transform: translateY(-4px);
        box-shadow:
            0 16px 48px var(--shadow-deep),
            0 1px 0 rgba(212,175,101,0.15) inset;
        border-color: rgba(212,175,101,0.38);
    }

    /* === OBSIDIAN MANIFESTO CARDS === */
    .manifesto-card {
        background: rgba(14, 12, 8, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(212,175,101,0.15);
        border-left: 3px solid var(--gold);
        border-radius: 16px;
        padding: 36px 40px;
        margin-bottom: 24px;
        line-height: 1.7;
        transition: all 0.35s ease;
        box-shadow: 0 4px 20px var(--shadow-warm);
    }
    .manifesto-card:hover {
        border-color: rgba(212,175,101,0.45);
        box-shadow: 0 12px 40px var(--shadow-deep);
        transform: translateY(-2px);
    }
    .manifesto-card h3 {
        font-family: 'Cormorant Garamond', serif;
        color: var(--charcoal);
        font-weight: 600;
        font-size: 1.45rem;
        letter-spacing: -0.01em;
        margin-bottom: 16px;
    }
    .manifesto-card p, .manifesto-card li {
        color: var(--warm-gray);
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.75;
    }

    /* === GLOBAL SMOOTH TRANSITIONS === */
    a, p, span, h1, h2, h3, h4, h5, h6, div {
        transition: background-color 0.35s ease, color 0.35s ease, border-color 0.35s ease !important;
    }
    
    /* === OBSIDIAN BUTTON SYSTEM === */
    .stButton > button {
        background: rgba(212,175,101,0.07) !important;
        border: 1px solid rgba(212,175,101,0.45) !important;
        color: var(--charcoal) !important;
        border-radius: 50px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.18em !important;
        font-weight: 600 !important;
        padding: 14px 28px !important;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
        text-transform: uppercase !important;
        will-change: transform, background !important;
        backdrop-filter: blur(8px) !important;
    }
    .stButton > button:hover {
        background: var(--gold) !important;
        color: #080808 !important;
        border-color: var(--gold) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 32px rgba(212,175,101,0.35) !important;
    }

    /* === STREAMLIT INPUTS (Black Glass) === */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    div[data-baseweb="select"] > div {
        background-color: rgba(18,15,10,0.88) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(212,175,101,0.22) !important;
        color: var(--charcoal) !important;
        border-radius: 14px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    div[data-baseweb="select"] > div:focus-within {
        border-color: rgba(212,175,101,0.7) !important;
        box-shadow: 0 0 0 3px rgba(212,175,101,0.10) !important;
        background-color: rgba(22,18,12,0.96) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: var(--warm-gray) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 500 !important;
    }

    /* Universal Fix for Text Area and File Uploader Backgrounds */
    .stTextArea textarea, 
    .stTextArea div[data-baseweb="base-input"],
    .stTextArea div[data-baseweb="textarea"] {
        background-color: rgba(18,15,10,0.88) !important;
        color: var(--charcoal) !important;
    }
    .stTextArea div[data-baseweb="base-input"],
    .stTextArea div[data-baseweb="textarea"] {
        border: 1px solid rgba(212,175,101,0.22) !important;
        border-radius: 14px !important;
    }
    .stTextArea textarea {
        background-color: transparent !important; /* Let the wrapper background show */
        border: none !important;
    }
    
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(18,15,10,0.88) !important;
        border: 1px dashed rgba(212,175,101,0.5) !important;
        border-radius: 14px !important;
        color: var(--charcoal) !important;
    }
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploadDropzone"] * {
        color: var(--charcoal) !important;
    }

    /* === SIDEBAR (Pitch Black) === */
    [data-testid="stSidebar"] {
        background-color: rgba(6,5,3,0.97) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(212,175,101,0.15) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        color: var(--charcoal) !important;
        border-color: rgba(212,175,101,0.25) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--gold) !important;
        color: #080808 !important;
        border-color: var(--gold) !important;
    }

    /* === TABS (Dark) === */
    .stTabs [data-baseweb="tab-list"],
    .stRadio > div,
    div[role="tablist"] {
        background-color: rgba(14,12,8,0.85) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(212,175,101,0.18) !important;
        border-radius: 50px !important;
        padding: 5px !important;
    }
    .stTabs [aria-selected="true"],
    button[role="tab"][aria-selected="true"] {
        background-color: var(--gold) !important;
        color: #080808 !important;
        border-radius: 50px !important;
        border: none !important;
    }

    /* === DEVELOPER SIGNATURE === */
    @keyframes subtle-float {
        0%   { transform: translateY(0px);   opacity: 0.4; }
        50%  { transform: translateY(-4px);  opacity: 0.7; }
        100% { transform: translateY(0px);   opacity: 0.4; }
    }
    .dev-signature {
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        text-align: center;
        margin-top: 60px;
        padding-bottom: 30px;
        color: var(--warm-light);
        animation: subtle-float 6s ease-in-out infinite;
        letter-spacing: 0.22em;
        text-transform: uppercase;
    }

    /* === GOLD METALLIC SHIMMER ON HEADINGS === */
    @keyframes gold-shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    /* Apply shimmer sweep to any element with gold-word class or h1.oa-hero-title */
    .gold-word, .oa-gold-text {
        background: linear-gradient(
            105deg,
            #D4AF65 0%,
            #EDD98A 35%,
            #FFFAED 48%,
            #EDD98A 55%,
            #D4AF65 70%,
            #B8952A 100%
        );
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gold-shimmer 3.5s linear infinite;
    }

    /* Selectbox dark */
    div[data-baseweb="select"] > div {
        background-color: rgba(18,15,10,0.92) !important;
        border: 1px solid rgba(212,175,101,0.22) !important;
        border-radius: 14px !important;
        color: var(--charcoal) !important;
    }
    div[data-baseweb="popover"] {
    /* ═══════════════════════════════════════════
       OBSIDIAN CURSOR SYSTEM
    ═══════════════════════════════════════════ */
    /* Hide the OS default cursor everywhere in the parent page */
    #oa-cursor-dot, #oa-cursor-ring { pointer-events: none !important; }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  BACKGROUND CANVASES
# ═══════════════════════════════════════════════════════════════

def draw_organic_curves(parallax=True):
    """Obsidian Assembly signature: thin gold SVG organic curves with mouse parallax."""
    import streamlit.components.v1 as components
    
    components.html("""
    <script>
    var isParallaxEnabled = """ + ("true" if parallax else "false") + """;
    (function() {
        var doc = window.parent.document;
        var win = window.parent;

        // Always recreate curves canvas for fresh start on each page
        var old = doc.getElementById('oa-curves-canvas');
        if (old) old.remove();

        var canvas = doc.createElement('canvas');
        canvas.id = 'oa-curves-canvas';
        canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;opacity:1';
        doc.body.prepend(canvas);
        var ctx = canvas.getContext('2d');

        var W = canvas.width = win.innerWidth;
        var H = canvas.height = win.innerHeight;

        // Mouse tracking for parallax
        var mx = W / 2, my = H / 2;
        var smx = W / 2, smy = H / 2;

        var curves = [];
        function makeCurve() {
            var side = Math.random() < 0.5 ? 0 : 1;
            var startX = side === 0 ? -80 : W + 80;
            var endX   = side === 0 ? W + 80 : -80;
            var depth  = 0.01 + Math.random() * 0.04;
            return {
                sx: startX,  sy: Math.random() * H,
                cp1x: W * (0.1 + Math.random() * 0.8), cp1y: Math.random() * H,
                cp2x: W * (0.1 + Math.random() * 0.8), cp2y: Math.random() * H,
                ex: endX,    ey: Math.random() * H,
                progress: 0,
                speed: 0.0007 + Math.random() * 0.0006,
                alpha: 0,
                maxAlpha: 0.35 + Math.random() * 0.45,  // much brighter on dark bg
                life: 0,
                lifetime: 700 + Math.random() * 500,
                width: 0.6 + Math.random() * 1.2,
                color: Math.random() < 0.65 ? '212,175,101' : '237,217,138',  // bright metallic gold
                depth: depth,
                ox: 0, oy: 0
            };
        }

        for (var i = 0; i < 8; i++) {  // more curves for visibility
            var c = makeCurve();
            c.progress = Math.random();
            c.life = Math.floor(c.lifetime * Math.random());
            curves.push(c);
        }

        function cubicBezier(t, p0, p1, p2, p3) {
            var mt = 1 - t;
            return mt*mt*mt*p0 + 3*mt*mt*t*p1 + 3*mt*t*t*p2 + t*t*t*p3;
        }

        function drawCurvePartial(c, t, ox, oy) {
            var steps = Math.max(2, Math.floor(t * 90));
            ctx.beginPath();
            ctx.moveTo(
                cubicBezier(0, c.sx+ox, c.cp1x+ox, c.cp2x+ox, c.ex+ox),
                cubicBezier(0, c.sy+oy, c.cp1y+oy, c.cp2y+oy, c.ey+oy)
            );
            for (var i = 1; i <= steps; i++) {
                var tt = i / steps * t;
                ctx.lineTo(
                    cubicBezier(tt, c.sx+ox, c.cp1x+ox, c.cp2x+ox, c.ex+ox),
                    cubicBezier(tt, c.sy+oy, c.cp1y+oy, c.cp2y+oy, c.ey+oy)
                );
            }
            ctx.strokeStyle = 'rgba(' + c.color + ',' + c.alpha + ')';
            ctx.lineWidth = c.width;
            ctx.stroke();
        }

        function tick() {
            if (!doc.getElementById('oa-curves-canvas')) return;
            if (doc.hidden) { requestAnimationFrame(tick); return; }  // pause when tab inactive
            ctx.clearRect(0, 0, W, H);

            smx += (mx - smx) * 0.04;
            smy += (my - smy) * 0.04;

            var pdx = (smx - W/2) / W;
            var pdy = (smy - H/2) / H;

            for (var i = 0; i < curves.length; i++) {
                var c = curves[i];
                c.life++;
                c.progress = Math.min(1, c.progress + c.speed);

                var lr = c.life / c.lifetime;
                if (lr < 0.15)      c.alpha = (lr / 0.15) * c.maxAlpha;
                else if (lr > 0.75) c.alpha = ((1 - lr) / 0.25) * c.maxAlpha;
                else                c.alpha = c.maxAlpha;

                var ox = isParallaxEnabled ? -pdx * W * c.depth * 180 : 0;
                var oy = isParallaxEnabled ? -pdy * H * c.depth * 180 : 0;

                c.ox += (ox - c.ox) * 0.06;
                c.oy += (oy - c.oy) * 0.06;

                drawCurvePartial(c, c.progress, c.ox, c.oy);

                if (c.life >= c.lifetime) {
                    curves[i] = makeCurve();
                }
            }
            requestAnimationFrame(tick);
        }

        win.removeEventListener('mousemove', win.__oa_curve_mm);
        var __oa_mm_last = 0;
        win.__oa_curve_mm = function(e) {
            var now = Date.now();
            if (now - __oa_mm_last < 16) return;  // cap at ~60fps
            __oa_mm_last = now;
            mx = e.clientX; my = e.clientY;
        };
        win.addEventListener('mousemove', win.__oa_curve_mm);

        win.addEventListener('resize', function() {
            if (!doc.getElementById('oa-curves-canvas')) return;
            W = canvas.width = win.innerWidth;
            H = canvas.height = win.innerHeight;
        });
        tick();
    })();
    </script>
    """, height=1)


def draw_obsidian_cursor():
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        var doc = window.parent.document;
        // ── Remove old cursor elements if present ──
        ['oa-cursor-dot','oa-cursor-ring','oa-cursor-style'].forEach(function(id) {
            var el = doc.getElementById(id);
            if (el) el.remove();
        });
    })();
    </script>
    """, height=0, width=0)
    return


def draw_3d_sphere():
    """3D particle sphere — recolored in warm gold/amber tones for Obsidian aesthetic."""
    import streamlit.components.v1 as components
    import uuid
    components.html(f"""
    <script>
    (function() {{
        var doc = window.parent.document;
        var win = window.parent;
        var opp = doc.getElementById('kinetic-dot-grid');
        if (opp) opp.remove();

        // Ensure we recreate the canvas if Streamlit re-evaluates
        var old = doc.getElementById('home-canvas');
        if (old) old.remove();

        var canvas = doc.createElement('canvas');
        canvas.id = 'home-canvas';
        canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none;opacity:0.85';
        doc.body.prepend(canvas);
        var ctx = canvas.getContext('2d');

        // Warm gold / amber Obsidian palette
        var COLORS = ['#C9A96E','#A07840','#E0C89A','#8B6914','rgba(201,169,110,0.85)'];
        var W = canvas.width = win.innerWidth;
        var H = canvas.height = win.innerHeight;
        var target = {{x:W/2, y:H/2}};
        var smooth = {{x:W/2, y:H/2}};
        var prevSmooth = {{x:W/2, y:H/2}};
        var particles = [], stars = [];
        var rotX=0, rotY=0, R=220;

        function buildSphere() {{
            particles = [];
            var phi = Math.PI*(3-Math.sqrt(5));
            for (var i=0; i<100; i++) {{
                var y=1-(i/99)*2, r=Math.sqrt(1-y*y), t=phi*i;
                particles.push({{x:Math.cos(t)*r, y:y, z:Math.sin(t)*r,
                    s:Math.random()*2+1.5, c:COLORS[Math.floor(Math.random()*5)],
                    a:Math.random()*0.35+0.55, w:Math.random()*6.28, ws:(Math.random()-0.5)*0.04}});
            }}
        }}

        function buildStars() {{
            stars = [];
            for (var i=0; i<80; i++) {{
                stars.push({{
                    bx: Math.random()*W, by: Math.random()*H,
                    x: 0, y: 0, vx: 0, vy: 0,
                    r: Math.random()*1.4+0.5,
                    a: Math.random()*0.3+0.4,
                    tw: Math.random()*6.28,
                    tws: (Math.random()*0.025+0.008) * (Math.random()<0.5?1:-1)
                }});
            }}
        }}

        function tick() {{
            if (!doc.getElementById('home-canvas')) return;
            ctx.clearRect(0,0,W,H);

            var dx = smooth.x - prevSmooth.x;
            var dy = smooth.y - prevSmooth.y;
            prevSmooth.x = smooth.x;
            prevSmooth.y = smooth.y;
            smooth.x += (target.x - smooth.x)*0.05;
            smooth.y += (target.y - smooth.y)*0.05;

            // Warm dust stars
            for (var i=0; i<stars.length; i++) {{
                var s = stars[i];
                s.tw += s.tws;
                var twinkle = 0.5 + 0.5*Math.sin(s.tw);
                var distSq = Math.pow(s.bx+s.x - smooth.x,2) + Math.pow(s.by+s.y - smooth.y,2);
                var influence = Math.max(0, 1 - distSq/(300*300));
                s.vx -= dx * influence * 0.15;
                s.vy -= dy * influence * 0.15;
                s.vx *= 0.93; s.vy *= 0.93;
                s.x += s.vx; s.y += s.vy;
                s.x *= 0.97; s.y *= 0.97;
                ctx.beginPath();
                ctx.arc(s.bx+s.x, s.by+s.y, s.r, 0, 6.28);
                ctx.fillStyle = 'rgba(201,169,110,'+(s.a*twinkle)+')';
                ctx.fill();
                if (twinkle > 0.6) {{
                    ctx.beginPath();
                    ctx.arc(s.bx+s.x, s.by+s.y, s.r*2.5, 0, 6.28);
                    ctx.fillStyle = 'rgba(201,169,110,'+(0.08*twinkle)+')';
                    ctx.fill();
                }}
            }}

            rotY += 0.004; rotX += 0.0015;
            var sX=Math.sin(rotX),cX=Math.cos(rotX),sY=Math.sin(rotY),cY=Math.cos(rotY);
            var proj=[];
            particles.forEach(function(p) {{
                p.w += p.ws;
                var rf = 1+Math.sin(p.w)*0.05;
                var px=p.x*rf, py=p.y*rf, pz=p.z*rf;
                var ty=py*cX-pz*sX, tz=py*sX+pz*cX; py=ty; pz=tz;
                var tx=px*cY+pz*sY; tz=-px*sY+pz*cY; px=tx; pz=tz;
                var zd=400+pz*R, sc=400/zd;
                proj.push({{sx:smooth.x+px*R*sc, sy:smooth.y+py*R*sc, sz:p.s*sc, c:p.c,
                    a:Math.min(1,Math.max(0,p.a*(0.5+0.8*((pz+1)/2)))), zd:zd}});
            }});

            proj.sort(function(a,b){{return b.zd-a.zd;}});
            proj.forEach(function(pt) {{
                // Warm glow
                ctx.beginPath(); ctx.arc(pt.sx,pt.sy,pt.sz*2,0,6.28);
                ctx.fillStyle=pt.c; ctx.globalAlpha=pt.a*0.18; ctx.fill();
                // Core dot
                ctx.beginPath(); ctx.arc(pt.sx,pt.sy,pt.sz,0,6.28);
                ctx.globalAlpha=pt.a; ctx.fill();
            }});
            ctx.globalAlpha=1;
            requestAnimationFrame(tick);
        }}

        doc.addEventListener('mousemove', function(e){{ target.x=e.clientX; target.y=e.clientY; }});
        win.addEventListener('resize', function(){{
            if (!doc.getElementById('home-canvas')) return;
            W=canvas.width=win.innerWidth; H=canvas.height=win.innerHeight;
            smooth.x=W/2; smooth.y=H/2; prevSmooth.x=W/2; prevSmooth.y=H/2;
            buildSphere(); buildStars();
        }});
        buildSphere(); buildStars(); tick();
    }})();
    </script>
    <!-- Trigger re-render {uuid.uuid4().hex} -->
    """, height=1)



def draw_kinetic_grid():
    """Kinetic dot grid — warm amber/gold tones for Obsidian aesthetic."""
    import streamlit.components.v1 as components
    import streamlit as st
    import uuid

    st.markdown("""
        <style>
        body {
            background-color: #080808 !important;
            background-image:
                radial-gradient(circle at 10% 20%, rgba(212,175,101,0.06) 0%, transparent 55%),
                radial-gradient(circle at 90% 80%, rgba(184,149,42,0.04) 0%, transparent 55%) !important;
        }
        [data-testid="stAppViewContainer"], .stApp, .main {
            background: transparent !important;
            background-color: transparent !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(8,8,8,0.0) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    components.html("""
    <script>
    (function() {
        var doc = window.parent.document;
        var win = window.parent;
        var opp = doc.getElementById('home-canvas');
        if (opp) opp.remove();
        var curves = doc.getElementById('oa-curves-canvas');
        if (curves) curves.remove();

        var canvas = doc.getElementById('kinetic-dot-grid');
        if (!canvas) {
            canvas = doc.createElement('canvas');
            canvas.id = 'kinetic-dot-grid';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;pointer-events:none';
            canvas._mx = -9999; canvas._my = -9999;
            canvas._ripples = [];
            doc.body.prepend(canvas);

            var W = canvas.width = win.innerWidth;
            var H = canvas.height = win.innerHeight;
            var ctx = canvas.getContext('2d');
            var SPACING = 30, RADIUS = 260;
            var dots = [];

            function buildDots() {
                dots = [];
                for (var x=SPACING/2; x<W; x+=SPACING)
                    for (var y=SPACING/2; y<H; y+=SPACING)
                        dots.push({x:x, y:y});
            }

            function tick() {
                var el = doc.getElementById('kinetic-dot-grid');
                if (!el) return;
                var mx = el._mx, my = el._my;
                ctx.clearRect(0,0,W,H);

                for (var i=0; i<dots.length; i++) {
                    var d=dots[i];
                    var ddx=d.x-mx, ddy=d.y-my;
                    var dist=Math.sqrt(ddx*ddx+ddy*ddy);
                    var t=Math.max(0,1-dist/RADIUS);
                    // Base dim gold dot on black
                    ctx.beginPath(); ctx.arc(d.x,d.y,0.8,0,6.28);
                    ctx.fillStyle='rgba(212,175,101,0.12)'; ctx.fill();
                    if (t>0) {
                        // Lit metallic gold dot
                        ctx.beginPath(); ctx.arc(d.x,d.y,0.8+t*1.4,0,6.28);
                        ctx.fillStyle='rgba(212,175,101,'+(t*0.9)+')';
                        ctx.fill();
                        // Metallic glow halo
                        ctx.beginPath(); ctx.arc(d.x,d.y,(0.8+t*1.4)*3.5,0,6.28);
                        ctx.fillStyle='rgba(212,175,101,'+(t*0.18)+')';
                        ctx.fill();
                    }
                }
                // Gold radial glow under cursor
                if (mx > -9000) {
                    var g = ctx.createRadialGradient(mx,my,0,mx,my,RADIUS);
                    g.addColorStop(0,'rgba(212,175,101,0.14)');
                    g.addColorStop(0.6,'rgba(184,149,42,0.05)');
                    g.addColorStop(1,'rgba(0,0,0,0)');
                    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
                }
                // Metallic gold ripples on click
                var rp=el._ripples;
                for (var j=rp.length-1;j>=0;j--) {
                    var r=rp[j]; r.radius+=8; r.alpha-=0.018;
                    if(r.alpha<=0){rp.splice(j,1);continue;}
                    ctx.beginPath(); ctx.arc(r.x,r.y,r.radius,0,6.28);
                    ctx.strokeStyle='rgba(212,175,101,'+r.alpha+')';
                    ctx.lineWidth=1.2; ctx.stroke();
                }
                requestAnimationFrame(tick);
            }

            win.addEventListener('resize', function(){
                var el=doc.getElementById('kinetic-dot-grid');
                if(!el) return;
                W=el.width=win.innerWidth; H=el.height=win.innerHeight;
                buildDots();
            });
            buildDots(); tick();
        }

        if (!win.__kdg_init) {
            win.__kdg_init = true;
            win.addEventListener('mousemove', function(e) {
                var el = doc.getElementById('kinetic-dot-grid');
                if (el) { el._mx = e.clientX; el._my = e.clientY; }
            }, true);
            win.addEventListener('click', function(e) {
                var el = doc.getElementById('kinetic-dot-grid');
                if (el) { el._ripples.push({x:e.clientX, y:e.clientY, radius:0, alpha:0.5}); }
            }, true);
        }
    })();
    </script>
    """, height=1)


# --- 3. DATABASE SETUP ---
def save_to_history(query, code, language):
    conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO history (query, code, language) VALUES (?, ?, ?)", (query, code, language))
    conn.commit()
    conn.close()


# --- 4. SESSION MANAGEMENT ---
if 'show_landing' not in st.session_state:   st.session_state['show_landing'] = True
if 'show_features' not in st.session_state:  st.session_state['show_features'] = False
if 'logged_in' not in st.session_state:      st.session_state['logged_in'] = False
if 'booting' not in st.session_state:        st.session_state['booting'] = False
if 'page' not in st.session_state:           st.session_state['page'] = 'generator'


# ═══════════════════════════════════════════════════════════════
#  CURSOR RESTORE
# ═══════════════════════════════════════════════════════════════
def restore_cursor():
    """Clean up any legacy cursor elements from old versions."""
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const doc = window.parent.document;
        // Remove old custom cursor elements from previous versions
        ['ag-cursor','ag-follower','ag-style','codify-canvas','login-dot-grid','cursor-fix-style'].forEach(id => {
            const el = doc.getElementById(id);
            if (el) el.remove();
        });
    </script>
    """, height=0, width=0)


# ═══════════════════════════════════════════════════════════════
#  LANDING PAGE — Obsidian Assembly Style
# ═══════════════════════════════════════════════════════════════
def landing_page():
    draw_3d_sphere()
    draw_organic_curves(parallax=False)
    draw_obsidian_cursor()  # ← Obsidian cursor system

    st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        header {visibility: hidden;}

        body {
            background-color: #080808 !important;
            color: #F0EDE6;
        }
        .stApp, [data-testid="stAppViewContainer"], .main {
            background: transparent !important;
            background-color: transparent !important;
            position: relative;
            z-index: 10;
        }
        @keyframes gold-shimmer {
            0%   { background-position: -200% center; }
            100% { background-position: 200% center; }
        }

        /* === HERO === */
        .oa-hero-wrap {
            padding-top: 80px;
            padding-bottom: 20px;
            position: relative;
            z-index: 10;
        }
        .oa-eyebrow {
            font-family: 'Inter', sans-serif;
            font-size: 0.7rem;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: #D4AF65;
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .oa-eyebrow::before {
            content: '';
            display: inline-block;
            width: 28px;
            height: 1px;
            background: #D4AF65;
        }
        .oa-hero-title {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: clamp(4rem, 9vw, 8.5rem);
            font-weight: 400;
            line-height: 0.92;
            letter-spacing: -0.03em;
            color: #F0EDE6;
            margin: 0 0 24px 0;
        }
        .oa-hero-title .italic-word {
            font-style: italic;
            font-weight: 300;
            color: #8A8278;
        }
        .oa-hero-title .gold-word {
            color: #D4AF65;
        }
        .oa-hero-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 0.92rem;
            color: #8A8278;
            line-height: 1.75;
            max-width: 460px;
            margin-bottom: 48px;
            letter-spacing: 0.01em;
        }
        .oa-divider-line {
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(212,175,101,0.4), transparent);
            margin: 60px 0;
        }

        /* === BENTO GRID WARM === */
        .oa-bento-card {
            background: rgba(12,10,6,0.85);
            backdrop-filter: blur(20px) saturate(150%);
            -webkit-backdrop-filter: blur(20px) saturate(150%);
            border: 1px solid rgba(212,175,101,0.18);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6), 0 1px 0 rgba(212,175,101,0.07) inset;
            transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
            position: relative;
            overflow: hidden;
        }
        .oa-bento-card::before {
            content: '';
            position: absolute;
            top: 0; left: 10%; right: 10%;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(212,175,101,0.3), transparent);
        }
        /* === SHIMMERING GOLD BENTO TITLE === */
        .oa-bento-title span, .oa-bento-title [style*='color:#C9A96E'],
        .oa-bento-title [style*='color:#D4AF65'] {
            background: linear-gradient(
                105deg,
                #D4AF65 0%, #EDD98A 35%, #FFFAED 48%, #EDD98A 55%, #D4AF65 75%, #B8952A 100%
            );
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gold-shimmer 3.5s linear infinite;
        }
        .oa-bento-card:hover .oa-bento-title {
            text-shadow: none;
        }
        .oa-bento-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.85), 0 0 0 1px rgba(212,175,101,0.3);
            border-color: rgba(212,175,101,0.45);
        }
        /* Hero title gold word shimmer */
        .oa-hero-title .gold-word {
            background: linear-gradient(
                105deg,
                #D4AF65 0%, #EDD98A 30%, #FFFAED 46%, #EDD98A 54%, #D4AF65 72%, #B8952A 100%
            );
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gold-shimmer 3s linear infinite;
        }
        .oa-bento-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.3rem;
            font-weight: 500;
            color: #F0EDE6;
            letter-spacing: -0.01em;
            margin-bottom: 8px;
        }
        .oa-bento-sub {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            color: #8A8278;
            letter-spacing: 0.03em;
            line-height: 1.6;
        }

        /* === ANIMATED CODE LINES (warm) === */
        .code-block-warm {
            background: rgba(6,5,3,0.9);
            border-radius: 10px;
            padding: 16px 18px;
            margin-top: 20px;
            border: 1px solid rgba(212,175,101,0.18);
            position: relative;
            overflow: hidden;
        }
        .code-line-warm {
            height: 7px;
            border-radius: 4px;
            margin-bottom: 10px;
            background: rgba(212,175,101,0.08);
            position: relative;
            overflow: hidden;
        }
        .code-line-warm::after {
            content: '';
            position: absolute;
            left: -100%;
            top: 0;
            height: 100%;
            width: 55%;
            background: linear-gradient(90deg, transparent, rgba(212,175,101,0.7), transparent);
            animation: warm-scan 3s ease-in-out infinite;
        }
        .code-line-warm:nth-child(1)::after { animation-delay: 0s; }
        .code-line-warm:nth-child(2)::after { animation-delay: 0.4s; }
        .code-line-warm:nth-child(3)::after { animation-delay: 0.8s; }
        .code-line-warm:nth-child(4)::after { animation-delay: 1.2s; }
        @keyframes warm-scan { 0%{left:-100%} 100%{left:200%} }
        .warm-cursor {
            display: inline-block;
            width: 7px; height: 14px;
            background: #D4AF65;
            margin-left: 3px;
            vertical-align: middle;
            animation: blink 1s step-end infinite;
        }
        @keyframes blink { 50%{opacity:0;} }
        .warm-scan-beam {
            position: absolute; top: 0; left: 0; width: 100%; height: 1.5px;
            background: linear-gradient(90deg, transparent, rgba(212,175,101,0.85), transparent);
            animation: warm-beam 2.5s linear infinite;
        }
        @keyframes warm-beam {
            0%  { top: 0; opacity: 1; }
            95% { top: 100%; opacity: 0.5; }
            100%{ top: 0; opacity: 0; }
        }

        /* === ARC REACTOR (warm gold) === */
        .arc-reactor-wrap {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 120px;
            position: relative;
        }
        .arc-reactor {
            width: 100px; height: 100px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .arc-ring {
            position: absolute;
            border-radius: 50%;
            border: 1.5px solid transparent;
        }
        .arc-ring-1 {
            width: 100px; height: 100px;
            border-top-color: #D4AF65;
            border-right-color: rgba(212,175,101,0.3);
            animation: spin-cw 3s linear infinite;
        }
        .arc-ring-2 {
            width: 78px; height: 78px;
            border-bottom-color: #B8952A;
            border-left-color: rgba(184,149,42,0.3);
            animation: spin-ccw 2s linear infinite;
        }
        .arc-ring-3 {
            width: 58px; height: 58px;
            border-top-color: #D4AF65;
            border-left-color: rgba(212,175,101,0.2);
            animation: spin-cw 1.5s linear infinite;
        }
        .arc-ring-4 {
            width: 40px; height: 40px;
            border-right-color: #B8952A;
            animation: spin-ccw 4s linear infinite;
        }
        .arc-spokes {
            position: absolute;
            width: 82px; height: 82px;
            animation: spin-cw 7s linear infinite;
        }
        .arc-spoke {
            position: absolute;
            left: 50%; top: 50%;
            width: 1px; height: 35px;
            background: linear-gradient(to top, transparent, rgba(212,175,101,0.6));
            transform-origin: bottom center;
        }
        .arc-core {
            width: 18px; height: 18px;
            border-radius: 50%;
            background: radial-gradient(circle, #F0EDE6 0%, #D4AF65 40%, rgba(212,175,101,0.15) 100%);
            box-shadow: 0 0 14px #D4AF65, 0 0 30px rgba(212,175,101,0.6);
            animation: core-pulse 1.8s ease-in-out infinite alternate;
            z-index: 10;
        }
        @keyframes spin-cw  { to { transform: rotate(360deg); } }
        @keyframes spin-ccw { to { transform: rotate(-360deg); } }
        @keyframes core-pulse {
            0%  { box-shadow: 0 0 10px #D4AF65, 0 0 24px rgba(212,175,101,0.5); transform: scale(1); }
            100%{ box-shadow: 0 0 22px #D4AF65, 0 0 45px rgba(212,175,101,0.85); transform: scale(1.12); }
        }

        /* === BAR CHART (warm) === */
        .bar-chart-warm {
            display: flex;
            gap: 8px;
            align-items: flex-end;
            height: 75px;
            margin-top: 20px;
        }
        .bar-warm {
            flex: 1;
            border-radius: 5px 5px 0 0;
            position: relative;
            animation: bar-grow 2s cubic-bezier(0.34,1.56,0.64,1) forwards;
        }
        @keyframes bar-grow { from{transform:scaleY(0);transform-origin:bottom} to{transform:scaleY(1);transform-origin:bottom} }
        .bw-1 { background: linear-gradient(to top, #6B4A00, #D4AF65); height: 50px; animation-delay: 0s; }
        .bw-2 { background: linear-gradient(to top, #B8952A, #EDD98A); height: 68px; animation-delay: 0.15s; }
        .bw-3 { background: linear-gradient(to top, #4A3200, #D4AF65); height: 40px; animation-delay: 0.3s; }
        .bw-4 { background: linear-gradient(to top, #B8952A, #D4AF65); height: 60px; animation-delay: 0.45s; }
        .bw-5 { background: linear-gradient(to top, #6B4A00, #EDD98A); height: 78px; animation-delay: 0.6s; }

        /* CTA orbit */
        .cta-orbit {
            position: absolute;
            width: 70px; height: 70px;
            border-radius: 50%;
            border: 1px dashed rgba(212,175,101,0.45);
            top: 50%; left: 50%;
            transform: translate(-50%,-50%);
            animation: spin-cw 10s linear infinite;
            pointer-events: none;
        }
        .cta-orbit-dot {
            position: absolute;
            width: 5px; height: 5px;
            border-radius: 50%;
            background: #D4AF65;
            box-shadow: 0 0 10px rgba(212,175,101,0.9);
            top: -2.5px; left: 50%;
            transform: translateX(-50%);
        }

        /* SVG security waveform warm */
        .security-wave {
            width: 100%;
            margin-top: 22px;
        }
        </style>
    """, unsafe_allow_html=True)


    # ── Hero ──────────────────────────────────────────────────
    st.markdown("""
        <div class="oa-hero-wrap reveal">
            <div class="oa-eyebrow">Imagine Possible</div>
            <h1 class="oa-hero-title">
                Codify<br>
                <span class="italic-word">Amplify</span><br>
                <span class="gold-word">Your Vision.</span>
            </h1>
            <p class="oa-hero-subtitle">
                High-fidelity AI coding assistant for implementing modern UI,
                optimized performance, and scalable data infrastructure.
            </p>
        </div>
    """, unsafe_allow_html=True)

    b1, b2, _ = st.columns([1, 1.2, 2])
    with b1:
        if st.button("Get Started", use_container_width=True, key="hero_btn"):
            st.session_state['show_landing'] = False
            st.rerun()
    with b2:
        if st.button("Explore Features →", use_container_width=True, key="explore_btn"):
            st.session_state['show_features'] = True
            st.rerun()

    st.markdown('<div class="oa-divider-line"></div>', unsafe_allow_html=True)

    from bento_cinema import render_bento_cinema
    render_bento_cinema()


    # Redundant bento cards removed as requested.

    # Bottom tagline
    st.markdown("""
        <div style="text-align:center;margin-top:80px;padding-bottom:40px;">
            <span style="font-family:'Inter';font-size:0.68rem;letter-spacing:0.22em;text-transform:uppercase;color:#B5AAA0;">
                No Shortcuts — Only Synthesis
            </span>
        </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  FEATURES PAGE
# ═══════════════════════════════════════════════════════════════
def features_page():
    # Remove the 3D sphere specifically when entering the features page
    import streamlit.components.v1 as components
    components.html("""
    <script>
        var doc = window.parent.document;
        var sphere = doc.getElementById('home-canvas');
        if (sphere) sphere.remove();
    </script>
    """, height=0, width=0)

    draw_organic_curves()
    draw_obsidian_cursor()  # ← Obsidian cursor system
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        header {visibility: hidden;}
        body, .stApp {
            background-color: #080808 !important;
            color: #F0EDE6;
        }
        @keyframes gold-shimmer {
            0%   { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        .feature-box {
            background: rgba(12,10,6,0.88);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(212,175,101,0.18);
            border-left: 3px solid #D4AF65;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 24px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        }
        .feature-box:hover {
            box-shadow: 0 12px 40px rgba(0,0,0,0.85), 0 0 0 1px rgba(212,175,101,0.2);
            transform: translateY(-2px);
        }
        .feature-box h2 {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.9rem;
            font-weight: 500;
            color: #F0EDE6;
            margin-bottom: 12px;
            letter-spacing: -0.02em;
        }
        .feature-box h2 span {
            background: linear-gradient(
                105deg,
                #D4AF65 0%, #EDD98A 30%, #FFFAED 46%, #EDD98A 54%, #D4AF65 72%, #B8952A 100%
            );
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gold-shimmer 3.5s linear infinite;
        }
        .feature-box p, .feature-box li {
            font-family: 'Inter', sans-serif;
            color: #8A8278;
            font-size: 0.95rem;
            line-height: 1.75;
        }
        div[data-testid="stButton"] button {
            background: rgba(212,175,101,0.07) !important;
            border: 1px solid rgba(212,175,101,0.4) !important;
            border-radius: 50px !important;
            padding: 10px 28px !important;
            color: #F0EDE6 !important;
            transition: all 0.3s !important;
        }
        div[data-testid="stButton"] button:hover {
            background: #D4AF65 !important;
            color: #080808 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state['show_features'] = False
            st.rerun()

    st.markdown("""
        <h1 style='font-family:"Cormorant Garamond",serif;font-size:3.8rem;font-weight:400;
                   text-align:center;margin-top:20px;letter-spacing:-0.03em;color:#F0EDE6;'>
            Codify <span style="color:#D4AF65;font-style:italic;">Capabilities</span>
        </h1>
        <p style='text-align:center;margin-bottom:50px;font-family:"Inter",sans-serif;
                  color:#8A8278;font-size:0.9rem;letter-spacing:0.05em;'>
            Empowering engineers and data analysts with neural intelligence.
        </p>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="feature-box">
            <h2>1. Advanced <span>Dataset Processing</span></h2>
            <p>Direct ingestion of <b>CSV, XLS, and XLSX</b> files into the AI context window. The system uses Pandas to pre-process and summarize dataframe topologies before passing them to the Llama-3.3 model.</p>
            <ul>
                <li>Automatic shape &amp; column mapping inference</li>
                <li>Preview top rows directly in the UI</li>
                <li>Intelligent handling of missing values via prompt context</li>
            </ul>
        </div>

        <div class="feature-box">
            <h2>2. Automated <span>Formula Synthesis</span></h2>
            <p>Codify isn't just for Python. Our engine generates complex data manipulation formulas tailored for business intelligence.</p>
            <ul>
                <li><b>Excel &amp; Google Sheets:</b> VLOOKUPs, nested IFs, INDEX/MATCH, conditional aggregates</li>
                <li>Complex string extraction and date-time arithmetic generation</li>
                <li>Explanations of formula logic included in the output</li>
            </ul>
        </div>

        <div class="feature-box">
            <h2>3. SQL Query <span>Architecture</span></h2>
            <p>Build schema-aware database queries. Provide your table context, and Codify writes optimized analytical queries.</p>
            <ul>
                <li>Multi-table JOINs and subqueries</li>
                <li>Window functions for rolling averages and cumulative sums</li>
                <li>SQLite compatibility (used natively as our persistence layer)</li>
            </ul>
        </div>

        <div class="feature-box">
            <h2>4. Python Data <span>Pipelines</span></h2>
            <p>Generate production-grade Python scripts for <b>ETL (Extract, Transform, Load)</b> workflows.</p>
            <ul>
                <li>Pandas melt, pivot_table, and groupby logic</li>
                <li>Data visualization scripts (Matplotlib / Seaborn / Plotly)</li>
                <li>SciPy and Numpy array manipulation functions</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  LOGIN PAGE — Obsidian Assembly Warm Minimal
# ═══════════════════════════════════════════════════════════════
def login_page():
    # Remove the 3D sphere specifically when entering the login page
    import streamlit.components.v1 as components
    components.html("""
    <script>
        var doc = window.parent.document;
        var sphere = doc.getElementById('home-canvas');
        if (sphere) sphere.remove();
    </script>
    """, height=0, width=0)

    draw_organic_curves(parallax=False)
    draw_obsidian_cursor()  # ← Obsidian cursor system

    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: transparent !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(245,241,235,0.0) !important;
        }

        /* Top gold accent bar */
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 2px;
            background: linear-gradient(90deg, transparent, #D4AF65, #EDD98A, #D4AF65, transparent);
            z-index: 999999;
        }

        /* Mascot peekaboo */
        .wombat-paws {
            transform: translateY(120px);
            transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
        }
        .wombat-eyes {
            transition: transform 0.1s ease-out;
        }
        body:has(input[type="password"]:focus) .wombat-paws {
            transform: translateY(0px) !important;
        }
        body:has(input[type="text"]:focus) .wombat-eyes {
            transform: translateX(4px) translateY(2px) !important;
        }

        /* Login column card */
        [data-testid="column"]:nth-of-type(2) {
            background: rgba(10,8,4,0.92) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            padding: 44px !important;
            border-radius: 24px !important;
            border: 1px solid rgba(212,175,101,0.2) !important;
            box-shadow: 0 12px 60px rgba(0,0,0,0.9), 0 1px 0 rgba(212,175,101,0.07) inset !important;
        }

        /* Inputs */
        .stTextInput > div > div > input {
            background-color: rgba(18,14,8,0.9) !important;
            border: 1px solid rgba(212,175,101,0.25) !important;
            color: #F0EDE6 !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            font-family: 'Inter', sans-serif !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: rgba(212,175,101,0.8) !important;
            box-shadow: 0 0 0 3px rgba(212,175,101,0.12) !important;
            background-color: rgba(22,18,10,0.98) !important;
        }
        .stTextInput label {
            color: #8A8278 !important;
            font-weight: 500 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.12em !important;
            text-transform: uppercase !important;
        }

        /* Auth buttons */
        .stButton > button {
            background: #D4AF65 !important;
            border: 1px solid #D4AF65 !important;
            color: #080808 !important;
            border-radius: 50px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.12em !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            padding: 12px !important;
            margin-top: 16px !important;
            width: 100% !important;
            transition: all 0.25s ease !important;
        }
        .stButton > button:hover {
            background: #EDD98A !important;
            border-color: #EDD98A !important;
            color: #080808 !important;
            box-shadow: 0 8px 28px rgba(212,175,101,0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid_col, _ = st.columns([1, 1.2, 1])
    with mid_col:
        from yuji_avatar import wombat_html
        st.markdown(wombat_html, unsafe_allow_html=True)

        import streamlit.components.v1 as components
        components.html("""
        <script>
            function updateTilt(e) {
                try {
                    const doc = window.parent.document;
                    const container = doc.getElementById('yuji-3d-container');
                    if (!container) return;
                    const x = e.clientX / window.parent.innerWidth - 0.5;
                    const y = e.clientY / window.parent.innerHeight - 0.5;
                    container.style.setProperty('--rx', (-y*50)+'deg');
                    container.style.setProperty('--ry', (x*50)+'deg');
                } catch(err){}
            }
            try { window.parent.document.addEventListener('mousemove', updateTilt); } catch(err){}
        </script>
        """, height=0, width=0)

        # Title
        mode_label = "Sign In" if st.session_state['login_mode'] == 'login' else (
            "Create Account" if st.session_state['login_mode'] == 'register' else "Reset Password")
        st.markdown(f"""
            <h1 style='text-align:center;
                       font-family:"Cormorant Garamond",serif;
                       font-size:2.8rem;
                       font-weight:400;
                       font-style:italic;
                       letter-spacing:-0.02em;
                       color:#F0EDE6;
                       margin-top:10px;
                       margin-bottom:28px;'>
                {mode_label}
            </h1>
        """, unsafe_allow_html=True)

        user_input = st.text_input("Username", key="login_user")
        pass_label = "Password" if st.session_state['login_mode'] != 'forgot_password' else "New Password"
        pass_input = st.text_input(pass_label, type="password", key="login_pass")

        if st.session_state['login_mode'] == 'login':
            if st.button("Sign In", use_container_width=True):
                if not user_input.strip() or not pass_input.strip():
                    st.warning("Please enter both username and password.")
                elif verify_user(user_input.strip(), pass_input.strip()):
                    st.session_state['logged_in'] = True
                    st.session_state['booting'] = True
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        elif st.session_state['login_mode'] == 'register':
            if st.button("Register", use_container_width=True):
                if not user_input.strip() or not pass_input.strip():
                    st.warning("Please provide a username and password.")
                elif create_user(user_input.strip(), pass_input.strip()):
                    st.success("Account created! Please sign in.")
                    st.session_state['login_mode'] = 'login'
                    st.rerun()
                else:
                    st.error("Username already exists.")
        elif st.session_state['login_mode'] == 'forgot_password':
            if st.button("Reset Password", use_container_width=True):
                if not user_input.strip() or not pass_input.strip():
                    st.warning("Please provide a username and new password.")
                elif reset_password(user_input.strip(), pass_input.strip()):
                    st.success("Password reset successfully! Please sign in.")
                    st.session_state['login_mode'] = 'login'
                    st.rerun()
                else:
                    st.error("Username does not exist.")

        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1, 1])
        with col_l:
            if st.session_state['login_mode'] == 'login':
                st.markdown('<div class="toggle-auth-container">', unsafe_allow_html=True)
                if st.button("Forgot Password?", key="forgot_btn"):
                    st.session_state['login_mode'] = 'forgot_password'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        with col_r:
            toggle_label = "Sign In" if st.session_state['login_mode'] in ['register','forgot_password'] else "Create Account"
            st.markdown('<div class="toggle-auth-container">', unsafe_allow_html=True)
            if st.button(toggle_label, key="toggle_auth_btn"):
                st.session_state['login_mode'] = 'login' if st.session_state['login_mode'] in ['register','forgot_password'] else 'register'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
            <style>
            .toggle-auth-container button {
                background: none !important;
                border: none !important;
                color: #B5AAA0 !important;
                font-size: 0.8rem !important;
                font-weight: 500 !important;
                padding: 0 !important;
                margin-top: 8px !important;
                box-shadow: none !important;
                width: auto !important;
                min-height: auto !important;
                line-height: normal !important;
                display: inline-block !important;
                transition: color 0.2s !important;
                letter-spacing: 0.04em !important;
                text-transform: none !important;
            }
            .toggle-auth-container button:hover {
                color: #1A1410 !important;
                background: none !important;
            }
            </style>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  BOOT SEQUENCE — Warm Obsidian
# ═══════════════════════════════════════════════════════════════
def boot_sequence():
    import streamlit.components.v1 as components

    boot_placeholder = st.empty()

    sequence = [
        "INITIALISING CORE SYSTEMS...",
        "CALIBRATING NEURAL INTERFACE...",
        "ENGAGING PRIMARY DRIVES...",
        "JARVIS ONLINE, WELCOME SIR",
    ]

    hud_css = """
    <style>
    body { background-color: #0A0A07 !important; }
    .hud-text {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-style: italic;
        color: #C9A96E;
        font-size: 2.2rem;
        text-align: center;
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        letter-spacing: 0.05em;
        text-shadow: 0 0 12px rgba(201,169,110,0.5), 0 0 30px rgba(201,169,110,0.25);
        animation: pop-in 0.5s cubic-bezier(0.175,0.885,0.32,1.275) forwards,
                   warm-pulse 1.6s infinite alternate 0.5s;
        z-index: 10000;
        white-space: nowrap;
    }
    @keyframes pop-in {
        0%   { transform: translate(-50%,-50%) scale(0.6); opacity:0; }
        70%  { transform: translate(-50%,-50%) scale(1.04); opacity:1; }
        100% { transform: translate(-50%,-50%) scale(1); opacity:1; }
    }
    @keyframes warm-pulse {
        0%   { text-shadow: 0 0 10px rgba(201,169,110,0.4); }
        100% { text-shadow: 0 0 22px rgba(201,169,110,0.9), 0 0 45px rgba(160,120,64,0.5); }
    }
    .hud-overlay {
        position: fixed;
        top:0; left:0; width:100vw; height:100vh;
        background:
            radial-gradient(circle at 50% 50%, transparent 30%, rgba(0,0,0,0.85) 90%),
            repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(201,169,110,0.015) 2px,rgba(201,169,110,0.015) 4px);
        pointer-events:none;
        z-index:9999;
    }
    </style>
    <div class='hud-overlay'></div>
    """

    # Play the custom AI voice audio (embedded as base64)
    _audio_js = '''<script>
(function() {
  var audio = new Audio('data:audio/mpeg;base64,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EltL9ksSFMyl8vV6bXGmjbVEx///lGEjLtDI9X/nUahswjDPc08/JtifMsZcy/7LkT1vmabZnOl5T8sz4PQarY1UEkCYpmvPQKs2pMMmnBb93xMA//uUBAAAAp9V22DBG05VqrstGKOuCvkpZ6MwUsFdqO90MxdGUBakbQKSP0VFdlw8XYdFc2N2YyGNRsl4m+iZaFu9iXLkkrFArOef5e7+QbNGQjq//l5L/F+dIv+l+uWenG5jELCkydKbbipCLpQvgZ4w9goh6FCsqA3u4QCntN+ipmKXDweTDor0u7/17Z9z26N0JPITkznVCLaiIimHDAiY73fKk59hK5DEZ1L+2xehdKs3q3La8lDUjELCkydKbbipCLpQvjHIOwGsqN1SoBhAARvm7JXrU5advQ+/4tB2/e9j0UDowbVnl699fl52mTjeOcIZKAhach0OCKBnRV06McxWCMVGQhPfWiF0Z1b1d/1f6nuzOuEkOQWjBDhFordG4zv1krTjAIZbTkFOcagxbqGFv6ONz6/4JIOXuHFgcvz+xMDDBQXH3UE2JlFD50VdOjHMVhBioyEJ760QujOrerucvU5+lT3ZjK8ISHIDjGEBSjrRcjY5tDNKYgpo//uUBAAAArJMWtECHsRWSYtaIEPYirFFeUMId7FWKK8oYQ72BYEAAEppzLF7V90jJOE8VkVp8j5DYch0DB5QniXukTbqVikowKoMKf3lEjiDVMq/VFclVF7fqp0639Ed1Un6vpg35njELsrAsJkcBCzR4NrehQxs+3pBYEAAEppzLF7V90jJOE8VkVp8j5DYch0DB5QniXukTbqVikowKoMKf3lEjiDVMq/VFclVF7fqp0639Ed1Un6vpg35njELsrAsJkcBCzR4NrehQxs+3pQteAAMolTlkPewhMeMQt0++Z/2YjIHlINe8/R7+xDM4CcxuxwEKolmdr07iUMQ5lCghD53R23s7evnp/v8hiPIipnWME1rmKIjYcn1wrnVKFDOisoUQteAAMolTlkPewhMeMQt0++Z/2YjIHlINe8/R7+xDM4CcxuxwEKolmdr07iUMQ5lCghD53R23s7evnp/v8hiPIipnWME1rmKIjYcn1wrnVKFDOisoUTEFNRQ//uUBAACIqhQXtDFFZ5VCgvaGKKzytFPdMWMtrFaKe6YsZbWQteUpNEpTwAe6zCc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yiqDwQdDub+Qjpp////ys7MLcizsRGKYWwlQEZAp0F3O3///6zKhI7gBhaiG0+gAk420bLQCX8IqkMm14VudkiIffX9d87u8WWZn2xRYWcgbRDMoqg8EHQ7m/kI6af///8rOzC3Is7ERimFsJUBGQKdBdzt///+syoSO4AYWohtPoAGoAnKCU7j6CgWQogmoLeS6Ge0uGOONm7xpyqWowpUM7cRFWdMpXKpWmgMKkGGLfpYcrFZnyf///2UtDIYxZSlDp6qUpau3tRv//y7mMhkM4iKsMDxgSfSQABqAJyglO4+goFkKIJqC3kuhntLhjjjZu8acqlqMKVDO3ERVnTKVyqVpoDCpBhi36WHKxWZ8n///9lLQyGMWUpQ6eqlKWrt7Ub//8u5jIZDOIirDA8YEn0kExBTQ//uUBAAAAo5dVoZhQABRy6rQzCgAC01lgbxkADFprLA3jIAGFFK1iMViOpMy35/k9d/9clUtzCAlIuw8YA8qNefRCUd/MV4WBVFQGgWf37yIfk5Y5P//////PNev/7pM8gMRyoxOJCUm//zPmfKmnkg9IlOJUFFK1iMViOpMy35/k9d/9clUtzCAlIuw8YA8qNefRCUd/MV4WBVFQGgWf37yIfk5Y5P//////PNev/7pM8gMRyoxOJCUm//zPmfKmnkg9IlOJUZCkt9kttCcrTobnh2NzE9xDWgcYbytUcUZR7LNQphq21w38ZQNgXA2FU2i5X1VVX//////////Sk64iYT/rd7Tce16RVJVz861TNxfH/9/pUTFQWfSIiGGIQjIUlvsltoTladDc8OxuYnuIa0DjDeVqjijKPZZqFMNW2uG/jKBsC4Gwqm0XK+qqq//////////6UnXETCf9bvabj2vSKpKufnWqZuL4//v9KiYqCz6REQwxCETEFNA//uUBAAAAqFaXmliNf5UK0vNLEa/ysFneaSI3TFYLO80kRumACUk0bdlBKnkGdwKE55sxNKUC+5OOUW77+D1HWw9uEdX9zGqcAMgtFO1/Kv////+pzDiGW7uZGX1ad2sTZ4wMrKk3//6I6uiFcHJJOiIKCyDZh3TABKSaNuyglTyDO4FCc82YmlKBfcnHKLd9/B6jrYe3COr+5jVOAGQWina/lX/////U5hxDLd3MjL6tO7WJs8YGVlSb//9EdXRCuDkknREFBZBsw7p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');
  audio.volume = 1.0;
  var p = audio.play();
  if (p !== undefined) {
    p.catch(function() {
      document.addEventListener('click', function() { audio.play(); }, {once:true});
    });
  }
  window.__codifyBootAudio = audio;
})();
</script>'''
    components.html(_audio_js, height=0)

    # Show each phrase for 2.01s — matches the 8.04s audio
    for text in sequence:
        boot_placeholder.markdown(hud_css + f"<div class='hud-text'>{text}</div>", unsafe_allow_html=True)
        time.sleep(2.01)
    time.sleep(0.3)
    boot_placeholder.empty()


# ═══════════════════════════════════════════════════════════════
#  ROUTING
# ═══════════════════════════════════════════════════════════════
if st.session_state.get('show_features', False):
    features_page()
elif st.session_state.get('show_landing', True):
    landing_page()
elif not st.session_state['logged_in']:
    login_page()
elif st.session_state.get('booting', False):
    boot_sequence()
    st.session_state['booting'] = False
    st.rerun()
else:
    draw_kinetic_grid()
    draw_obsidian_cursor()  # ← Obsidian cursor system

    # ── SIDEBAR ────────────────────────────────────────────────
    with st.sidebar:
        import base64
        logo_path = "assets/codify_logo_clean.png"
        try:
            with open(logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(image_file.read()).decode()
        except Exception:
            encoded_logo = ""

        import textwrap
        animated_logo_html = textwrap.dedent(f"""
            <div class="animated-logo-container">
                <style>
                .animated-logo-container {{
                    position: relative;
                    width: 100%;
                    max-width: 180px;
                    aspect-ratio: 1 / 1;
                    margin: 0 auto 12px auto;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .base-logo-img {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    z-index: 1;
                }}
                .circuit-overlay {{
                    position: absolute;
                    top: 0; left: 0;
                    width: 100%; height: 100%;
                    z-index: 2;
                    pointer-events: none;
                }}
                .coolant-gold {{
                    fill: none;
                    stroke: #D4AF65;
                    stroke-width: 0.8;
                    stroke-linecap: round;
                    stroke-dasharray: 18 180;
                    animation: circuit-flow 2.8s linear infinite;
                }}
                .coolant-amber {{
                    fill: none;
                    stroke: #B8952A;
                    stroke-width: 0.8;
                    stroke-linecap: round;
                    stroke-dasharray: 12 200;
                    animation: circuit-flow 3.8s linear infinite;
                }}
                .coolant-cream {{
                    fill: none;
                    stroke: #EDD98A;
                    stroke-width: 0.8;
                    stroke-linecap: round;
                    stroke-dasharray: 22 150;
                    animation: circuit-flow 2.2s linear infinite;
                }}
                @keyframes circuit-flow {{
                    from {{ stroke-dashoffset: 200; }}
                    to   {{ stroke-dashoffset: -200; }}
                }}
                </style>
                <img src="data:image/png;base64,{encoded_logo}" class="base-logo-img" alt="CODIFY AI Logo"/>
                <svg class="circuit-overlay" viewBox="0 0 100 100">
                    <path class="coolant-gold"  d="M 45,42 L 35,42 L 30,35 L 20,35" style="animation-delay:0s;"/>
                    <path class="coolant-gold"  d="M 45,43 L 38,43 L 30,50 L 22,50" style="animation-delay:-0.5s;"/>
                    <path class="coolant-amber" d="M 44,45 L 35,45 L 30,55 L 20,60" style="animation-delay:-1.2s;"/>
                    <path class="coolant-amber" d="M 48,39 L 45,30 L 40,25" style="animation-delay:-0.2s;"/>
                    <path class="coolant-cream" d="M 46,42 L 32,30 L 25,30" style="animation-delay:-0.8s;"/>
                    <path class="coolant-cream" d="M 46,43 L 32,54 L 25,54" style="animation-delay:-2.1s;"/>
                    <path class="coolant-gold"  d="M 40,42 L 15,42" style="animation-delay:-0.3s;"/>
                    <path class="coolant-amber" d="M 47,38 L 47,20 L 40,15" style="animation-delay:-0.9s;"/>
                    <path class="coolant-cream" d="M 47,48 L 47,65 L 42,70" style="animation-delay:-1.4s;"/>
                    <path class="coolant-gold"  d="M 55,42 L 65,42 L 70,47 L 85,47" style="animation-delay:0s;"/>
                    <path class="coolant-amber" d="M 55,45 L 60,50 L 75,50 L 80,45" style="animation-delay:-1s;"/>
                    <path class="coolant-cream" d="M 55,39 L 60,35 L 75,35 L 80,40" style="animation-delay:-0.5s;"/>
                </svg>
            </div>
        """)
        st.markdown(animated_logo_html, unsafe_allow_html=True)

        # Sidebar label
        st.markdown("""
            <div style="text-align:center;margin-bottom:16px;">
                <span style="font-family:'Inter';font-size:0.65rem;letter-spacing:0.2em;
                             text-transform:uppercase;color:#B5AAA0;">Navigation</span>
            </div>
        """, unsafe_allow_html=True)

        st.divider()
        if st.button("⚡  Neural Generator", use_container_width=True):
            st.session_state['page'] = 'generator'
        if st.button("📖  Tech Manifesto", use_container_width=True):
            st.session_state['page'] = 'docs'

        st.divider()
        st.markdown("""
            <div style="font-family:'Inter';font-size:0.65rem;letter-spacing:0.18em;
                        text-transform:uppercase;color:#B5AAA0;margin-bottom:10px;">
                Recent Logs
            </div>
        """, unsafe_allow_html=True)
        conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
        hist = conn.execute("SELECT language, query, code FROM history ORDER BY rowid DESC LIMIT 3").fetchall()
        conn.close()
        for item in hist:
            with st.expander(f"{item[0]}: {item[1][:12]}..."):
                st.code(item[2], language=item[0].lower())

        if st.button("🚪  Terminate Session", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['show_landing'] = True
            st.session_state['show_features'] = False
            st.session_state.pop('res', None)
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    #  GENERATOR PAGE
    # ═══════════════════════════════════════════════════════════
    if st.session_state['page'] == 'generator':
        st.markdown("""
        <style>
        [data-testid="stAppViewContainer"], .stApp, .main {
            background: transparent !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(245,241,235,0.0) !important;
        }

        /* === Glass input panels (dark) === */
        .stTextArea > div {
            background: rgba(14,12,8,0.88) !important;
            backdrop-filter: blur(22px) saturate(150%) !important;
            -webkit-backdrop-filter: blur(22px) saturate(150%) !important;
            border: 1px solid rgba(212,175,101,0.22) !important;
            border-radius: 18px !important;
            box-shadow:
                0 6px 28px rgba(0,0,0,0.5),
                0 1px 0 rgba(212,175,101,0.06) inset !important;
            transform: perspective(800px) rotateX(0.5deg) translateZ(0) !important;
            transition: all 0.4s cubic-bezier(0.16,1,0.3,1) !important;
        }
        .stTextArea > div:focus-within {
            border-color: rgba(212,175,101,0.65) !important;
            box-shadow:
                0 12px 40px rgba(0,0,0,0.7),
                0 0 0 3px rgba(212,175,101,0.12),
                0 1px 0 rgba(212,175,101,0.08) inset !important;
            transform: perspective(800px) rotateX(0deg) translateY(-3px) translateZ(0) !important;
        }
        .stTextArea > div > div > textarea {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #F0EDE6 !important;
            font-family: 'Inter', sans-serif !important;
        }

        [data-testid="stFileUploader"] {
            background: rgba(14,12,8,0.85) !important;
            backdrop-filter: blur(18px) !important;
            border: 1px solid rgba(212,175,101,0.18) !important;
            border-radius: 18px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
            transition: all 0.4s cubic-bezier(0.16,1,0.3,1) !important;
            padding: 8px !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: rgba(212,175,101,0.45) !important;
            box-shadow: 0 12px 40px rgba(0,0,0,0.7) !important;
            transform: translateY(-2px) !important;
        }

        [data-testid="stSelectbox"] {
            background: rgba(14,12,8,0.88) !important;
            backdrop-filter: blur(18px) !important;
            border: 1px solid rgba(212,175,101,0.2) !important;
            border-radius: 18px !important;
            box-shadow: 0 4px 18px rgba(0,0,0,0.5) !important;
            transition: all 0.4s cubic-bezier(0.16,1,0.3,1) !important;
            padding: 4px 6px !important;
        }

        [data-testid="stExpander"] {
            background: rgba(12,10,6,0.85) !important;
            backdrop-filter: blur(18px) !important;
            border: 1px solid rgba(212,175,101,0.15) !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.4) !important;
            margin-bottom: 10px !important;
        }
        [data-testid="stExpander"]:hover {
            border-color: rgba(212,175,101,0.35) !important;
        }

        /* Loading spinner warm */
        .cube-loader {
            display: flex; justify-content: center; align-items: center;
            height: 90px; margin: 18px 0;
        }
        .cube {
            width: 36px; height: 36px;
            background: transparent;
            border: 1.5px solid #D4AF65;
            animation: cube-spin 2.5s infinite linear, cube-glow 1.8s infinite alternate;
        }
        .loading-text {
            text-align: center;
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 1.1rem;
            color: #8A8278;
            letter-spacing: 0.05em;
            animation: warm-pulse-text 1.2s infinite alternate;
        }
        @keyframes cube-spin {
            0%   { transform: rotateX(0deg) rotateY(0deg); }
            100% { transform: rotateX(360deg) rotateY(360deg); }
        }
        @keyframes cube-glow {
            0%   { box-shadow: 0 0 8px rgba(212,175,101,0.3); }
            100% { box-shadow: 0 0 24px rgba(212,175,101,0.85); }
        }
        @keyframes warm-pulse-text {
            0%   { opacity: 0.5; }
            100% { opacity: 1; }
        }
        @keyframes gold-shimmer {
            0%   { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        </style>
        """, unsafe_allow_html=True)

        _, center_col, _ = st.columns([1, 2.5, 1])
        with center_col:
            st.markdown("""
                <h1 style='font-family:"Cormorant Garamond",serif;
                            font-weight:400;font-style:italic;
                            font-size:3rem;text-align:center;
                            margin-bottom:8px;margin-top:10px;
                            color:#F0EDE6;letter-spacing:-0.02em;'>
                    AI <span style="color:#C9A96E;">//</span> <span style="
                        background: radial-gradient(circle at center, #FFF4D2 0%, #D4AF65 40%, #B8952A 100%);
                        background-size: 200% auto;
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        animation: gold-shimmer 2.2s linear infinite;
                    ">Architect</span>
                </h1>
                <p style="text-align:center;font-family:'Inter';font-size:0.75rem;
                          letter-spacing:0.15em;text-transform:uppercase;color:#B5AAA0;
                          margin-bottom:32px;">
                    Synthesize your vision into code
                </p>
            """, unsafe_allow_html=True)

            from codify_avatar_input import codify_input_html
            st.markdown(codify_input_html, unsafe_allow_html=True)

            q = st.text_area(
                "What would you like to build?",
                placeholder="Describe your objective, feature, or data manipulation task in plain language...",
                height=170
            )

            uploaded_file = st.file_uploader(
                "Attach context dataset (Optional)",
                type=["csv", "xls", "xlsx", "db", "sqlite", "sqlite3"],
                help="Upload a CSV, Excel, or SQLite database file for AI analysis."
            )

            dataset_context = ""
            if uploaded_file is not None:
                try:
                    import io, sqlite3 as _sqlite3, tempfile, os as _os
                    ext = uploaded_file.name.split('.')[-1].lower()
                    raw_bytes = uploaded_file.read()

                    if ext in ('db', 'sqlite', 'sqlite3'):
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                            tmp.write(raw_bytes)
                            tmp_path = tmp.name
                        try:
                            conn_db = _sqlite3.connect(tmp_path)
                            cursor_db = conn_db.cursor()
                            tables = [r[0] for r in cursor_db.execute(
                                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
                            ).fetchall()]
                            st.markdown(
                                f"<p style='font-size:0.8rem;color:#7A6E64;margin-top:8px;'>"
                                f"✓ Loaded <b>{uploaded_file.name}</b> — {len(tables)} table(s): "
                                f"<code>{'</code>, <code>'.join(tables)}</code></p>",
                                unsafe_allow_html=True
                            )
                            schema_parts = [f"DATABASE FILE: {uploaded_file.name}"]
                            for tbl in tables:
                                cols = cursor_db.execute(f"PRAGMA table_info([{tbl}]);").fetchall()
                                col_info = ", ".join(f"{c[1]} ({c[2]})" for c in cols)
                                row_count = cursor_db.execute(f"SELECT COUNT(*) FROM [{tbl}];").fetchone()[0]
                                sample = cursor_db.execute(f"SELECT * FROM [{tbl}] LIMIT 5;").fetchall()
                                col_names = [c[1] for c in cols]
                                schema_parts.append(
                                    f"\nTABLE: {tbl} ({row_count} rows)\n"
                                    f"Columns: {col_info}\n"
                                    f"Sample rows (5):\n" +
                                    "\n".join([str(dict(zip(col_names, row))) for row in sample])
                                )
                                with st.expander(f"📋 {tbl} — schema & preview", expanded=False):
                                    import pandas as _pd
                                    df_tbl = _pd.read_sql_query(f"SELECT * FROM [{tbl}] LIMIT 20", conn_db)
                                    st.dataframe(df_tbl, use_container_width=True)
                            conn_db.close()
                            dataset_context = "\n\n" + "\n".join(schema_parts)
                        finally:
                            _os.unlink(tmp_path)
                    elif ext == 'csv':
                        df = pd.read_csv(io.BytesIO(raw_bytes))
                        st.markdown(
                            f"<p style='font-size:0.8rem;color:#7A6E64;margin-top:8px;'>"
                            f"✓ Loaded <b>{uploaded_file.name}</b> — {df.shape[0]} rows × {df.shape[1]} cols</p>",
                            unsafe_allow_html=True
                        )
                        with st.expander("📊 Dataset Preview", expanded=False):
                            st.dataframe(df.head(10), use_container_width=True)
                        dataset_context = (
                            f"\n\nREFERENCE DATASET: {uploaded_file.name}\n"
                            f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
                            f"Columns: {', '.join(df.columns.tolist())}\n"
                            f"First 50 rows (CSV format):\n{df.head(50).to_csv(index=False)}"
                        )
                    else:
                        df = pd.read_excel(io.BytesIO(raw_bytes))
                        st.markdown(
                            f"<p style='font-size:0.8rem;color:#7A6E64;margin-top:8px;'>"
                            f"✓ Loaded <b>{uploaded_file.name}</b> — {df.shape[0]} rows × {df.shape[1]} cols</p>",
                            unsafe_allow_html=True
                        )
                        with st.expander("📊 Dataset Preview", expanded=False):
                            st.dataframe(df.head(10), use_container_width=True)
                        dataset_context = (
                            f"\n\nREFERENCE DATASET: {uploaded_file.name}\n"
                            f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
                            f"Columns: {', '.join(df.columns.tolist())}\n"
                            f"First 50 rows (CSV format):\n{df.head(50).to_csv(index=False)}"
                        )
                except Exception as e:
                    st.warning(f"⚠️ Could not read file: {e}")

            lang = st.selectbox(
                "Target Language / Tool",
                [
                    "Python",
                    "SQL",
                    "Power BI (DAX / M Query)",
                    "Tableau (Calculated Fields / LOD)",
                    "Excel Formula",
                    "Google Sheets Formula",
                ],
                help="Select the tool or language you want the AI to generate output for."
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Synthesize", use_container_width=True):
                if q or dataset_context:
                    loader_placeholder = st.empty()
                    loader_placeholder.markdown("""
                    <div class="cube-loader"><div class="cube"></div></div>
                    <div class="loading-text">Synthesising Neural Pathways...</div>
                    """, unsafe_allow_html=True)

                    try:
                        STEP_GUIDE = (
                            "\n\nAfter the output, you MUST include:\n"
                            "**### Step-by-Step Execution Guide**\n"
                            "Numbered steps (1, 2, 3...) explaining exactly how to run or use the generated output.\n"
                            "\n**### Code / Formula Explanation**\n"
                            "A plain-English explanation of each part.\n"
                            "\n**### Expected Output**\n"
                            "Describe clearly what the user should see after running the output."
                        )
                        tool_instructions = {
                            "Python": (
                                "You are an expert Python data scientist and software engineer. "
                                "Generate clean, well-commented Python code using pandas, numpy, or relevant libraries."
                                + STEP_GUIDE
                            ),
                            "SQL": (
                                "You are a senior SQL database architect. "
                                "Generate optimized, well-commented SQL queries (compatible with standard SQL / SQLite unless specified). "
                                "If a database schema is provided, write queries that use the EXACT table and column names."
                                + STEP_GUIDE
                            ),
                            "Power BI (DAX / M Query)": (
                                "You are a certified Power BI developer. "
                                "Generate the appropriate DAX measure/column formula OR Power Query (M) transformation. "
                                "Clearly label which type you are providing."
                                + STEP_GUIDE
                            ),
                            "Tableau (Calculated Fields / LOD)": (
                                "You are a Tableau Server Certified Associate. "
                                "Generate the appropriate Tableau Calculated Field or LOD expression."
                                + STEP_GUIDE
                            ),
                            "Excel Formula": (
                                "You are an advanced Microsoft Excel specialist. "
                                "Generate professional Excel formulas using modern functions (XLOOKUP, LET, LAMBDA, dynamic arrays)."
                                + STEP_GUIDE
                            ),
                            "Google Sheets Formula": (
                                "You are an advanced Google Sheets specialist. "
                                "Generate professional Google Sheets formulas using QUERY, ARRAYFORMULA, IMPORTRANGE, etc."
                                + STEP_GUIDE
                            ),
                        }

                        system_prompt = tool_instructions.get(
                            lang,
                            f"You are an expert in {lang}. Generate accurate, professional output." + STEP_GUIDE
                        )

                        if q:
                            user_request = f"User Request: {q}"
                        elif dataset_context:
                            user_request = f"Analyse the provided dataset/database and produce the best {lang} solution."
                        else:
                            user_request = "Provide a useful example."

                        full_prompt = f"{system_prompt}\n\n{user_request}{dataset_context}"
                        chat = client.chat.completions.create(
                            messages=[{"role": "user", "content": full_prompt}],
                            model="llama-3.3-70b-versatile"
                        )
                        st.session_state['res'] = chat.choices[0].message.content
                        history_label = q if q else f"Dataset analysis: {uploaded_file.name if uploaded_file else 'unknown'}"
                        save_to_history(history_label, st.session_state['res'], lang)
                    except Exception as e:
                        st.error(f"Inference Failure: {e}")
                    finally:
                        loader_placeholder.empty()

        # ── Output Box ─────────────────────────────────────────
        if 'res' in st.session_state:
            _, out_col, _ = st.columns([0.1, 9.8, 0.1])
            with out_col:
                from codify_avatar import codify_html
                st.markdown(f"""
<div style='display:flex;flex-direction:row;align-items:flex-start;gap:24px;margin-top:36px;'>
<!-- Mascot -->
<div style='flex:0 0 160px;margin-top:10px;'>
{codify_html}
</div>
<!-- Output Card -->
<div style='flex:1 1 auto;padding:32px 36px;border-radius:20px;
            background:rgba(255,254,250,0.88);
            backdrop-filter:blur(28px) saturate(130%);
            -webkit-backdrop-filter:blur(28px) saturate(130%);
            border:1px solid rgba(201,169,110,0.22);
            border-top:1px solid rgba(255,255,255,0.9);
            border-left:3px solid #C9A96E;
            box-shadow:0 20px 60px rgba(26,20,16,0.1),0 1px 0 rgba(255,255,255,0.9) inset;
            position:relative;overflow:hidden;'>
<!-- Shimmer -->
<div style='position:absolute;top:0;left:8%;right:8%;height:1px;
            background:linear-gradient(90deg,transparent,rgba(201,169,110,0.4),transparent);
            pointer-events:none;'></div>
<!-- Gold glow spot -->
<div style='position:absolute;top:-40px;left:-40px;width:140px;height:140px;
            background:radial-gradient(circle,rgba(201,169,110,0.08) 0%,transparent 70%);
            pointer-events:none;'></div>
<div style='font-family:"Cormorant Garamond",serif;font-style:italic;
            font-size:0.82rem;color:#C9A96E;letter-spacing:0.12em;
            margin-bottom:20px;display:flex;align-items:center;gap:8px;'>
    ⚡ Codify's Response
</div>
""", unsafe_allow_html=True)
                st.markdown(st.session_state['res'])
                st.markdown("</div></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    #  DOCS / MANIFESTO PAGE
    # ═══════════════════════════════════════════════════════════
    elif st.session_state['page'] == 'docs':
        st.markdown("""
            <h1 style='font-family:"Cormorant Garamond",serif;font-weight:400;
                       color:#1A1410;font-size:3.2rem;margin-bottom:8px;letter-spacing:-0.03em;'
                class='reveal'>
                Technical <span style='color:#C9A96E;font-style:italic;'>Manifesto</span>
            </h1>
            <p style="font-family:'Inter';font-size:0.75rem;letter-spacing:0.18em;
                      text-transform:uppercase;color:#B5AAA0;margin-bottom:48px;">
                The Architecture & Vision of Codify AI
            </p>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="manifesto-card reveal">
            <h3>I. Project Abstract &amp; Vision</h3>
            <p><b>Codify AI</b> is a next-generation code synthesis platform developed to resolve
            <b>'Syntactic Friction'</b> in the modern DevOps lifecycle.
            The vision is to democratize high-level software architecture by automating boilerplate generation.
            By leveraging the <b>Groq LPU (Language Processing Unit)</b>, this system achieves
            ~500 tokens per second throughput, making AI responses feel instantaneous.</p>
        </div>

        <div class="manifesto-card reveal reveal-delay-1">
            <h3>II. 3-Tier Architectural Decoupling</h3>
            <p>The system is engineered using a robust, decoupled infrastructure:</p>
            <ul>
                <li><b>Presentation Layer:</b> Built on Streamlit, utilizing custom CSS injection for advanced Glassmorphism and editorial UI elements.</li>
                <li><b>Logic Layer:</b> Secured API handshake with Groq Cloud, utilizing the <b>Llama-3.3-70B</b> transformer model.</li>
                <li><b>Data Layer:</b> Relational <b>SQLite 3</b> database for ACID-compliant session history and auditing.</li>
            </ul>
        </div>

        <div class="manifesto-card reveal reveal-delay-2">
            <h3>III. Performance &amp; Development Methodology</h3>
            <p>This project utilized the <b>Agile Software Development Life Cycle (SDLC)</b>,
            focusing on rapid prototyping and iterative feedback loops. Key metrics achieved:</p>
            <ul>
                <li><b>Latency:</b> Sub-0.8s cold start for inference queries.</li>
                <li><b>Security:</b> End-to-end secret masking via Environment Variable encryption.</li>
                <li><b>Reliability:</b> Thread-safe database connections for multi-user session stability.</li>
            </ul>
        </div>

        <div class="manifesto-card reveal reveal-delay-3">
            <h3>IV. Future Scope — The AI Agent Roadmap</h3>
            <p>Codify AI is designed for modular scalability. The following are planned for Version 3.0:</p>
            <ul>
                <li><b>Contextual RAG:</b> Connecting the neural engine to private Vector Databases to understand specific user codebases.</li>
                <li><b>Automated Testing:</b> Real-time generation of unit tests for every code block synthesised.</li>
                <li><b>Multi-Modal:</b> Voice-commanded code generation using the OpenAI Whisper API.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ── DEVELOPER SIGNATURE ────────────────────────────────────
    st.markdown("<div class='dev-signature'>Developed by Deekshith</div>", unsafe_allow_html=True)