from dotenv import load_dotenv
import os
import requests
import json

# variaveis de ambiente
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

mensagem = "Deus abençoe"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHANNEL_ID,
    "text": mensagem
}

resposta = requests.post(url=url, data=payload)

if resposta.status_code == 200:
    print("Mensagem enviada com sucesso!")
else:
    print(f"Falha ao enviar a mensagem: {resposta.text}")
    
def lambda_handler(event, context):
    # coleta a regiao e a medida de CO
    
    # busca os dados necessarios
    
    # lida com mensagens nao enviadas
    
    # tenta enviar a nova mensagem 
    
    return {
        "statusCode": 200,
        "message": json.dumps()
    }
    pass

if __name__ == "__main__":
    with open("AWS_Lambda\\save_data\\save_data_average\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))