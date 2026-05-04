import streamlit as st

HTML = r'''<div id="bento-container">
<style>
#bento-container { width:100%; position:relative; overflow:hidden; font-family:'Inter',sans-serif; color:#F0EDE6; padding-bottom:40px; }
#bento-container * { box-sizing:border-box; margin:0; padding:0; }
#bento-container #stage { position:relative; width:100%; display:flex; align-items:center; justify-content:center; isolation:isolate; }
#bento-container #heading { position:absolute;top:24px;left:0;right:0;text-align:center; z-index:5;pointer-events:none; }
#bento-container .ey { font-size:.62rem;letter-spacing:.22em;text-transform:uppercase;color:#D4AF65; margin-bottom:10px;display:flex;align-items:center;justify-content:center;gap:10px; }
#bento-container .ey::before, #bento-container .ey::after { content:'';width:26px;height:1px;background:#D4AF65;display:inline-block; }
#bento-container h1 { font-family:'Playfair Display',serif;font-size:clamp(2rem,4vw,4rem);font-weight:400;letter-spacing:-.03em;color:#F0EDE6;line-height:1.05; }
#bento-container h1 em { font-style:italic;font-weight:300;color:#8A8278; }
#bento-container .gold { background:linear-gradient(105deg,#D4AF65,#EDD98A,#FFFAED,#EDD98A,#D4AF65);background-size:200% auto; -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:gs 4s linear infinite; }
@keyframes gs { 0%{background-position:-200% center}100%{background-position:200% center} }
#bento-container #grid { display:grid; grid-template-columns:1fr 1.6fr 1.6fr 1fr; grid-template-rows:200px 200px 110px; gap:14px;width:min(1300px,92vw); padding-top:100px; position:relative; }
#bento-container .bc { position:relative;border-radius:16px;overflow:hidden; border:1px solid rgba(212,175,101,.18);background:#0D0D0D; box-shadow:0 4px 24px rgba(0,0,0,.7);cursor:pointer; transition:border-color 0.3s ease; will-change:transform; transform:translate3d(0,0,0); }
#bento-container .bc img { position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;transition:opacity .4s ease; }
#bento-container .bc:hover { border-color:rgba(212,175,101,.5);z-index:20; }
#bento-container .ov { position:absolute;inset:0;background:linear-gradient(to top,rgba(8,6,2,.93) 0%,rgba(8,6,2,.3) 52%,transparent 100%);z-index:1;pointer-events:none; }
#bento-container .lb { position:absolute;bottom:0;left:0;right:0;padding:14px 16px;z-index:3;pointer-events:none; }
#bento-container .lt { font-size:.55rem;letter-spacing:.2em;text-transform:uppercase;color:#D4AF65;margin-bottom:4px; }
#bento-container .ln { font-family:'Playfair Display',serif;font-size:.9rem;font-weight:500;color:#E5E4E2;line-height:1.2; }
#bento-container #bL { grid-column:1;grid-row:1/4; }
#bento-container #bT1 { grid-column:2;grid-row:1; }
#bento-container #bT2 { grid-column:3;grid-row:1; }
#bento-container #bT3 { grid-column:4;grid-row:1; }
#bento-container #bC { grid-column:2/4;grid-row:2/4;z-index:10; border-color:rgba(212,175,101,.3);box-shadow:0 8px 48px rgba(0,0,0,.85);overflow:hidden; }
#bento-container #bR { grid-column:4;grid-row:2/4; }
#bento-container #bC .ov { background:linear-gradient(to top,rgba(8,6,2,.95) 0%,rgba(8,6,2,.4) 40%,transparent 100%); }
#bento-container .cbot { position:absolute;bottom:24px;left:32px;right:32px;z-index:4;display:flex;justify-content:space-between;align-items:flex-end;pointer-events:none; }
#bento-container .ctag { font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;color:#D4AF65;margin-bottom:8px; }
#bento-container .cttl { font-family:'Playfair Display',serif;font-size:2.2rem;font-weight:400;color:#F0EDE6;line-height:1; }
#bento-container .cfr { font-family:'Inter',sans-serif;font-size:.7rem;letter-spacing:.1em;color:#8A8278; }
#bento-container .nav { position:absolute;top:24px;right:24px;z-index:5;display:flex;gap:8px; }
#bento-container .nb { width:40px;height:40px;border-radius:50%;background:rgba(20,18,14,.6);border:1px solid rgba(212,175,101,.2); backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;cursor:pointer; transition:all .3s ease;pointer-events:auto; }
#bento-container .nb svg { stroke:#E5E4E2;transition:stroke .3s ease; }
#bento-container .nb:hover { background:rgba(212,175,101,.15);border-color:rgba(212,175,101,.5); }
#bento-container .nb:hover svg { stroke:#D4AF65; }
#infoModal { position:fixed; inset:0; z-index:999999; background:rgba(6,5,3,0.75); backdrop-filter:blur(15px); -webkit-backdrop-filter:blur(15px); display:flex; align-items:center; justify-content:center; opacity:0; pointer-events:none; transition:opacity 0.4s; }
#infoModal.show { opacity:1; pointer-events:auto; }
#infoModal .modal-content { width:90%; max-width:540px; padding:40px; background:#12100A; border:1px solid rgba(212,175,101,0.2); border-radius:16px; box-shadow:0 10px 40px rgba(0,0,0,0.8); position:relative; transform:translateY(20px); transition:transform 0.4s cubic-bezier(0.16,1,0.3,1); }
#infoModal.show .modal-content { transform:translateY(0); }
#infoModal .modal-close { position:absolute; top:20px; right:20px; width:30px; height:30px; background:none; border:none; color:#8A8278; font-size:24px; cursor:pointer; display:flex; align-items:center; justify-content:center; border-radius:50%; transition:all 0.3s; }
#infoModal .modal-close:hover { color:#D4AF65; background:rgba(212,175,101,0.1); }
#infoModal #modTag { font-size:0.75rem; letter-spacing:0.2em; text-transform:uppercase; color:#D4AF65; margin-bottom:12px; }
#infoModal #modTitle { font-family:'Playfair Display',serif; font-size:2.2rem; color:#F0EDE6; margin-bottom:20px; font-weight:400; line-height:1.1; }
#infoModal #modDesc { font-size:1rem; line-height:1.7; color:#B5AAA0; font-weight:300; }
</style>
<div id="stage"><div id="heading"><div class="ey">Codify AI &mdash; The Obsidian Assembly</div><h1>Craft <em>with</em> <span class="gold">Intelligence</span></h1></div><div id="grid"><div class="bc" id="bL"><img id="iL" src="" alt=""><div class="ov"></div><div class="lb"><div class="lt" id="tL"></div><div class="ln" id="nL"></div></div></div><div class="bc" id="bT1"><img id="iT1" src="" alt=""><div class="ov"></div><div class="lb"><div class="lt" id="tT1"></div><div class="ln" id="nT1"></div></div></div><div class="bc" id="bT2"><img id="iT2" src="" alt=""><div class="ov"></div><div class="lb"><div class="lt" id="tT2"></div><div class="ln" id="nT2"></div></div></div><div class="bc" id="bT3"><img id="iT3" src="" alt=""><div class="ov"></div><div class="lb"><div class="lt" id="tT3"></div><div class="ln" id="nT3"></div></div></div><div class="bc" id="bC" data-idx="-1"><video id="vC" autoplay loop muted playsinline style="width:100%; height:100%; object-fit:cover; transform:scale(0.92); transform-origin:center center; will-change:transform;"><source src="app/static/ai_core.mp4" type="video/mp4"></video><div class="ov"></div><div class="cbot"><div><div class="ctag" id="ctag">Codify Core</div><div class="cttl" id="cttl">AI Consciousness</div></div></div><div class="nav"><button class="nb prev" id="bP"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></button><button class="nb next" id="bN"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></button></div></div><div class="bc" id="bR"><img id="iR" src="" alt=""><div class="ov"></div><div class="lb"><div class="lt" id="tR"></div><div class="ln" id="nR"></div></div></div></div></div><div id="infoModal"><div class="modal-content"><button class="modal-close" id="modalClose">&times;</button><div id="modTag">Tag</div><div id="modTitle">Title</div><div id="modDesc">Description goes here...</div></div></div>
<script>
(function(){
'use strict';
var P=[
{"title":"Neural Synthesis","tag":"AI Architecture","desc":"Dynamically generates deep neural networks optimized for your specific data topology. Synthesizes fully functional PyTorch and TensorFlow code instantly.","img":"app/static/neural.png"},
{"title":"Code Generation","tag":"Language Engine","desc":"The heart of Codify AI. Leverages an advanced Language Processing Unit to generate syntactically flawless architecture across 40+ programming languages.","img":"app/static/code_float.png"},
{"title":"Human × Machine","tag":"Interface Layer","desc":"Bridging the gap between human intent and machine execution. Provides an intuitive, natural language interface that feels like pair-programming with an expert.","img":"app/static/ai_hand.png"},
{"title":"Data Intelligence","tag":"Stream Processing","desc":"Real-time data ingestion and transformation pipelines. Generates highly optimized Kafka and Spark configurations for enterprise-scale workloads.","img":"app/static/data_stream.png"},
{"title":"Terminal Mastery","tag":"CLI Powerhouse","desc":"Total command line integration. Generates and executes bash, zsh, and powershell scripts securely within isolated containerized environments.","img":"app/static/terminal.png"},
{"title":"Silicon Precision","tag":"Hardware Aware","desc":"Generates low-level, hardware-optimized code (C/C++, Rust) that maximizes CPU cache utilization and minimizes memory fragmentation.","img":"app/static/circuit.png"}
];
var N=P.length,cur=0,at=null;
function G(id){return document.getElementById(id);}
function w(i){return((i%N)+N)%N;}
function sync(ci){
  var m=[w(ci),w(ci+1),w(ci+2),w(ci+3),w(ci+4)];
  var refs=[{im:'iL',t:'tL',n:'nL',c:'bL'},{im:'iT1',t:'tT1',n:'nT1',c:'bT1'},{im:'iT2',t:'tT2',n:'nT2',c:'bT2'},{im:'iT3',t:'tT3',n:'nT3',c:'bT3'},{im:'iR',t:'tR',n:'nR',c:'bR'}];
  refs.forEach(function(r,k){
    var p=P[m[k]]; var el=G(r.im); el.style.opacity='0';
    setTimeout(function(){el.src=p.img;el.style.opacity='1';},150);
    G(r.t).textContent=p.tag;G(r.n).textContent=p.title; G(r.c).setAttribute('data-idx', m[k]);
  });
}
function adv(d){cur=w(cur+d);sync(cur);}
function sa(){at=setInterval(function(){adv(1);},3000);}
function ca(){clearInterval(at);}
G('bP').onclick=function(e){e.stopPropagation();ca();adv(-1);sa();};
G('bN').onclick=function(e){e.stopPropagation();ca();adv(1);sa();};
var centerData = {tag: "Codify Core", title: "AI Consciousness", desc: "The centralized orchestration engine that manages state, contextual memory, and multithreaded task execution for all your active projects. It perpetually monitors and analyzes system architecture."};
['bL','bT1','bT2','bT3','bC','bR'].forEach(function(id){
  G(id).onclick = function(e) {
    if(e.target.closest('.nav')) return; ca();
    var idx = parseInt(this.getAttribute('data-idx'), 10);
    if(idx === -1) { G('modTag').textContent = centerData.tag; G('modTitle').textContent = centerData.title; G('modDesc').textContent = centerData.desc; }
    else { var p = P[idx]; G('modTag').textContent = p.tag; G('modTitle').textContent = p.title; G('modDesc').textContent = p.desc; }
    G('infoModal').classList.add('show');
  };
});
G('modalClose').onclick = function() { G('infoModal').classList.remove('show'); sa(); };
document.addEventListener('keydown',function(ev){
  if(G('infoModal').classList.contains('show') && ev.key==='Escape') { G('modalClose').click(); }
  else { if(ev.key==='ArrowLeft') {ca();adv(-1);sa();} if(ev.key==='ArrowRight') {ca();adv(1);sa();} }
});
sync(0);sa();
})();
</script>
</div>'''

def render_bento_cinema():
    """Render Codify AI static bento gallery without heavy iframes or base64"""
    # Use st.html instead of st.markdown to prevent Streamlit from interpreting the CSS as markdown
    st.html(HTML)
