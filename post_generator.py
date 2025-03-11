# post_generator.py
import os
import openai
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

# Устанавливаем API ключи
openai.api_key = os.getenv("OPENAI_API_KEY")
currentsapi_key = os.getenv("CURRENTS_API_KEY")

if not openai.api_key or not currentsapi_key:
    raise ValueError("Переменные окружения OPENAI_API_KEY и CURRENTS_API_KEY должны быть установлены")

def get_recent_news(topic: str):
    url = "https://api.currentsapi.services/v1/latest-news"
    params = {
        "language": "en",
        "keywords": topic,
        "apiKey": currentsapi_key,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных: {response.text}")
    news_data = response.json().get("news", [])
    if not news_data:
        return "Свежих новостей не найдено."
    return "\n".join([article["title"] for article in news_data[:5]])

def generate_content(topic: str):
    recent_news = get_recent_news(topic)
    try:
        # Генерация заголовка
        title = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Придумайте привлекательный и точный заголовок для статьи на тему '{topic}', с учётом актуальных новостей:\n{recent_news}. Заголовок должен быть интересным и ясно передавать суть темы."
            }],
            max_tokens=80,
            temperature=0.5,
            stop=["\n"]
        ).choices[0].message.content.strip()

        # Генерация мета-описания
        meta_description = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Напишите мета-описание для статьи с заголовком: '{title}'. Оно должно быть полным, информативным и содержать основные ключевые слова. В мета-описании не должно быть никаких лишних символов, например \"#\", \".\""
            }],
            max_tokens=220,
            temperature=0.5,
            stop=["."]
        ).choices[0].message.content.strip()

        # Генерация полного контента статьи
        post_content = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""Напишите подробную статью на тему '{topic}', используя последние новости:
{recent_news}. 
Статья должна быть:
1. Информативной и логичной
2. Содержать не менее 1500 символов
3. Иметь четкую структуру с подзаголовками
4. Включать анализ текущих трендов
5. Иметь вступление, основную часть и заключение
6. Включать примеры из актуальных новостей
7. Каждый абзац должен быть не менее 3-4 предложений
8. Текст должен быть легким для восприятия и содержательным
9. В тексте не должно быть никаких лишних символов, например \"#\", \".\""""
            }],
            max_tokens=1500,
            temperature=0.5,
            presence_penalty=0.6,
            frequency_penalty=0.6
        ).choices[0].message.content.strip()

        return {
            "title": title,
            "meta_description": meta_description,
            "post_content": post_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации контента: {str(e)}")
