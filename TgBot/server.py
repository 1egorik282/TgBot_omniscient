from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/generate', methods=['POST'])
def generate_response():
    data = request.json
    user_message = data.get("prompt", "")
    # Простая логика ответа (можно заменить на вызов модели)
    return jsonify({"response": f"Вы сказали: '{user_message}'. Это тестовый ответ сервера."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)