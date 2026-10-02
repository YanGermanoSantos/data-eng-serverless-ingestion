import json
import os
from datetime import datetime
import boto3
# from dotenv import load_dotenv  # <-- LOCAL: O Lambda não usa arquivo .env
import requests

# load_dotenv()

def get_secret() -> str:
    return os.getenv('API_KEY')

def lambda_handler(event, context) -> dict:
    api_key = get_secret()

    print("Buscando dados da API...")
    url = f'https://api.openweathermap.org/data/2.5/weather?q=Sao Paulo,BR&units=metric&appid={api_key}'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code}")
        return {
            'statusCode': response.status_code,
            'body': json.dumps('Erro ao buscar dados da API'),
        }

    data = response.json()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f'clima_sp_{timestamp}.json'
    
    # local_path = f'tmp/{file_name}' 
    local_path = f'/tmp/{file_name}' 
    # folder = os.path.dirname(local_path)  
    # os.makedirs(folder, exist_ok=True)

    with open(local_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Arquivo salvo temporariamente em: {local_path}")

    bucket_name = os.getenv("S3_BUCKET")
    
    # session = boto3.Session(profile_name='estudos-aws')  # <-- LOCAL: Usa o perfil do seu computador
    s3_client = boto3.client('s3')  # <-- AWS: O Lambda usa as permissões nativas (IAM Role) automaticamente
    
    s3_client.upload_file(local_path, bucket_name, f"raw/clima/{file_name}")
    print(f"Upload concluído para s3://{bucket_name}/raw/clima/{file_name}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Ingestão concluída com sucesso!'),
    }

# if __name__ == '__main__':
#     lambda_handler()  #