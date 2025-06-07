from PIL import Image
import os

gif_path = "assets/pets/troll/troll.gif"

output_folder = "assets/pets/troll"

os.makedirs(output_folder, exist_ok=True)

with Image.open(gif_path) as img:
    for frame in range(img.n_frames):
        img.seek(frame)
        frame_path = os.path.join(output_folder, f"frame_{frame:03d}.png")
        img.convert("RGBA").save(frame_path)
