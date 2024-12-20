import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, PartitionKey
import logging


# 로그 형식 정의 (시간, 로그 레벨, 메시지)
log_format = '%(asctime)sZ: [%(levelname)s] %(message)s'

# 로그 기본 설정: 시간 형식, 로그 레벨 및 출력 형식 설정
logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format=log_format,   # 로그 형식 설정
    handlers=[logging.StreamHandler()]  # 콘솔로 출력 (파일로도 출력 가능)
)

# Managed Identity Auth
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

# Flask app init
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#-----------------------------------------------------------------
# Azure OpenAI Setting
# openai.api_type = "azure"
# openai.api_key = os.getenv("AZURE_OPENAI_KEY")  # Get ENV API Key
#-----------------------------------------------------------------
# token method
openai.api_type = "azure_ad"
openai.api_key = token.token  # Managed Identity Get to access Token

openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # Get Env
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # API Version
deployment_id = os.getenv("AZURE_OPENAI_MODEL")  # Get Deploy Name(mini-ZZ)

# Cosmos DB 연결 설정
COSMOS_DB_URI = os.getenv("COSMOS_DB_URI")  # Cosmos DB URI
COSMOS_DB_KEY = token.token  # Managed Identity Get to access Toke  # Cosmos DB Key
# COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")  # Cosmos DB Key
DATABASE_NAME = os.getenv("DATABASE_NAME")  # 데이터베이스 이름
CONTAINER_NAME = os.getenv("CONTAINER_NAME")  # 컨테이너 이름 (컬렉션에 해당)

# Cosmos DB
def get_db_connection():
    # Cosmos DB 클라이언트 연결
    client = CosmosClient(COSMOS_DB_URI, COSMOS_DB_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    print("Connected to Azure Cosmos DB SQL API")
    logging.info("Connected to Azure Cosmos DB SQL API")
    return container  # Cosmos DB의 컨테이너 객체 반환

@app.route('/ask_gpt', methods=['POST'])
def ask_gpt():
    try:
        data = request.json
        prompt = data.get("input", "")

        if not prompt:
            return jsonify({"success": False, "error": "No input provided"}), 400

        # ChatCompletion Call
        response = openai.ChatCompletion.create(
            deployment_id=deployment_id,  # Deploy Name
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
    
# azure Cosmos DB
@app.route('/api/faqs', methods=['GET'])
def get_faq():
    # Cosmos DB 클라이언트 연결
    container=get_db_connection()

    # Cosmos DB에서 데이터를 쿼리하여 가져오기
    query = "SELECT * FROM c"  # SQL 쿼리 (전체 데이터를 가져옴)
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    # 각 아이템의 '_id'는 이미 문자열로 되어 있기 때문에 추가적인 변환이 필요하지 않음
    for item in items:
        item['id'] = item['id']  # Cosmos DB에서 _id는 id로 제공

    return jsonify(items)  # JSON 형식으로 반환

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
