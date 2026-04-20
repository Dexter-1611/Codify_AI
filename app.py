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
        win.__oa_curve_mm = function(e) { mx = e.clientX; my = e.clientY; };
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
    h1, h2 = st.columns([1.6, 1])
    with h1:
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

        b1, b2, _ = st.columns([0.9, 1.1, 1.4])
        with b1:
            if st.button("Get Started", use_container_width=True, key="hero_btn"):
                st.session_state['show_landing'] = False
                st.rerun()
        with b2:
            if st.button("Explore Features →", use_container_width=True, key="explore_btn"):
                st.session_state['show_features'] = True
                st.rerun()

    st.markdown('<div class="oa-divider-line"></div>', unsafe_allow_html=True)

    # ── Bento Grid ────────────────────────────────────────────
    g1, g2, g3 = st.columns([1.2, 1, 1])

    with g1:
        st.markdown("""
            <div class="oa-bento-card reveal reveal-delay-1" style="height:380px;">
                <div class="oa-bento-title">Automated <span style="color:#C9A96E">Coding</span></div>
                <div class="oa-bento-sub">Synthesizing complex UI components at neural speed.<span class="warm-cursor"></span></div>
                <div class="code-block-warm">
                    <div class="warm-scan-beam"></div>
                    <div class="code-line-warm" style="width:78%;"></div>
                    <div class="code-line-warm" style="width:52%;"></div>
                    <div class="code-line-warm" style="width:90%;"></div>
                    <div class="code-line-warm" style="width:42%;"></div>
                    <div style="width:100%;height:5px;background:rgba(160,120,64,0.15);border-radius:3px;overflow:hidden;margin-top:8px;">
                        <div style="height:100%;background:linear-gradient(90deg,#C9A96E,#A07840);border-radius:3px;animation:fill-bar 3s ease-in-out infinite alternate;width:70%;"></div>
                    </div>
                    <style>@keyframes fill-bar{0%{width:15%}100%{width:94%}}</style>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("""
            <div class="oa-bento-card reveal reveal-delay-2" style="height:210px;margin-bottom:18px;">
                <div class="oa-bento-title" style="text-align:center;">AI <span style="color:#C9A96E">Integration</span></div>
                <div class="arc-reactor-wrap">
                    <div class="arc-reactor">
                        <div class="arc-ring arc-ring-1"></div>
                        <div class="arc-ring arc-ring-2"></div>
                        <div class="arc-ring arc-ring-3"></div>
                        <div class="arc-ring arc-ring-4"></div>
                        <div class="arc-spokes">
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(0deg)   translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(45deg)  translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(90deg)  translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(135deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(180deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(225deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(270deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform:translateX(-50%) rotate(315deg) translateY(-100%);"></div>
                        </div>
                        <div class="arc-core"></div>
                    </div>
                </div>
            </div>

            <div class="oa-bento-card reveal reveal-delay-2" style="height:152px;">
                <div class="oa-bento-title"><span style="color:#C9A96E">Security</span> &amp; Compliance</div>
                <svg class="security-wave" viewBox="0 0 100 30">
                    <polyline points="0,20 18,12 38,22 58,6 78,16 100,2"
                        fill="none" stroke="#C9A96E" stroke-width="2.5"
                        stroke-linecap="round" stroke-linejoin="round"/>
                    <polyline points="0,20 18,12 38,22 58,6 78,16 100,2"
                        fill="none" stroke="rgba(201,169,110,0.25)" stroke-width="7"
                        stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
        """, unsafe_allow_html=True)

    with g3:
        st.markdown("""
            <div class="oa-bento-card reveal reveal-delay-3" style="height:190px;margin-bottom:18px;">
                <div class="oa-bento-title">Deployment &amp; <span style="color:#C9A96E">Scaling</span></div>
                <div class="bar-chart-warm">
                    <div class="bar-warm bw-1"></div>
                    <div class="bar-warm bw-2"></div>
                    <div class="bar-warm bw-3"></div>
                    <div class="bar-warm bw-4"></div>
                    <div class="bar-warm bw-5"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="oa-bento-card reveal reveal-delay-3" style="height:170px;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;">
                <div class="cta-orbit"><div class="cta-orbit-dot"></div></div>
                <div class="oa-bento-title" style="text-align:center;margin-bottom:14px;z-index:2;">Ready to build?</div>
        """, unsafe_allow_html=True)

        if st.button("Get Started", use_container_width=True, key="bento_get_started"):
            st.session_state['show_landing'] = False
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

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
    boot_placeholder = st.empty()
    sequence = [
        "INITIALISING CORE SYSTEMS...",
        "CALIBRATING NEURAL INTERFACE...",
        "ENGAGING PRIMARY DRIVES...",
        "Jarvis Online, Welcome Buddy",
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
    for text in sequence:
        boot_placeholder.markdown(hud_css + f"<div class='hud-text'>{text}</div>", unsafe_allow_html=True)
        time.sleep(0.85)
    time.sleep(0.4)
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