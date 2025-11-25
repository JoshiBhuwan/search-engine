import httpx
import time
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from contextlib import asynccontextmanager
from fastapi_pagination import Page, add_pagination, paginate
from models import Message

API_URL = "https://november7-730026606190.europe-west1.run.app/messages/"
cache = {"data": None, "timestamp": 0}
CACHE_TTL = 300


async def fetch_messages():
    now = time.time()
    # I could have used an LRU cache here but this is simple example
    if cache["data"] and (now - cache["timestamp"]) < CACHE_TTL:
        return cache["data"]
    
    print("Fetching messages from API...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        messages = []
        skip = 0
        
        while True:
            try:
                resp = await client.get(API_URL, params={"skip": skip, "limit": 100})
                # Looks like there was a rate limit
                if resp.status_code == 403:
                    # My approach is to wait for 2 seconds and try again
                    await asyncio.sleep(2)
                    continue
                    
                resp.raise_for_status()
                data = resp.json()
                
                items = data.get("items", [])
                if not items:
                    break
                    
                messages.extend([Message(**item) for item in items])
                
                if len(items) < 100:
                    break
                    
                skip += 100
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching at skip={skip}: {e}")
                break
        
        cache["data"] = messages
        cache["timestamp"] = now
        print(f"Cache loaded with {len(messages)} messages")
        return messages


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Preloading cache on startup...")
    await fetch_messages()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search", response_model=Page[Message])
async def search(query: Optional[str] = Query(None)):
    messages = await fetch_messages()
 
    if query:
        q_lower = query.lower()
        filtered = [m for m in messages if q_lower in m.message.lower() or q_lower in m.user_name.lower()]
    else:
        filtered = messages
    
    return paginate(filtered)


add_pagination(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
