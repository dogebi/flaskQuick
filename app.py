import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask 애플리케이션 초기화
app = Flask(__name__)
CORS(app)

# Azure OpenAI API 키와 엔드포인트를 환경 변수에서 가져옵니다.
openai.api_key = os.getenv('AZURE_OPENAI_KEY')  # Azure OpenAI API Key
openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')  # Azure OpenAI Endpoint

# # 환경 변수에서 프록시 설정 가져오기
# os.environ['HTTP_PROXY'] = 'http://80023:nomura49@172.19.248.1:92'
# os.environ['HTTPS_PROXY'] = 'http://80023:nomura49@172.19.248.1:92'

@app.route('/ask_gpt', methods=['POST'])
def ask_gpt():
    try:
        user_input = request.json.get('message')
        app.logger.info(f"Received message: {user_input}")  # Log the incoming message

        if not user_input:
            app.logger.error("No message provided")
            return jsonify({"success": False, "error": "No message provided"}), 400

        response = openai.ChatCompletion.create(
            model="gpt-4o",  # 사용하려는 모델 이름
            messages=[{"role": "user", "content": user_input}],
            max_tokens=150
        )

        answer = response['choices'][0]['message']['content'].strip()
        return jsonify({"success": True, "answer": answer})

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
