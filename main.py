from sanic import Sanic, response
from sanic.request import Request
from characterai import aiocai
import os
import mangum

app = Sanic(__name__)

# Token API untuk karakter AI
token = '29422450f9ebdf864bb798a6f9796cdab019d9f1'
client = aiocai.Client(token)

async def create_new_chat(char_id):
    try:
        async with await client.connect() as chat:
            me = await client.get_me()
            new, _ = await chat.new_chat(char_id, me.id)
            if hasattr(new, 'chat_id'):
                return new.chat_id
            return None
    except Exception as e:
        print(f"Terjadi kesalahan saat membuat chat baru: {e}")
        return None

async def send_message_to_chat(chat_id, char_id, text):
    try:
        async with await client.connect() as chat:
            message = await chat.send_message(char_id, chat_id, text=text)
            return {'name': message.name, 'text': message.text}
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim pesan: {e}")
        return None

async def search_characters(query):
    try:
        results = await client.search(query)
        if isinstance(results, list):
            return [result.__dict__ for result in results]
        return results
    except Exception as e:
        print(f"Terjadi kesalahan saat mencari karakter: {e}")
        return None

@app.route('/')
async def index(request: Request):
    try:
        with open('index.html', 'r') as f:
            html_content = f.read()
        return response.html(html_content)
    except Exception as e:
        return response.json({"error": f"Terjadi kesalahan: {e}"}, status=500)

@app.route('/new', methods=['GET'])
async def new_chat(request: Request):
    char_id = request.args.get('char')
    if not char_id:
        return response.json({"error": "char_id tidak valid"}, status=400)
    chat_id = await create_new_chat(char_id)
    if chat_id:
        return response.json({"chat_id": chat_id})
    return response.json({"error": "Gagal membuat chat baru"}, status=500)

@app.route('/chat', methods=['GET'])
async def chat(request: Request):
    char_id = request.args.get('char')
    chat_id = request.args.get('id')
    text = request.args.get('text')
    if not char_id or not chat_id or not text:
        return response.json({"error": "char_id, chat_id, dan text diperlukan"}, status=400)
    result = await send_message_to_chat(chat_id, char_id, text)
    if result:
        return response.json(result)
    return response.json({"error": "Gagal mengirim pesan"}, status=500)

@app.route('/search', methods=['GET'])
async def search(request: Request):
    query = request.args.get('q')
    if not query:
        return response.json({"error": "Query pencarian diperlukan"}, status=400)
    results = await search_characters(query)
    if results:
        return response.json(results)
    return response.json({"error": "Gagal melakukan pencarian"}, status=500)

# Gunakan Mangum untuk integrasi dengan AWS Lambda
handler = mangum.Mangum(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
