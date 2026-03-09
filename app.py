from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# デフォルトのシステムプロンプト
DEFAULT_SYSTEM_PROMPT = "あなたはSenninAIという名前の、非常に賢く謙虚なAIアシスタントです。"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/accountsetting')
def account_setting():
    return render_template('accountsetting.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    
    # フロントエンドの設定値を取得（値がない場合はデフォルト値を使用）
    system_prompt = data.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
    model_name = data.get("model", "llama-3.3-70b-versatile")
    user_api_key = data.get("api_key")
    
    # フロントエンドから送られてきた履歴を取得（高性能化対応）
    chat_history = data.get("history", [])

    # APIキーの選定：ユーザー入力があればそれを優先、なければ環境変数を使用
    active_api_key = user_api_key if user_api_key else os.environ.get("GROQ_API_KEY")

    if not active_api_key:
        return jsonify({"error": "APIキーが設定されていません。設定画面で入力するかサーバーの環境変数を確認してください。"}), 400

    try:
        # リクエストごとにクライアントを生成（カスタムキー対応のため）
        dynamic_client = Groq(api_key=active_api_key)
        
        # メッセージリストの構築（システムプロンプト + 過去の履歴 + 今回の質問）
        messages = [{"role": "system", "content": system_prompt}]
        for msg in chat_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})
        
        completion = dynamic_client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=False
        )
        response_text = completion.choices[0].message.content
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render等の環境に対応するためPORT環境変数を確実に取得
    # ポートが検出されないエラーを回避するため、host='0.0.0.0' を固定
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
