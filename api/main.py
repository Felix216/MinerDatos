import asyncio
import json
import os
import redis.asyncio as redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

REDIS_KEY = "word_ranking"

async def get_top_words(n: int):
    """Obtiene el Top N de palabras desde el Sorted Set de Redis."""
    results = await redis_client.zrevrange(REDIS_KEY, 0, n - 1, withscores=True)
    
    data = [{"word": word, "count": int(score)} for word, score in results]
    return data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    top_n = 10
    
    try:
        async def listen_to_client():
            nonlocal top_n
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                if message.get("action") == "set_top":
                    top_n = int(message.get("value", 10))
                    print(f"Cliente solicitó Top {top_n}")

        async def send_updates():
            while True:
                data = await get_top_words(top_n)
                await websocket.send_text(json.dumps(data))
                await asyncio.sleep(1)

        listener_task = asyncio.create_task(listen_to_client())
        sender_task = asyncio.create_task(send_updates())
        
        await asyncio.gather(listener_task, sender_task)
        
    except WebSocketDisconnect:
        print("Cliente desconectado")
    except Exception as e:
        print(f"Error en la conexión WebSocket: {e}")