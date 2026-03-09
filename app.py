from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Groqクライアント設定（環境変数から取得）
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# デフォルトのシステムプロンプト（リポジトリの内容をここに反映）
DEFAULT_SYSTEM_PROMPT = "あなたはSenninAIという名前の、非常に賢く謙虚なAIアシスタントです。"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    system_prompt = data.get("system_prompt", DEFAULT_SYSTEM_PROMPT)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            stream=False
        )
        response_text = completion.choices[0].message.content
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
