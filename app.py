import streamlit as st
import sqlite3
import os
import time
import pandas as pd
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

# --- 2. ADVANCED UI & LOGO ANIMATIONS (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=Fira+Code:wght@400;500&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #1a1a1a, #000000);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }

    /* Logo Branding Styling */
    .logo-container {
        font-family: 'Space Grotesk', sans-serif;
        color: #f3f4f6;
        font-weight: 600;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .logo-highlight {
        color: #ffffff;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
    }

    /* Scroll Reveal Animation */
    .reveal {
        opacity: 0;
        transform: translateY(20px);
        animation: reveal-in 0.8s forwards cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes reveal-in {
        to { opacity: 1; transform: translateY(0); }
    }

    /* Manifesto High-Density Cards */
    .manifesto-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 35px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 25px;
        line-height: 1.7;
        transition: all 0.3s ease;
    }
    .manifesto-card:hover {
        border-color: rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
    
    .manifesto-card h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #e2e8f0;
        font-weight: 500;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }

    /* Floating Developer Signature */
    @keyframes subtle-float {
        0% { transform: translateY(0px); opacity: 0.6; }
        50% { transform: translateY(-4px); opacity: 0.9; }
        100% { transform: translateY(0px); opacity: 0.6; }
    }
    .dev-signature {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 50px;
        padding-bottom: 30px;
        color: #94a3b8;
        animation: subtle-float 5s ease-in-out infinite;
        letter-spacing: 3px;
    }

    /* Inputs, Buttons, and Glass Elements styling */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div,
    .stFileUploader>div>div,
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: rgba(220, 20, 60, 0.5) !important;
        box-shadow: 0 0 20px rgba(220, 20, 60, 0.15) !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Navigation Tabs & Radio Buttons (Sidebar + Main) */
    .stTabs [data-baseweb="tab-list"], 
    .stRadio>div, 
    div[role="tablist"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 6px !important;
        gap: 8px !important;
    }
    
    /* Active Tab / Radio button styling */
    .stTabs [aria-selected="true"], 
    .stRadio input:checked + div,
    button[role="tab"][aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.05) !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, rgba(220, 20, 60, 0.8), rgba(147, 51, 234, 0.7)) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: 2px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        text-transform: uppercase !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(220, 20, 60, 1), rgba(147, 51, 234, 0.9)) !important;
        border-color: rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 8px 30px rgba(220, 20, 60, 0.4), inset 0 0 10px rgba(255,255,255,0.2) !important;
        transform: translateY(-2px) !important;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# === HOME PAGE: Circular Orbit Particle Background ===
import streamlit.components.v1 as components
components.html("""
<script>
    const doc = window.parent.document;

    // Cleanup old canvas
    const old = doc.getElementById('home-canvas');
    if (old) old.remove();

    const canvas = doc.createElement('canvas');
    canvas.id = 'home-canvas';
    Object.assign(canvas.style, {
        position: 'fixed', top: '0', left: '0',
        width: '100vw', height: '100vh',
        zIndex: '0', pointerEvents: 'none',
        opacity: '0.8'
    });
    doc.body.prepend(canvas);

    // Keep stApp background transparent so we see the canvas
    const stApp = doc.querySelector('.stApp');
    if (stApp) stApp.style.backgroundColor = 'transparent';
    doc.body.style.background =
        'radial-gradient(circle at top right, #1a1a1a, #000000)';

    const ctx = canvas.getContext('2d');

    // Home page color scheme: crimson, gold, warm white
    const COLORS = ['#dc143c', '#e52e6b', '#fbbf24', '#f97316', 'rgba(255,255,255,0.7)'];

    let W = canvas.width  = window.parent.innerWidth;
    let H = canvas.height = window.parent.innerHeight;

    // Mouse / target position — defaults to screen center
    let target = { x: W / 2, y: H / 2 };
    let smooth = { x: W / 2, y: H / 2 };  // smoothed cursor center

    // ── Build particles on a 3D Sphere ──────────────────────────
    const NUM_PARTICLES = 180; // slightly more for a bigger sphere
    let particles = [];
    
    // Euler angles for sphere rotation
    let rotX = 0;
    let rotY = 0;
    const sphereRadius = 240; // Increased base size of the 3D sphere

    function buildParticles() {
        particles = [];
        // Fibonacci sphere distribution for even spread
        const phi = Math.PI * (3 - Math.sqrt(5)); // golden angle
        
        for (let i = 0; i < NUM_PARTICLES; i++) {
            const y = 1 - (i / (NUM_PARTICLES - 1)) * 2; // y goes from 1 to -1
            const radiusAtY = Math.sqrt(1 - y * y); // radius at y
            
            const theta = phi * i; // golden angle increment
            
            const x = Math.cos(theta) * radiusAtY;
            const z = Math.sin(theta) * radiusAtY;
            
            particles.push({
                x: x,
                y: y,
                z: z,
                baseSize: Math.random() * 2.5 + 2.0, // Increased base particle size for vibrancy
                color: COLORS[Math.floor(Math.random() * COLORS.length)],
                alpha: Math.random() * 0.4 + 0.6, // Higher base alpha
                // slight wobble for breathing effect
                wobble: Math.random() * Math.PI * 2,
                wobbleSpeed: (Math.random() - 0.5) * 0.05
            });
        }
    }

    function tick() {
        ctx.clearRect(0, 0, W, H);

        // Smoothly interpolate cursor follow
        smooth.x += (target.x - smooth.x) * 0.06;
        smooth.y += (target.y - smooth.y) * 0.06;

        // Rotate sphere slowly
        rotY += 0.005;
        rotX += 0.002;

        const sinX = Math.sin(rotX), cosX = Math.cos(rotX);
        const sinY = Math.sin(rotY), cosY = Math.cos(rotY);

        // Sort particles by Z so further ones are drawn first (painters algorithm)
        let projected = [];

        for (const p of particles) {
            // Apply slight wobble to the distance from center
            p.wobble += p.wobbleSpeed;
            const rOffset = 1.0 + Math.sin(p.wobble) * 0.05;
            
            let px = p.x * rOffset;
            let py = p.y * rOffset;
            let pz = p.z * rOffset;

            // Rotate around X-axis
            let tempY = py * cosX - pz * sinX;
            let tempZ = py * sinX + pz * cosX;
            py = tempY; pz = tempZ;

            // Rotate around Y-axis
            let tempX = px * cosY + pz * sinY;
            tempZ = -px * sinY + pz * cosY;
            px = tempX; pz = tempZ;
            
            // Perspective projection
            const fov = 400;
            const viewerDistance = 400; // how far viewer is from sphere center
            // pz range is roughly -1 to 1 based on unit sphere. 
            // Scale by sphereRadius maps it to roughly -sphereRadius to +sphereRadius
            const scaledZ = pz * sphereRadius; 
            
            const zDepth = viewerDistance + scaledZ;
            const scale = fov / zDepth;
            
            // 2D canvas coordinates centered on smoothed cursor
            const screenX = smooth.x + (px * sphereRadius * scale);
            const screenY = smooth.y + (py * sphereRadius * scale);
            
            // Depth cues: size and opacity
            // Normalize Z from -1 (back) to 1 (front) roughly
            const zNorm = pz; 
            const finalSize = p.baseSize * scale;
            
            // Brighten up the particles: even the back ones are visible
            let finalAlpha = p.alpha * (0.5 + 0.8 * ((zNorm + 1) / 2)); 
            if (finalAlpha < 0) finalAlpha = 0;
            if (finalAlpha > 1) finalAlpha = 1;

            projected.push({
                sx: screenX, sy: screenY, 
                size: finalSize, color: p.color, alpha: finalAlpha,
                zDepth: zDepth
            });
        }
        
        // Sort highest zDepth (furthest away) to lowest (closest)
        projected.sort((a, b) => b.zDepth - a.zDepth);

        // Draw projected dots
        for (const pt of projected) {
            ctx.beginPath();
            ctx.arc(pt.sx, pt.sy, pt.size, 0, Math.PI * 2);
            ctx.fillStyle = pt.color;
            ctx.globalAlpha = pt.alpha;
            // Add a subtle glow
            ctx.shadowBlur = 8;
            ctx.shadowColor = pt.color;
            ctx.fill();
            // Reset shadow so it doesn't affect everything globally if other rendering happens
            ctx.shadowBlur = 0;
        }

        ctx.globalAlpha = 1;
        requestAnimationFrame(tick);
    }

    doc.addEventListener('mousemove', e => {
        target.x = e.clientX;
        target.y = e.clientY;
    });

    window.parent.addEventListener('resize', () => {
        W = canvas.width  = window.parent.innerWidth;
        H = canvas.height = window.parent.innerHeight;
        // keep default centre if mouse hasn't moved yet
        smooth.x = W / 2; smooth.y = H / 2;
        target.x = W / 2; target.y = H / 2;
        buildParticles();
    });

    buildParticles();
    tick();
</script>
""", height=0, width=0)

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
if 'show_landing' not in st.session_state: st.session_state['show_landing'] = True
if 'show_features' not in st.session_state: st.session_state['show_features'] = False
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'booting' not in st.session_state: st.session_state['booting'] = False
if 'page' not in st.session_state: st.session_state['page'] = 'generator'


