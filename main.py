from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from characterai import aiocai
import asyncio
import os

app = FastAPI()

token = '29422450f9ebdf864bb798a6f9796cdab019d9f1'
client = aiocai.Client(token)

@app.get("/")
async def index():
    # Serve static file using FastAPI's static files capability
    return {"message": "Use /static/index.html to get the index.html file"}

@app.get("/new")
async def new_chat(char: str):
    if not char:
        raise HTTPException(status_code=400, detail="char_id tidak valid")

    try:
        async def create_new_chat():
            async with await client.connect() as chat:
                me = await client.get_me()
                new, _ = await chat.new_chat(char, me.id)
                return new.chat_id if hasattr(new, 'chat_id') else None

        chat_id = await create_new_chat()
        if chat_id:
            return {"chat_id": chat_id}
        raise HTTPException(status_code=500, detail="Gagal membuat chat baru")
    except Exception as e:
        print(f"Terjadi kesalahan saat membuat chat baru: {e}")
        raise HTTPException(status_code=500, detail="Gagal membuat chat baru")

@app.get("/chat")
async def chat(char: str, id: str, text: str):
    if not char or not id or not text:
        raise HTTPException(status_code=400, detail="char_id, chat_id, dan text diperlukan")

    try:
        async def send_message_to_chat():
            async with await client.connect() as chat:
                message = await chat.send_message(char, id, text=text)
                return {'name': message.name, 'text': message.text}

        result = await send_message_to_chat()
        if result:
            return result
        raise HTTPException(status_code=500, detail="Gagal mengirim pesan")
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim pesan: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengirim pesan")

@app.get("/search")
async def search(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query pencarian diperlukan")

    try:
        async def search_characters():
            results = await client.search(q)
            if isinstance(results, list):
                return [result.__dict__ for result in results]
            return results

        results = await search_characters()
        if results:
            return results
        raise HTTPException(status_code=500, detail="Gagal melakukan pencarian")
    except Exception as e:
        print(f"Terjadi kesalahan saat mencari karakter: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan pencarian")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
