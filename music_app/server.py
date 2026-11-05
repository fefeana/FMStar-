from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    lyrics = data.get('text', '')
    return jsonify({
        "status": "success",
        "message": f"تم توليد لحن أكوستيك لكلمات: ({lyrics[:20]}...)",
        "audio_url": "https://example.com/mock-audio.mp3"
    })

if __name__ == '__main__':
    print("⚔️ الساموراي جاهز! الخادم يعمل على http://127.0.0.1:5000")
    app.run(port=5000)
