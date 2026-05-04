import base64

# Read the sphere image
with open('assets/bento/sphere.png', 'rb') as f:
    data = base64.b64encode(f.read()).decode()

data_uri = "data:image/png;base64," + data

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CODIFY AI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@400&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #050505;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      overflow: hidden;
    }
    #sphere-canvas {
      display: block;
      width: 420px;
      height: 420px;
    }
    .brand {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: -16px;
      animation: fadeUp 1.2s ease-out 0.3s forwards;
      opacity: 0;
    }
    @keyframes fadeUp {
      0%   { opacity: 0; transform: translateY(16px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    .divider {
      width: 220px;
      height: 1px;
      background: linear-gradient(90deg, transparent, #c9a84c, #f5d98b, #c9a84c, transparent);
      margin-bottom: 14px;
      animation: shimmerLine 3s ease-in-out infinite;
    }
    @keyframes shimmerLine {
      0%, 100% { opacity: 0.5; }
      50%       { opacity: 1; }
    }
    .title-wrap { position: relative; display: inline-block; }
    .title {
      font-family: 'Cinzel Decorative', serif;
      font-size: 2.4rem;
      font-weight: 700;
      letter-spacing: 0.38em;
      background: linear-gradient(135deg, #8a6a1a 0%, #c9a84c 30%, #f5d98b 50%, #c9a84c 70%, #8a6a1a 100%);
      background-size: 200% auto;
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: shimmerText 4s linear infinite;
    }
    @keyframes shimmerText {
      0%   { background-position: 200% center; }
      100% { background-position: -200% center; }
    }
    .title-glow {
      font-family: 'Cinzel Decorative', serif;
      font-size: 2.4rem;
      font-weight: 700;
      letter-spacing: 0.38em;
      color: #c9a84c;
      position: absolute;
      top: 0; left: 0;
      filter: blur(14px);
      animation: glowPulse 3s ease-in-out infinite;
      pointer-events: none;
      white-space: nowrap;
    }
    @keyframes glowPulse {
      0%, 100% { opacity: 0.25; }
      50%       { opacity: 0.55; }
    }
    .subtitle {
      margin-top: 8px;
      font-family: 'Cinzel', serif;
      font-size: 0.58rem;
      letter-spacing: 0.55em;
      color: #c9a84c;
      opacity: 0.6;
      text-transform: uppercase;
    }
  </style>
</head>
<body>
  <canvas id="sphere-canvas"></canvas>
  <div class="brand">
    <div class="divider"></div>
    <div class="title-wrap">
      <div class="title-glow">CODIFY AI</div>
      <div class="title">CODIFY AI</div>
    </div>
    <div class="subtitle">Intelligence &nbsp;&middot;&nbsp; Redefined</div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
  <script>
    const SPHERE_IMG = "SPHERE_DATA_URI";

    const canvas   = document.getElementById('sphere-canvas');
    const W = canvas.offsetWidth, H = canvas.offsetHeight;
    canvas.width  = W * devicePixelRatio;
    canvas.height = H * devicePixelRatio;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(devicePixelRatio);
    renderer.setSize(W, H);
    renderer.setClearColor(0x000000, 0);

    const scene  = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 100);
    camera.position.z = 2.8;

    // Lights
    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const goldLight = new THREE.PointLight(0xc9a84c, 4, 10);
    goldLight.position.set(2, 2, 3);
    scene.add(goldLight);
    const rimLight = new THREE.PointLight(0x4466cc, 1.5, 8);
    rimLight.position.set(-3, -1, -2);
    scene.add(rimLight);

    // Load texture from embedded base64
    const loader  = new THREE.TextureLoader();
    const texture = loader.load(SPHERE_IMG);

    const geometry = new THREE.SphereGeometry(1, 64, 64);
    const material = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.35,
      metalness: 0.65,
    });
    const sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);

    let t = 0;
    function animate() {
      requestAnimationFrame(animate);
      t += 0.016;

      // Spin the sphere on Y axis
      sphere.rotation.y += 0.007;

      // Gentle float
      sphere.position.y = Math.sin(t * 0.8) * 0.08;

      // Orbiting gold light
      goldLight.position.x = Math.cos(t * 0.4) * 3;
      goldLight.position.z = Math.sin(t * 0.4) * 2 + 1;

      renderer.render(scene, camera);
    }
    animate();
  </script>
</body>
</html>"""

# Inject the base64 image URI
html = html.replace("SPHERE_DATA_URI", data_uri)

with open('assets/bento/sphere_animated.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done! HTML size: {len(html) / 1024:.0f} KB")
