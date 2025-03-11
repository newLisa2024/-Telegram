# app.py
import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# Импорт функций генерации постов и изображений
from post_generator import generate_content
from image_generator import generate_image, add_text_to_image

load_dotenv()  # Загружаем переменные окружения из .env

app = FastAPI()

class Topic(BaseModel):
    topic: str

@app.post("/generate-post")
async def generate_post_api(topic: Topic):
    return generate_content(topic.topic)

# Пример эндпоинта для генерации изображения и добавления текста
class ImageRequest(BaseModel):
    prompt: str  # Промпт для генерации изображения
    text: str    # Текст, который будет наложен на изображение

@app.post("/generate-image")
async def generate_image_api(request: ImageRequest):
    image_path = generate_image(request.prompt, output_path="temp/story.jpg")
    output_image = add_text_to_image(image_path, request.text, output_path="temp/story_text.jpg")
    return {"message": "Изображение с текстом успешно сгенерировано", "image_file": output_image}

@app.get("/")
async def root():
    return {"message": "Service is running"}

@app.get("/heartbeat")
async def heartbeat_api():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)