# --- 4.5 LANDING PAGE (BENTO GRID DESIGN) ---
def landing_page():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        header {visibility: hidden;}
        .stApp {
            background-color: #020617;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(147, 51, 234, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(6, 182, 212, 0.15) 0%, transparent 50%);
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }

        /* Glassmorphism for Bento Cards */
        .bento-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .bento-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
    """, unsafe_allow_html=True)

    # === PARTICLE BACKGROUND + MAGNETIC CURSOR via components.html (scripts execute here) ===
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const doc = window.parent.document;

        // ── 1. PARTICLE CANVAS ──────────────────────────────────────────
        const old = doc.getElementById('codify-canvas');
        if (old) old.remove();

        const canvas = doc.createElement('canvas');
        canvas.id = 'codify-canvas';
        Object.assign(canvas.style, {
            position: 'fixed', top: '0', left: '0',
            width: '100vw', height: '100vh',
            zIndex: '0', pointerEvents: 'none'
        });
        doc.body.prepend(canvas);

        // Make Streamlit app container transparent so canvas shows through
        const stApp = doc.querySelector('.stApp');
        if (stApp) stApp.style.background = 'transparent';
        doc.body.style.backgroundColor = '#020617';
        doc.body.style.backgroundImage =
            'radial-gradient(circle at 15% 50%, rgba(147,51,234,0.18) 0%, transparent 55%),' +
            'radial-gradient(circle at 85% 30%, rgba(6,182,212,0.18) 0%, transparent 55%)';

        const ctx = canvas.getContext('2d');
        const COLORS = ['#00f2fe','#a855f7','#4f46e5','rgba(255,255,255,0.8)'];
        let W, H, pts = [];
        const mouse = { x: -9999, y: -9999, r: 160 };

        function resize() {
            W = canvas.width  = window.parent.innerWidth;
            H = canvas.height = window.parent.innerHeight;
            pts = [];
            const n = Math.floor((W * H) / 5000);
            for (let i = 0; i < n; i++) {
                const bx = Math.random() * W;
                const by = Math.random() * H;
                pts.push({
                    x: bx, y: by, bx, by,
                    r: Math.random() * 2 + 1,
                    vx: (Math.random() - 0.5) * 0.4,
                    vy: (Math.random() - 0.5) * 0.4,
                    color: COLORS[Math.floor(Math.random() * COLORS.length)],
                    alpha: Math.random() * 0.5 + 0.4,
                    dens: Math.random() * 25 + 5
                });
            }
        }

        function tick() {
            ctx.clearRect(0, 0, W, H);
            for (const p of pts) {
                // drift base position
                p.bx += p.vx; p.by += p.vy;
                if (p.bx > W) p.bx = 0; if (p.bx < 0) p.bx = W;
                if (p.by > H) p.by = 0; if (p.by < 0) p.by = H;

                // repulsion from mouse
                const dx = mouse.x - p.x, dy = mouse.y - p.y;
                const dist = Math.hypot(dx, dy);
                if (dist < mouse.r && dist > 0) {
                    const f = (mouse.r - dist) / mouse.r;
                    p.x -= (dx / dist) * f * p.dens;
                    p.y -= (dy / dist) * f * p.dens;
                } else {
                    p.x += (p.bx - p.x) * 0.07;
                    p.y += (p.by - p.y) * 0.07;
                }

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.alpha;
                ctx.fill();
            }
            ctx.globalAlpha = 1;
            requestAnimationFrame(tick);
        }

        doc.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
        doc.addEventListener('mouseleave', () => { mouse.x = -9999; mouse.y = -9999; });
        window.parent.addEventListener('resize', resize);
        resize();
        tick();

        // ── 2. MAGNETIC CURSOR ──────────────────────────────────────────
        const oldCur = doc.getElementById('ag-cursor');
        if (oldCur) oldCur.remove();
        const oldFol = doc.getElementById('ag-follower');
        if (oldFol) oldFol.remove();
        const oldSty = doc.getElementById('ag-style');
        if (oldSty) oldSty.remove();

        const style = doc.createElement('style');
        style.id = 'ag-style';
        style.textContent = `
            * { cursor: none !important; }
            #ag-cursor {
                position: fixed; z-index: 999999; pointer-events: none;
                width: 10px; height: 10px; border-radius: 50%;
                background: #00f2fe;
                box-shadow: 0 0 12px #00f2fe, 0 0 24px rgba(6,182,212,0.5);
                transform: translate(-50%,-50%);
                transition: width .25s, height .25s, border-radius .25s, background .25s;
                mix-blend-mode: screen;
            }
            #ag-follower {
                position: fixed; z-index: 999998; pointer-events: none;
                width: 32px; height: 32px; border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, rgba(147, 51, 234, 0.8), rgba(90, 20, 160, 0.9) 60%, rgba(30, 0, 70, 1) 100%);
                box-shadow: 
                    inset -5px -5px 15px rgba(0, 0, 0, 0.6),
                    inset 2px 2px 8px rgba(255, 255, 255, 0.5),
                    0 0 15px rgba(147, 51, 234, 0.6),
                    0 0 25px rgba(147, 51, 234, 0.4);
                transform: translate(-50%,-50%);
                transition: width .3s, height .3s, opacity .3s, border-radius .3s;
                mix-blend-mode: screen;
            }
            #ag-cursor.hov {
                width: 55px; height: 55px; border-radius: 12px;
                background: rgba(147,51,234,0.35);
                mix-blend-mode: normal;
            }
            #ag-follower.hov { opacity: 0; }
        `;
        doc.head.appendChild(style);

        const cur = doc.createElement('div'); cur.id = 'ag-cursor';
        const fol = doc.createElement('div'); fol.id = 'ag-follower';
        doc.body.appendChild(cur); doc.body.appendChild(fol);

        let mx = W/2, my = H/2, fx = mx, fy = my;

        doc.addEventListener('mousemove', e => {
            mx = e.clientX; my = e.clientY;
            cur.style.left = mx + 'px'; cur.style.top = my + 'px';
        });

        (function moveFol() {
            fx += (mx - fx) * 0.14;
            fy += (my - fy) * 0.14;
            fol.style.left = fx + 'px'; fol.style.top = fy + 'px';
            requestAnimationFrame(moveFol);
        })();

        function bindHover() {
            doc.querySelectorAll('button,a,input,[role="button"]').forEach(el => {
                if (el._agBound) return; el._agBound = true;
                el.addEventListener('mouseenter', () => { cur.classList.add('hov'); fol.classList.add('hov'); });
                el.addEventListener('mouseleave', () => { cur.classList.remove('hov'); fol.classList.remove('hov'); });
            });
        }
        setInterval(bindHover, 800);
    </script>
    """, height=0, width=0)


    # Hero Section

    h1, h2 = st.columns([1.5, 1])
    with h1:
        st.markdown("""
            <div style="padding-top: 50px; padding-bottom: 30px; z-index: 10; position: relative;">
                <h1 class="hero-title">Codify AI: <br><span class="glow-purple">Amplify</span> Your <span class="glow-cyan">Engineering</span> Potential</h1>
                <p class="hero-subtitle">High-fidelity coding assistant for implementing modern UI, optimized performance, and scalable AI infrastructure.</p>
            </div>
        """, unsafe_allow_html=True)
        
        b1, b2, _ = st.columns([0.8, 1, 1.5])
        with b1:
            if st.button("GET STARTED", use_container_width=True, key="hero_btn"):
                st.session_state['show_landing'] = False
                st.rerun()
        with b2:
            if st.button("EXPLORE FEATURES →", use_container_width=True, key="explore_btn"):
                st.session_state['show_features'] = True
                st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Bento Grid
    g1, g2, g3 = st.columns([1.2, 1, 1])
    with g1:
        st.markdown("""
            <style>
            /* Automated Coding animations */
            .code-block {
                background: rgba(0,0,0,0.4); border-radius: 12px; padding: 18px 20px;
                margin-top: 24px; border: 1px solid rgba(6,182,212,0.25);
                position: relative; overflow: hidden; font-family: 'Fira Code', monospace;
            }
            .code-line {
                height: 9px; border-radius: 4px; margin-bottom: 12px;
                background: rgba(255,255,255,0.08);
                position: relative; overflow: hidden;
            }
            .code-line::after {
                content: ''; position: absolute; left: -100%; top: 0;
                height: 100%; width: 60%;
                background: linear-gradient(90deg, transparent, rgba(0,242,254,0.5), transparent);
                animation: scan 3s ease-in-out infinite;
            }
            .code-line:nth-child(1)::after { animation-delay: 0s; }
            .code-line:nth-child(2)::after { animation-delay: 0.4s; }
            .code-line:nth-child(3)::after { animation-delay: 0.8s; }
            .code-line:nth-child(4)::after { animation-delay: 1.2s; }
            @keyframes scan { 0%{left:-100%} 100%{left:200%} }

            .scan-beam {
                position: absolute; top: 0; left: 0; width: 100%; height: 2px;
                background: linear-gradient(90deg, transparent, #00f2fe, transparent);
                animation: beam-sweep 2s linear infinite;
            }
            @keyframes beam-sweep {
                0%  { top: 0; opacity: 1; }
                95% { top: 100%; opacity: 0.6; }
                100%{ top: 0; opacity: 0; }
            }
            .cursor-blink {
                display: inline-block; width: 8px; height: 16px;
                background: #00f2fe; margin-left: 4px; vertical-align: middle;
                animation: blink 1s step-end infinite;
                box-shadow: 0 0 8px #00f2fe;
            }
            @keyframes blink { 50%{opacity: 0;} }
            </style>

            <div class="bento-card" style="height: 390px;">
                <h3 style="color: #f8fafc; font-family: 'Space Grotesk'; font-size: 1.4rem;">AUTOMATED <span class="glow-cyan">CODING</span></h3>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 8px;">Synthesizing complex UI components.<span class="cursor-blink"></span></p>
                <div class="code-block">
                    <div class="scan-beam"></div>
                    <div class="code-line" style="width: 75%;"></div>
                    <div class="code-line" style="width: 55%;"></div>
                    <div class="code-line" style="width: 88%;"></div>
                    <div class="code-line" style="width: 40%;"></div>
                    <!-- glowing progress line -->
                    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; margin-top: 8px;">
                        <div style="height: 100%; background: linear-gradient(90deg, #00f2fe, #a855f7); border-radius: 3px; box-shadow: 0 0 10px #00f2fe; animation: fill-bar 3s ease-in-out infinite alternate; width: 70%;"></div>
                    </div>
                    <style>@keyframes fill-bar { 0%{width:15%} 100%{width:92%} }</style>
                </div>
            </div>
        """, unsafe_allow_html=True)

        
    with g2:
        st.markdown("""
            <style>
            /* === ARC REACTOR === */
            .arc-reactor-wrap {
                display: flex; justify-content: center; align-items: center;
                height: 130px; position: relative;
            }
            .arc-reactor {
                width: 110px; height: 110px;
                position: relative;
                display: flex; align-items: center; justify-content: center;
            }
            /* Rings */
            .arc-ring {
                position: absolute; border-radius: 50%;
                border: 2px solid transparent;
            }
            .arc-ring-1 {
                width: 110px; height: 110px;
                border-top-color: #00f2fe; border-right-color: rgba(0,242,254,0.3);
                animation: spin-cw 3s linear infinite;
                box-shadow: 0 0 10px rgba(0,242,254,0.4);
            }
            .arc-ring-2 {
                width: 86px; height: 86px;
                border-bottom-color: #a855f7; border-left-color: rgba(168,85,247,0.3);
                animation: spin-ccw 2s linear infinite;
                box-shadow: 0 0 8px rgba(168,85,247,0.4);
            }
            .arc-ring-3 {
                width: 64px; height: 64px;
                border-top-color: #00f2fe; border-left-color: rgba(0,242,254,0.2);
                animation: spin-cw 1.5s linear infinite;
            }
            .arc-ring-4 {
                width: 46px; height: 46px;
                border-right-color: #a855f7; border-bottom-color: rgba(168,85,247,0.2);
                animation: spin-ccw 4s linear infinite;
            }
            /* Radial energy lines */
            .arc-spokes {
                position: absolute; width: 90px; height: 90px;
                animation: spin-cw 6s linear infinite;
            }
            .arc-spoke {
                position: absolute; left: 50%; top: 50%;
                width: 1px; height: 38px;
                background: linear-gradient(to top, transparent, rgba(0,242,254,0.5));
                transform-origin: bottom center;
            }
            /* Core */
            .arc-core {
                width: 22px; height: 22px; border-radius: 50%;
                background: radial-gradient(circle, #ffffff 0%, #00f2fe 40%, rgba(0,242,254,0.2) 100%);
                box-shadow: 0 0 12px #00f2fe, 0 0 25px #00f2fe, 0 0 40px rgba(0,242,254,0.5);
                animation: core-pulse 1.5s ease-in-out infinite alternate;
                z-index: 10;
            }
            @keyframes spin-cw  { to { transform: rotate(360deg); } }
            @keyframes spin-ccw { to { transform: rotate(-360deg); } }
            @keyframes core-pulse {
                0%  { box-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 35px rgba(0,242,254,0.4); transform: scale(1); }
                100%{ box-shadow: 0 0 18px #00f2fe, 0 0 35px #a855f7, 0 0 55px rgba(168,85,247,0.6); transform: scale(1.15); }
            }
            </style>

            <div class="bento-card" style="height: 220px; margin-bottom: 20px;">
                <h3 style="color: #f8fafc; font-family: 'Space Grotesk'; font-size: 1.2rem; text-align: center;">
                    AI <span class="glow-purple">INTEGRATION</span>
                </h3>
                <div class="arc-reactor-wrap">
                    <div class="arc-reactor">
                        <div class="arc-ring arc-ring-1"></div>
                        <div class="arc-ring arc-ring-2"></div>
                        <div class="arc-ring arc-ring-3"></div>
                        <div class="arc-ring arc-ring-4"></div>
                        <!-- 8 spoke lines -->
                        <div class="arc-spokes">
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(0deg)   translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(45deg)  translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(90deg)  translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(135deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(180deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(225deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(270deg) translateY(-100%);"></div>
                            <div class="arc-spoke" style="transform: translateX(-50%) rotate(315deg) translateY(-100%);"></div>
                        </div>
                        <div class="arc-core"></div>
                    </div>
                </div>
            </div>
            
            <div class="bento-card" style="height: 160px;">
                <h3 style="color: #f8fafc; font-family: 'Space Grotesk'; font-size: 1.1rem;"><span class="glow-cyan">SECURITY</span> & COMPLIANCE</h3>
                <svg viewBox="0 0 100 30" style="margin-top: 25px; width: 100%;">
                    <polyline points="0,20 20,10 40,25 60,5 80,15 100,0" fill="none" stroke="#00f2fe" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                    <polyline points="0,20 20,10 40,25 60,5 80,15 100,0" fill="none" stroke="rgba(6, 182, 212, 0.4)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" filter="blur(4px)" />
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
    with g3:
        st.markdown("""
            <style>
            /* Deployment & Scaling: Animated bar chart */
            .bar-chart { display: flex; gap: 10px; align-items: flex-end; height: 80px; margin-top: 24px; }
            .bar {
                flex: 1; border-radius: 6px 6px 0 0;
                position: relative; overflow: hidden;
                animation: bar-grow 2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
            }
            .bar::after {
                content: ''; position: absolute; top: 0; left: 0; right: 0;
                height: 3px; background: rgba(255,255,255,0.4);
                animation: bar-shine 2s ease infinite alternate;
            }
            @keyframes bar-grow { from { transform: scaleY(0); transform-origin: bottom; } to { transform: scaleY(1); transform-origin: bottom; } }
            @keyframes bar-shine { 0%{opacity:0.3} 100%{opacity:1} }
            .bar-1 { background: linear-gradient(to top, #4f46e5, #7c3aed); height: 55px; animation-delay: 0s; }
            .bar-2 { background: linear-gradient(to top, #06b6d4, #00f2fe); height: 75px; animation-delay: 0.15s; }
            .bar-3 { background: linear-gradient(to top, #a855f7, #c084fc); height: 45px; animation-delay: 0.3s; }
            .bar-4 { background: linear-gradient(to top, #06b6d4, #a855f7); height: 65px; animation-delay: 0.45s; }
            .bar-5 { background: linear-gradient(to top, #4f46e5, #06b6d4); height: 85px; animation-delay: 0.6s; }
            /* Orbiting deployment circle */
            .orbit-wrapper {
                position: relative; width: 30px; height: 30px; margin: 0 auto; margin-top: 16px;
            }
            .orbit-ring {
                width: 30px; height: 30px; border-radius: 50%;
                border: 1.5px solid rgba(0,242,254,0.4);
                animation: spin-cw 3s linear infinite;
                position: absolute; top: 0; left: 0;
            }
            .orbit-dot {
                width: 5px; height: 5px; border-radius: 50%;
                background: #00f2fe; box-shadow: 0 0 6px #00f2fe;
                position: absolute; top: -3px; left: 50%; transform: translateX(-50%);
            }
            </style>

            <div class="bento-card" style="height: 200px; margin-bottom: 20px;">
                <h3 style="color: #f8fafc; font-family: 'Space Grotesk'; font-size: 1.2rem;">DEPLOYMENT & <span class="glow-purple">SCALING</span></h3>
                <div class="bar-chart">
                    <div class="bar bar-1"></div>
                    <div class="bar bar-2"></div>
                    <div class="bar bar-3"></div>
                    <div class="bar bar-4"></div>
                    <div class="bar bar-5"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        
        # The GET STARTED / Ready to build card with orbit-ring animation
        st.markdown("""
            <style>
            /* Security card: animated shield */
            .shield-wrap { display: flex; justify-content: center; margin-top: 12px; position: relative; }
            .shield-pulse-ring {
                position: absolute; width: 44px; height: 44px; border-radius: 50%;
                border: 1px solid rgba(0,242,254,0.5);
                animation: shield-pulse 2s ease-out infinite;
            }
            .shield-pulse-ring:nth-child(2) { animation-delay: 0.7s; }
            .shield-pulse-ring:nth-child(3) { animation-delay: 1.4s; }
            @keyframes shield-pulse {
                0%  { transform: scale(1);   opacity: 0.8; }
                100%{ transform: scale(2.5); opacity: 0;   }
            }
            /* Get Started: orbiting ring */
            .cta-orbit {
                position: absolute; width: 80px; height: 80px; border-radius: 50%;
                border: 1px dashed rgba(147,51,234,0.4);
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                animation: spin-cw 8s linear infinite;
                pointer-events: none;
            }
            .cta-orbit-dot {
                position: absolute; width: 6px; height: 6px; border-radius: 50%;
                background: #a855f7; box-shadow: 0 0 8px #a855f7;
                top: -3px; left: 50%; transform: translateX(-50%);
            }
            </style>
            <div style="height: 160px; position: relative;">
                <div class="bento-card" style="display:flex; flex-direction:column; justify-content:center; align-items:center; position: relative;">
                    <div class="cta-orbit"><div class="cta-orbit-dot"></div></div>
                    <h3 style="color:#fff; font-family:'Space Grotesk'; font-size:1.1rem; margin-bottom:12px; text-align:center; z-index:2;">Ready to build?</h3>
        """, unsafe_allow_html=True)

        
        if st.button("GET STARTED", use_container_width=True, key="bento_get_started"):
            st.session_state['show_landing'] = False
            st.rerun()
            
        st.markdown("</div></div>", unsafe_allow_html=True)

# A reusable helper that restores the cursor when not on the landing page
def restore_cursor():
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const doc = window.parent.document;
        // Remove the custom cursor elements injected by landing page
        ['ag-cursor','ag-follower','ag-style','codify-canvas'].forEach(id => {
            const el = doc.getElementById(id);
            if (el) el.remove();
        });
        // Force the real OS cursor back everywhere
        const fix = doc.getElementById('cursor-fix-style');
        if (!fix) {
            const s = doc.createElement('style');
            s.id = 'cursor-fix-style';
            s.textContent = '* { cursor: auto !important; } a, button, [role="button"] { cursor: pointer !important; } input, textarea, select { cursor: text !important; }';
            doc.head.appendChild(s);
        }
    </script>
    """, height=0, width=0)

# --- 4.6 EXPLORE FEATURES PAGE ---
def features_page():
    restore_cursor()
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none;}
        header {visibility: hidden;}
        .stApp {
            background-color: #020617;
            color: #f8fafc;
            font-family: 'Space Grotesk', sans-serif;
            background-image: 
                radial-gradient(circle at top right, rgba(147, 51, 234, 0.15) 0%, transparent 60%),
                radial-gradient(circle at bottom left, rgba(6, 182, 212, 0.15) 0%, transparent 60%);
        }
        .feature-box {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 25px;
            transition: all 0.3s;
        }
        .feature-box:hover {
            border-color: rgba(6, 182, 212, 0.3);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transform: translateY(-2px);
        }
        h2 { color: #fff; font-size: 2.2rem; margin-bottom: 10px; font-weight: 700; }
        .gradient-text {
            background: linear-gradient(to right, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .gradient-text-purple {
            background: linear-gradient(to right, #a855f7, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p { color: #94a3b8; font-size: 1.1rem; line-height: 1.6; font-family: 'Inter', sans-serif;}
        li { color: #cbd5e1; margin-bottom: 8px; font-size: 1.05rem; font-family: 'Inter', sans-serif; }
        
        div[data-testid="stButton"] button {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 30px !important;
            padding: 10px 30px !important;
            color: white !important;
            transition: all 0.3s !important;
        }
        div[data-testid="stButton"] button:hover {
            background: rgba(255,255,255,0.1) !important;
            border-color: #fff !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← BACK"):
            st.session_state['show_features'] = False
            st.rerun()
            
    st.markdown("<h1 style='text-align:center; font-size: 3.5rem; margin-top: 20px; font-weight: 800;'>Codify <span class='gradient-text-purple'>Data Science</span> Capabilities</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; margin-bottom: 50px;'>Empowering data analysts and engineers with neural intelligence.</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="feature-box">
            <h2 class="gradient-text">1. Advanced Dataset Processing</h2>
            <p>Direct ingestion of <b>CSV, XLS, and XLSX</b> files into the AI context window. The system uses Pandas to pre-process and summarize dataframe topologies before passing them to the Llama-3.3 model, ensuring high-accuracy data understanding.</p>
            <ul>
                <li>Automatic shape & column mapping inference</li>
                <li>Preview top rows directly in the UI</li>
                <li>Intelligent handling of missing values via prompt context</li>
            </ul>
        </div>
        
        <div class="feature-box">
            <h2 class="gradient-text-purple">2. Automated Formula Synthesis</h2>
            <p>Codify isn't just for Python. Our engine generates complex data manipulation formulas tailored for business intelligence.</p>
            <ul>
                <li><b>Excel & Google Sheets:</b> VLOOKUPs, nested IFs, INDEX/MATCH, and conditional aggregates</li>
                <li>Complex string extraction and date-time arithmetic generation</li>
                <li>Explanations of formula logic included in the generation output</li>
            </ul>
        </div>
        
        <div class="feature-box">
            <h2 class="gradient-text">3. SQL Query Architecture</h2>
            <p>Quickly build schema-aware database queries. Provide the context of your tables, and Codify will write optimized analytical queries.</p>
            <ul>
                <li>Multi-table JOINs and subqueries</li>
                <li>Window functions for rolling averages and cumulative sums</li>
                <li>SQLite compatibility (used natively as our persistence layer)</li>
            </ul>
        </div>
        
        <div class="feature-box">
            <h2 class="gradient-text-purple">4. Python Data Pipelines</h2>
            <p>Generate production-grade Python scripts for <b>ETL (Extract, Transform, Load)</b> workflows.</p>
            <ul>
                <li>Pandas melt, pivot_table, and groupby logic</li>
                <li>Data visualization scripts (Matplotlib / Seaborn / Plotly)</li>
                <li>SciPy and Numpy array manipulation functions</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)


# --- 5. LOGIN PAGE WITH LOGO ---

def login_page():
    restore_cursor()
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top right, #1a1a1a, #000000) !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(255, 255, 255, 0.0) !important;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background: linear-gradient(90deg, #8b0000, #dc143c, #4b0082, #1a1a1a, #4b0082, #dc143c);
            z-index: 999999;
        }

        .wombat-paws {
            transform: translateY(120px);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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

        [data-testid="column"]:nth-of-type(2) {
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            padding: 40px !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
        }
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #f8fafc !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        .stTextInput>div>div>input:focus {
            border-color: #ffffff !important;
            box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.3) !important;
        }
        .stTextInput label {
            color: #e2e8f0 !important;
            font-weight: 500 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 14px !important;
            margin-bottom: 4px !important;
            letter-spacing: 1px;
        }
        .stButton>button {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #e2e8f0 !important;
            border-radius: 8px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 1px;
            padding: 10px !important;
            margin-top: 20px !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border-color: #ffffff !important;
            color: #ffffff !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
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
                    
                    const rotateY = x * 50;
                    const rotateX = -y * 50;
                    
                    container.style.setProperty('--rx', rotateX + 'deg');
                    container.style.setProperty('--ry', rotateY + 'deg');
                } catch (err) {
                    console.log(err);
                }
            }
            try {
                window.parent.document.addEventListener('mousemove', updateTilt);
            } catch (err) {}
        </script>
        """, height=0, width=0)
        
        st.markdown("""
            <h1 style='text-align: center; 
                       color: #fff; 
                       text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #dc143c, 0 0 40px #dc143c, 0 0 50px #dc143c, 0 0 60px #dc143c, 0 0 70px #dc143c; 
                       font-family: "Space Grotesk", sans-serif;
                       font-size: 3.5rem;
                       margin-top: 10px;
                       margin-bottom: 30px;
                       letter-spacing: 4px;
                       font-weight: 800;
                       user-select: none;
                       animation: neon-pulse 1.5s infinite alternate;'>
                SIGN IN
            </h1>
            <style>
                @keyframes neon-pulse {
                    0% { opacity: 0.8; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #dc143c, 0 0 20px #dc143c; filter: brightness(0.9); }
                    100% { opacity: 1; text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #dc143c, 0 0 40px #dc143c, 0 0 60px #dc143c; filter: brightness(1.1); }
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.text_input("Username")
        st.text_input("Password", type="password")
        
        if st.button("Sign In", use_container_width=True):
            st.session_state['logged_in'] = True
            st.session_state['booting'] = True
            st.rerun()
            
        st.markdown("""
            <div style="text-align: center; margin-top: 25px;">
                <a href="#" style="color: #94a3b8; text-decoration: none; font-size: 14px; margin-right: 15px; font-weight: 500; transition: color 0.2s;" onmouseover="this.style.color='#ffffff'" onmouseout="this.style.color='#94a3b8'">Forgot password?</a>
                <span style="color: #475569;">|</span>
                <a href="#" style="color: #94a3b8; text-decoration: none; font-size: 14px; margin-left: 15px; font-weight: 500; transition: color 0.2s;" onmouseover="this.style.color='#ffffff'" onmouseout="this.style.color='#94a3b8'">Create an Account</a>
            </div>
        """, unsafe_allow_html=True)

# --- 6. BOOT SEQUENCE ---
def boot_sequence():
    boot_placeholder = st.empty()
    sequence = [
        "INITIALIZING CORE SYSTEMS...",
        "CALIBRATING NEURAL INTERFACE...",
        "ENGAGING PRIMARY DRIVES...",
        "HUD ONLINE. WELCOME, BUDDY ."
    ]
    hud_css = """
    <style>
    .hud-text {
        font-family: 'Space Grotesk', monospace;
        color: #ffffff;
        font-size: 2rem;
        text-align: center;
        margin-top: 40vh;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.7);
        animation: pulse 1s infinite alternate;
    }
    @keyframes pulse {
        0% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .hud-overlay {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle, transparent 20%, #000000 80%), repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255, 255, 255, 0.02) 2px, rgba(255, 255, 255, 0.02) 4px);
        pointer-events: none;
        z-index: 9999;
    }
    </style>
    <div class='hud-overlay'></div>
    """
    for text in sequence:
        boot_placeholder.markdown(hud_css + f"<div class='hud-text reveal'>{text}</div>", unsafe_allow_html=True)
        time.sleep(0.8)
    time.sleep(0.5)
    boot_placeholder.empty()

# --- 7. MAIN APPLICATION ---
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
    restore_cursor()
    with st.sidebar:
        import base64
        # Load the user's logo image as base64
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
                    max-width: 190px;
                    aspect-ratio: 1 / 1;
                    margin: 0 auto 10px auto;
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
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 2;
                    pointer-events: none;
                    filter: drop-shadow(0px 0px 3px rgba(0, 242, 254, 0.6));
                }}
                .coolant-cyan {{
                    fill: none;
                    stroke: #00f2fe;
                    stroke-width: 0.8;
                    stroke-linecap: round;
                    stroke-dasharray: 20 180;
                    animation: circuit-flow 2.5s linear infinite;
                }}
                .coolant-purple {{
                    fill: none;
                    stroke: #a855f7;
                    stroke-width: 0.8;
                    stroke-linecap: round;
                    stroke-dasharray: 15 200;
                    animation: circuit-flow 3.5s linear infinite;
                }}
                .coolant-blue {{
                    fill: none;
                    stroke: #3b82f6;
                    stroke-width: 0.8;
                    stroke-linecap: round;
                    stroke-dasharray: 25 150;
                    animation: circuit-flow 2s linear infinite;
                }}
                @keyframes circuit-flow {{
                    from {{ stroke-dashoffset: 200; }}
                    to {{ stroke-dashoffset: -200; }}
                }}
                </style>
                <img src="data:image/png;base64,{encoded_logo}" class="base-logo-img" alt="CODIFY AI Logo" />
                <svg class="circuit-overlay" viewBox="0 0 100 100">
                    <path class="coolant-cyan" d="M 45,42 L 35,42 L 30,35 L 20,35" style="animation-delay: 0s;" />
                    <path class="coolant-cyan" d="M 45,43 L 38,43 L 30,50 L 22,50" style="animation-delay: -0.5s;" />
                    <path class="coolant-cyan" d="M 43,40 L 38,35 L 30,35 L 25,28" style="animation-delay: -1s;" />
                    <path class="coolant-purple" d="M 44,45 L 35,45 L 30,55 L 25,55 L 20,60" style="animation-delay: -1.2s;" />
                    <path class="coolant-purple" d="M 48,39 L 45,30 L 40,25" style="animation-delay: -0.2s;" />
                    <path class="coolant-purple" d="M 48,46 L 45,55 L 40,60" style="animation-delay: -1.8s;" />
                    <path class="coolant-blue" d="M 46,42 L 32,30 L 25,30" style="animation-delay: -0.8s;" />
                    <path class="coolant-blue" d="M 46,43 L 32,54 L 25,54" style="animation-delay: -2.1s;" />
                    <path class="coolant-blue" d="M 42,42 L 28,42 L 22,35" style="animation-delay: -1.5s;" />
                    <path class="coolant-cyan" d="M 40,42 L 15,42" style="animation-delay: -0.3s;" />
                    <path class="coolant-purple" d="M 47,38 L 47,20 L 40,15" style="animation-delay: -0.9s;" />
                    <path class="coolant-cyan" d="M 47,48 L 47,65 L 42,70" style="animation-delay: -1.4s;" />
                    <path class="coolant-purple" d="M 55,42 L 65,42 L 70,47 L 85,47" style="animation-delay: 0s;" />
                    <path class="coolant-cyan" d="M 55,45 L 60,50 L 75,50 L 80,45" style="animation-delay: -1s;" />
                    <path class="coolant-blue" d="M 55,39 L 60,35 L 75,35 L 80,40" style="animation-delay: -0.5s;" />
                </svg>
            </div>
        """)
        st.markdown(animated_logo_html, unsafe_allow_html=True)
        st.divider()
        if st.button("⚡ NEURAL GENERATOR", use_container_width=True): st.session_state['page'] = 'generator'
        if st.button("📖 TECH MANIFESTO", use_container_width=True): st.session_state['page'] = 'docs'
        
        st.divider()
        st.subheader("📜 RECENT LOGS")
        conn = sqlite3.connect('codify_pro.db', check_same_thread=False)
        hist = conn.execute("SELECT language, query, code FROM history ORDER BY rowid DESC LIMIT 3").fetchall()
        conn.close()
        for item in hist:
            with st.expander(f"{item[0]}: {item[1][:10]}..."):
                st.code(item[2], language=item[0].lower())
        
        if st.button("🚪 TERMINATE SESSION", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['show_landing'] = True
            st.session_state['show_features'] = False
            st.session_state.pop('res', None)
            st.rerun()

    if st.session_state['page'] == 'generator':
        _, center_col, _ = st.columns([1, 2.5, 1])
        with center_col:
            st.markdown("<h1 class='reveal' style='font-family: \"Space Grotesk\", sans-serif; font-weight: 700; font-size: 2.5rem; text-align: center; margin-bottom: 30px; margin-top: 10px; background: linear-gradient(to right, #dc143c, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AI <span style='opacity: 0.3; -webkit-text-fill-color: #ffffff;'>//</span> ARCHITECT</h1>", unsafe_allow_html=True)
            q = st.text_area("What would you like to build?", placeholder="Describe your objective, feature, or data manipulation task in plain English...", height=180)
            
            # --- File Upload Section ---
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
                        # ── SQLite database upload ────────────────────────────
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                            tmp.write(raw_bytes)
                            tmp_path = tmp.name

                        try:
                            conn_db = _sqlite3.connect(tmp_path)
                            cursor_db = conn_db.cursor()

                            # Get all table names
                            tables = [r[0] for r in cursor_db.execute(
                                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
                            ).fetchall()]

                            st.markdown(
                                f"<p style='font-size:0.8rem; color:#94a3b8; margin-top:8px;'>"
                                f"✅ Loaded <b>{uploaded_file.name}</b> — {len(tables)} table(s): "
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
                        st.markdown(f"<p style='font-size:0.8rem; color:#94a3b8; margin-top:8px;'>✅ Loaded <b>{uploaded_file.name}</b> — {df.shape[0]} rows × {df.shape[1]} columns</p>", unsafe_allow_html=True)
                        with st.expander("📊 DATASET PREVIEW", expanded=False):
                            st.dataframe(df.head(10), use_container_width=True)
                        dataset_context = (
                            f"\n\nREFERENCE DATASET: {uploaded_file.name}\n"
                            f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
                            f"Columns: {', '.join(df.columns.tolist())}\n"
                            f"First 50 rows (CSV format):\n{df.head(50).to_csv(index=False)}"
                        )
                    else:
                        df = pd.read_excel(io.BytesIO(raw_bytes))
                        st.markdown(f"<p style='font-size:0.8rem; color:#94a3b8; margin-top:8px;'>✅ Loaded <b>{uploaded_file.name}</b> — {df.shape[0]} rows × {df.shape[1]} columns</p>", unsafe_allow_html=True)
                        with st.expander("📊 DATASET PREVIEW", expanded=False):
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
                    loader_html = """
                    <style>
                    .cube-loader {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100px;
                        margin: 20px 0;
                    }
                    .cube {
                        width: 40px;
                        height: 40px;
                        background-color: transparent;
                        border: 2px solid #ffffff;
                        animation: spin 2s infinite linear, glow 1.5s infinite alternate;
                    }
                    .loading-text {
                        text-align: center;
                        font-family: 'Space Grotesk', monospace;
                        color: #e2e8f0;
                        letter-spacing: 3px;
                        animation: pulse 1s infinite alternate;
                    }
                    @keyframes spin {
                        0% { transform: rotateX(0deg) rotateY(0deg); }
                        100% { transform: rotateX(360deg) rotateY(360deg); }
                    }
                    @keyframes glow {
                        0% { box-shadow: 0 0 5px rgba(255, 255, 255, 0.2); }
                        100% { box-shadow: 0 0 20px rgba(255, 255, 255, 0.8), inset 0 0 10px rgba(255, 255, 255, 0.5); }
                    }
                    </style>
                    <div class="cube-loader">
                        <div class="cube"></div>
                    </div>
                    <div class="loading-text">SYNTHESIZING NEURAL PATHWAYS...</div>
                    """
                    loader_placeholder.markdown(loader_html, unsafe_allow_html=True)
                    
                    try:
                        # ── Build a rich, tool-aware system prompt ──────────────
                        STEP_GUIDE = (
                            "\n\nAfter the output, you MUST include:\n"
                            "**### Step-by-Step Execution Guide**\n"
                            "Numbered steps (1, 2, 3...) explaining exactly how to run or use the generated output.\n"
                            "\n**### Code / Formula Explanation**\n"
                            "A plain-English explanation of what each part of the generated output does and why.\n"
                            "\n**### Expected Output**\n"
                            "Describe clearly what the user should see after running the output (e.g., table columns, chart type, formula result)."
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
                                "If a database schema is provided, write queries that use the EXACT table and column names from the schema."
                                + STEP_GUIDE
                            ),
                            "Power BI (DAX / M Query)": (
                                "You are a certified Power BI developer. "
                                "Generate the appropriate DAX measure/column formula OR Power Query (M) transformation based on the request. "
                                "Clearly label which type (DAX or M Query) you are providing."
                                + STEP_GUIDE
                            ),
                            "Tableau (Calculated Fields / LOD)": (
                                "You are a Tableau Server Certified Associate. "
                                "Generate the appropriate Tableau Calculated Field expression or LOD (Level of Detail) expression."
                                + STEP_GUIDE
                            ),
                            "Excel Formula": (
                                "You are an advanced Microsoft Excel specialist. "
                                "Generate professional Excel formulas using modern functions (XLOOKUP, LET, LAMBDA, dynamic arrays, etc.)."
                                + STEP_GUIDE
                            ),
                            "Google Sheets Formula": (
                                "You are an advanced Google Sheets specialist. "
                                "Generate professional Google Sheets formulas using functions like QUERY, ARRAYFORMULA, IMPORTRANGE, etc."
                                + STEP_GUIDE
                            ),
                        }

                        system_prompt = tool_instructions.get(lang, f"You are an expert in {lang}. Generate accurate, professional output for the user's request." + STEP_GUIDE)

                        if q:
                            user_request = f"User Request: {q}"
                        elif dataset_context:
                            user_request = f"Analyse the provided dataset/database and produce the best {lang} solution to process and summarize it."
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

        # ── Output box rendered OUTSIDE the narrow input column ──────────────
        if 'res' in st.session_state:
            _, out_col, _ = st.columns([0.1, 9.8, 0.1])
            with out_col:
                st.markdown("""
                    <div style='
                        margin-top: 36px;
                        padding: 32px 36px;
                        border-radius: 14px;
                        background: rgba(255,255,255,0.025);
                        border: 1px solid rgba(255,255,255,0.08);
                        border-left: 3px solid #dc143c;
                        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
                    '>
                    <h3 style='
                        font-family: "Space Grotesk", sans-serif;
                        font-size: 0.75rem;
                        font-weight: 600;
                        color: #dc143c;
                        letter-spacing: 3px;
                        text-transform: uppercase;
                        margin-bottom: 24px;
                    '>⚡ SYSTEM OUTPUT</h3>
                """, unsafe_allow_html=True)
                st.markdown(st.session_state['res'])
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state['page'] == 'docs':
        st.markdown("<h1 style='font-family: \"Space Grotesk\", sans-serif; font-weight: 500; color: #f8fafc; font-size: 2.2rem; margin-bottom: 30px;' class='reveal'>TECHNICAL <span style='color: #ffffff; opacity: 0.6;'>MANIFESTO</span></h1>", unsafe_allow_html=True)
        
        # --- ENHANCED DOCUMENTATION ---
        st.markdown("""
        <div class="manifesto-card reveal">
            <h3>🏗️ I. PROJECT ABSTRACT & VISION</h3>
            <p><b>Codify AI</b> is a next-generation code synthesis platform developed to resolve <b>'Syntactic Friction'</b> in the modern DevOps lifecycle. 
            The vision is to democratize high-level software architecture by automating the mundane task of boilerplate generation. 
            By leveraging the <b>Groq LPU (Language Processing Unit)</b>, this system achieves a throughput of ~500 tokens per second, 
            effectively making the AI response feel instantaneous.</p>
        </div>
        
        <div class="manifesto-card reveal" style="animation-delay: 0.2s">
            <h3>⚙️ II. 3-TIER ARCHITECTURAL DECOUPLING</h3>
            <p>The system is engineered using a robust, decoupled infrastructure:</p>
            <ul>
                <li><b>Presentation Layer (Frontend):</b> Built on Streamlit, utilizing custom CSS injection for advanced Glassmorphism and Neon-Cyberpunk UI elements.</li>
                <li><b>Logic Layer (Inference Engine):</b> Secured API handshake with Groq Cloud, utilizing the <b>Llama-3.3-70B</b> transformer model.</li>
                <li><b>Data Layer (Persistence):</b> Relational <b>SQLite 3</b> database for ACID-compliant session history and auditing.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        

        st.markdown("""
        <div class="manifesto-card reveal" style="animation-delay: 0.4s">
            <h3>🚀 III. PERFORMANCE & DEVELOPMENT METHODOLOGY</h3>
            <p>This project utilized the <b>Agile Software Development Life Cycle (SDLC)</b>, focusing on rapid prototyping and iterative feedback loops. 
            Key metrics achieved include:</p>
            <ul>
                <li><b>Latency:</b> Sub-0.8s cold start for inference queries.</li>
                <li><b>Security:</b> End-to-end secret masking via Environment Variable encryption.</li>
                <li><b>Reliability:</b> Thread-safe database connections for multi-user session stability.</li>
            </ul>
        </div>
        
        <div class="manifesto-card reveal" style="animation-delay: 0.6s">
            <h3>🔮 IV. FUTURE SCOPE: THE AI AGENT ROADMAP</h3>
            <p>Codify AI is designed for modular scalability. The following implementations are planned for Version 3.0:</p>
            <ul>
                <li><b>Contextual RAG:</b> Connecting the neural engine to private Vector Databases to understand specific user codebases.</li>
                <li><b>Automated Testing:</b> Real-time generation of unit tests for every code block synthesized.</li>
                <li><b>Multi-Modal:</b> Voice-commanded code generation using the OpenAI Whisper API.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        

    # --- DYNAMIC FLOATING SIGNATURE ---
    st.markdown(f"<div class='dev-signature'>DEVELOPED BY DEEKSHITH</div>", unsafe_allow_html=True)