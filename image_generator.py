# image_generator.py
import os
import requests
from PIL import Image, ImageDraw, ImageFont
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env


def generate_image(prompt: str, output_path: str = "story.jpg"):
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        raise ValueError("Переменная окружения STABILITY_API_KEY не установлена")

    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*"
    }
    data = {
        "prompt": prompt,
        "output_format": "jpeg"
    }

    response = requests.post(url, headers=headers, files={"none": ""}, data=data)

    if response.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(response.content)
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=f"Ошибка при генерации изображения: {response.text}")

    return output_path


def add_text_to_image(image_path: str, text: str, output_path: str = "story_text.jpg",
                      font_path: str = "Roboto-Thin.ttf"):
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось открыть изображение: {str(e)}")

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, 65)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось загрузить шрифт: {str(e)}")

    img_width, _ = img.size
    x, y = 100, 100

    # Разбиваем текст на строки, чтобы он не выходил за границы изображения
    lines = []
    line = ""
    for word in text.split():
        if draw.textlength(line + word, font) <= img_width - 200:
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    ascent, descent = font.getmetrics()
    line_height = ascent + descent

    overlay = Image.new("RGBA", (int(max(draw.textlength(line, font) for line in lines)),
                                 int(line_height * len(lines))), (0, 0, 128, 180))
    img.paste(overlay, (int(x), int(y)), mask=overlay)

    y_offset = y
    for line in lines:
        draw.text((x, y_offset), line, font=font, fill=(255, 0, 0))
        y_offset += line_height

    img = img.convert("RGB")
    img.save(output_path)

    return output_path
