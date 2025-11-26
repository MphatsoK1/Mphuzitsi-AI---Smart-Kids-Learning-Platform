# generate_avatars.py
from PIL import Image, ImageDraw, ImageFont
import os

def create_avatar(color, letter, filename):
    img = Image.new('RGB', (150, 150), color=color)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # Center the letter
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((150 - text_width) / 2, (150 - text_height) / 2 - 10)
    
    draw.text(position, letter, fill='white', font=font)
    
    # Make it circular
    mask = Image.new('L', (150, 150), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, 150, 150), fill=255)
    
    output = Image.new('RGBA', (150, 150))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
    os.makedirs('static/avatars', exist_ok=True)
    output.save(f'static/avatars/{filename}')

# Generate avatars
colors = [
    ('#3B82F6', 'A'),  # Blue
    ('#10B981', 'B'),  # Green
    ('#F59E0B', 'C'),  # Orange
    ('#EF4444', 'D'),  # Red
    ('#8B5CF6', 'E'),  # Purple
]

for i, (color, letter) in enumerate(colors, 1):
    create_avatar(color, letter, f'avatar{i}.png')

# Create default avatar
create_avatar('#6B7280', '?', 'default.png')

print("Avatars created successfully!")