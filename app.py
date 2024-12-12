import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Flask 애플리케이션 초기화
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Azure OpenAI 설정
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")  # 환경 변수에서 API 키 가져오기
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # 환경 변수에서 엔드포인트 가져오기
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # API 버전
deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # 배포 이름 가져오기

@app.route('/ask_gpt', methods=['POST'])
def ask_gpt():
    try:
        data = request.json
        prompt = data.get("input", "")

        if not prompt:
            return jsonify({"success": False, "error": "No input provided"}), 400

        # ChatCompletion 호출
        response = openai.ChatCompletion.create(
            # deployment_id=deployment_id,  # 배포 이름 사용
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )

        answer = response['choices'][0]['message']['content'].strip()
        return jsonify({"success": True, "answer": answer})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
