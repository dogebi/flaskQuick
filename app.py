import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Flask 애플리케이션 초기화
app = Flask(__name__)
CORS(app)

# Azure OpenAI API 설정
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")  # 환경 변수에서 API 키 가져오기
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # Azure OpenAI Endpoint
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # API 버전

# 배포된 모델 이름
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # Azure 포털에서 확인한 배포 이름

@app.route('/ask_gpt', methods=['POST'])
def ask_gpt():
    try:
        # 클라이언트로부터 입력받기
        data = request.json
        prompt = data.get("input", "")
        
        # 입력값 확인
        if not prompt:
            return jsonify({"success": False, "error": "No input provided"}), 400

        # ChatCompletion API 호출
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,  # Azure 배포 모델 이름
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )

        # 응답 반환
        answer = response['choices'][0]['message']['content'].strip()
        return jsonify({"success": True, "answer": answer})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
