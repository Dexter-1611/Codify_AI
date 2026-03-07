import base64
import os

normal_path = r"C:\Users\AD\.gemini\antigravity\brain\47326433-7a50-49c7-b2d5-078cf81bc0ca\yuji_normal_1772869709396.png"
covered_path = r"C:\Users\AD\.gemini\antigravity\brain\47326433-7a50-49c7-b2d5-078cf81bc0ca\yuji_covering_eyes_1772869724683.png"

with open(normal_path, "rb") as f:
    normal_b64 = base64.b64encode(f.read()).decode()
    
with open(covered_path, "rb") as f:
    covered_b64 = base64.b64encode(f.read()).decode()

html_content = f'''<!DOCTYPE html>
<html>
<head>
<style>
  body {{ background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; gap: 20px; }}
  .yuji-container {{
    width: 200px; 
    height: 200px; 
    border-radius: 50%; 
    margin: 0 auto; 
    position: relative; 
    overflow: hidden; 
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.5), 0 0 20px rgba(220, 20, 60, 0.4);
    border: 2px solid #dc143c;
  }}
  .yuji-img {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }}
  
  .yuji-normal {{
    z-index: 1;
    transform-origin: center;
  }}
  
  /* We use clip-path to hide the top half of the covered image initially,
     and translate it down so the hands are below the frame. */
  .yuji-covered {{
    z-index: 2;
    transform: translateY(100%);
    clip-path: inset(30% 0 0 0); /* roughly where the hands start */
  }}
  
  /* Password field focus animation */
  body:has(#password:focus) .yuji-normal {{
    filter: brightness(0.6);
    transform: scale(0.95);
  }}
  body:has(#password:focus) .yuji-covered {{
    transform: translateY(0);
    clip-path: inset(0 0 0 0);
  }}
  
  /* Username field focus animation (Leaning in / head tracking) */
  body:has(#username:focus) .yuji-normal {{
    transform: scale(1.1) translate(5px, 5px);
  }}
  
  input {{ padding: 10px; font-size: 16px; border-radius: 8px; border: 1px solid #555; background: #333; color: #fff; }}
</style>
</head>
<body>
  <div class="yuji-container">
    <img class="yuji-img yuji-normal" src="data:image/png;base64,{normal_b64}" alt="Yuji Normal">
    <img class="yuji-img yuji-covered" src="data:image/png;base64,{covered_b64}" alt="Yuji Covered">
  </div>
  <input type="text" id="username" placeholder="Username">
  <input type="password" id="password" placeholder="Password">
</body>
</html>
'''

with open(r"c:\Users\AD\OneDrive\Deekshith\Codify_Project\test_animation.html", "w") as f:
    f.write(html_content)
