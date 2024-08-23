from flask import Flask, request, jsonify
from characterai import aiocai
import asyncio

app = Flask(__name__)

# Inisialisasi client dengan token Anda
token = '29422450f9ebdf864bb798a6f9796cdab019d9f1'
client = aiocai.Client(token)

async def create_new_chat(char_id):
    try:
        async with await client.connect() as chat:
            me = await client.get_me()
            new, _ = await chat.new_chat(char_id, me.id)

            if hasattr(new, 'chat_id'):
                return new.chat_id
            else:
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
        async with await client.connect():
            results = await client.search(query)
            return results
    except Exception as e:
        print(f"Terjadi kesalahan saat mencari karakter: {e}")
        return None

@app.route('/newchat', methods=['GET'])
def new_chat():
    char_id = request.args.get('char')

    if not char_id:
        return jsonify({"error": "char_id tidak valid"}), 400

    chat_id = asyncio.run(create_new_chat(char_id))
    if chat_id:
        return jsonify({"chat_id": chat_id})
    else:
        return jsonify({"error": "Gagal membuat chat baru"}), 500

@app.route('/chat', methods=['GET'])
def chat():
    char_id = request.args.get('char')
    chat_id = request.args.get('chat_id')
    text = request.args.get('text')

    if not char_id or not chat_id or not text:
        return jsonify({"error": "char_id, chat_id, dan text diperlukan"}), 400

    result = asyncio.run(send_message_to_chat(chat_id, char_id, text))
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Gagal mengirim pesan"}), 500

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')

    if not query:
        return jsonify({"error": "Query pencarian diperlukan"}), 400

    results = asyncio.run(search_characters(query))
    if results:
        return jsonify(results)
    else:
        return jsonify({"error": "Gagal melakukan pencarian"}), 500

if __name__ == '__main__':
    app.run(debug=True)
