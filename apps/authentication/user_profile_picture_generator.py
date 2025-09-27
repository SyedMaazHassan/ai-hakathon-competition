# In views.py
import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.conf import settings

def generate_random_name(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_color():
    return tuple(random.randint(0, 100) for _ in range(3))

def generate_default_profile_picture(full_name):
    random_name = generate_random_name()
    bg_color = generate_random_color()

    # Generate initials
    initials = ''.join(word[0].upper() for word in full_name.split())
    initials = initials[:2]

    img = Image.new('RGB', (200, 200), color=bg_color)
    d = ImageDraw.Draw(img)
    font_path = os.path.join(settings.BASE_DIR, 'fonts', 'arial.ttf')
    # try:
    #     font = ImageFont.truetype(font_path, 80)
    # except IOError:
    #     # Handle the case where the font is not found or cannot be loaded
    #     font = ImageFont.load_default()

    font = ImageFont.truetype(font_path, 80)
    

    _, _, w, h = d.textbbox((0, 0), initials, font=font)
    d.text(((200-w)/2, (200-h)/2), initials, font=font, fill=(255, 255, 255))

    # Save the image to a BytesIO buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)

    # Do not save the image directly here
    return (random_name, buffer)
