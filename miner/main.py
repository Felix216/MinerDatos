import os
import time
import requests
import redis
import base64
from extractor import extract_words_from_code

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
REDIS_KEY = "word_ranking"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def search_repositories(language, sort="stars", order="desc", per_page=5):
    """Busca los repositorios más populares por lenguaje."""
    url = f"https://api.github.com/search/repositories?q=language:{language}&sort={sort}&order={order}&per_page={per_page}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Error buscando repositorios: {response.status_code} - {response.text}")
        return []

def process_repository(repo_full_name, language):
    """Busca archivos de código dentro de un repositorio específico."""
    print(f"Procesando repositorio: {repo_full_name} ({language})")
    
    ext = "py" if language == "python" else "java"
    url = f"https://api.github.com/search/code?q=extension:{ext}+repo:{repo_full_name}&per_page=10"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return

    items = response.json().get("items", [])
    for item in items:
        file_url = item.get("url")
        file_res = requests.get(file_url, headers=HEADERS)
        if file_res.status_code == 200:
            content_b64 = file_res.json().get("content", "")
            if content_b64:
                code = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                
                words = extract_words_from_code(code, language)
                
                for word in words:
                    redis_client.zincrby(REDIS_KEY, 1, word)
                    
        time.sleep(2)

def start_mining():
    print("Iniciando el Miner de GitHub...")
    languages = ["python", "java"]
    
    while True:
        for lang in languages:
            repos = search_repositories(lang)
            for repo in repos:
                process_repository(repo["full_name"], lang)
                time.sleep(5)
                
        print("Ciclo completado. Esperando para reiniciar...")
        time.sleep(60)

if __name__ == "__main__":
    start_mining()