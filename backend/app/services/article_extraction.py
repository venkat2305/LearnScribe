import requests
from app.config import config


def webpage_extractor_rapid_api(article_url):
    url = "https://webpage-extractor1.p.rapidapi.com/webpage_extractor/text"
    payload = {"url": article_url}
    headers = {
        "x-rapidapi-key": config.RAPID_API_KEY,
        "x-rapidapi-host": "webpage-extractor1.p.rapidapi.com",
        "Content-Type": "application/json",
        "x-token": "Makshad Nai Bhoolna @ 2025"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def get_article_transcript(article_url):
    transcript = webpage_extractor_rapid_api(article_url)
    return transcript.get('response', '')
