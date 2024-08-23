from quart import Quart, request, jsonify
from characterai import aiocai
import asyncio

app = Quart(__name__)

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

@app.route('/new', methods=['GET'])
async def new_chat():
    char_id = request.args.get('char')
    if not char_id:
        return jsonify({"error": "char_id tidak valid"}), 400
    chat_id = await create_new_chat(char_id)
    if chat_id:
        return jsonify({"chat_id": chat_id})
    return jsonify({"error": "Gagal membuat chat baru"}), 500

@app.route('/chat', methods=['GET'])
async def chat():
    char_id = request.args.get('char')
    chat_id = request.args.get('id')
    text = request.args.get('text')
    if not char_id or not chat_id or not text:
        return jsonify({"error": "char_id, chat_id, dan text diperlukan"}), 400
    result = await send_message_to_chat(chat_id, char_id, text)
    if result:
        return jsonify(result)
    return jsonify({"error": "Gagal mengirim pesan"}), 500

@app.route('/search', methods=['GET'])
async def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query pencarian diperlukan"}), 400
    results = await search_characters(query)
    if results:
        return jsonify(results)
    return jsonify({"error": "Gagal melakukan pencarian"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
