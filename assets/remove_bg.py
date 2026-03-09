"""
Remove the dark navy background from the Codify AI logo.
Saves the result as assets/codify_logo.png (transparent BG).
"""
from PIL import Image
import numpy as np
import sys, os

# Accept input path as argument; default to the original file
input_path = sys.argv[1] if len(sys.argv) > 1 else "assets/codify_logo_original.png"
output_path = "assets/codify_logo.png"

img = Image.open(input_path).convert("RGBA")
data = np.array(img, dtype=float)

r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

# The background is a dark navy/charcoal: approximately #1a2035 to #232a42
# We'll mask pixels that are dark AND low-saturation (background-like)
brightness = (r + g + b) / 3.0
max_ch = np.maximum(np.maximum(r, g), b)
min_ch = np.minimum(np.minimum(r, g), b)
saturation = np.where(max_ch > 0, (max_ch - min_ch) / max_ch, 0)

# Background = dark (brightness < 70) AND low saturation (< 0.35)
# The neon logo lines are bright and saturated, so they survive
bg_mask = (brightness < 72) & (saturation < 0.38)

# Soft edge: feather pixels near the boundary (brightness 45-85, sat < 0.5)
feather_mask = (brightness < 85) & (brightness >= 45) & (saturation < 0.5) & bg_mask
data[:,:,3] = np.where(bg_mask, 0, 255)
data[:,:,3] = np.where(
    feather_mask,
    np.clip((brightness[feather_mask] - 45) / 40.0 * 255, 0, 255),
    data[:,:,3]
)

result = Image.fromarray(data.astype(np.uint8), "RGBA")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
result.save(output_path)
print(f"Saved transparent logo to: {output_path}")
