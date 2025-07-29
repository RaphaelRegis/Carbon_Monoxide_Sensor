import json
import os
from dotenv import load_dotenv
import urllib
import urllib.parse
import urllib.request

# load environment variables
load_dotenv()
VALIDY_TOKEN = os.getenv("VALIDY_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def collect_request_body(event):
    body = json.loads(event['body'])
    return body['token'], body['measurement']

def verify_token(token):
    return token == VALIDY_TOKEN

def classify_measurement(measurement):
    
    # REAJUSTAR DE ACORDO COM FONTES CONFIÁVEIS
    measurement = int(measurement)
    
    classificacao = ""
    if measurement < 9:
        classificacao = "Ar bom"
    elif measurement >= 9 and measurement <= 10:
        classificacao = "Ar moderado"
    elif measurement >= 11 and measurement <= 50:
        classificacao = "Ar ruim"
    elif measurement > 50:
        measurement = "Ar péssimo"
        
    return classificacao

def send_Telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")
    
    req= urllib.request.Request(url, data=data)
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())
    
def lambda_handler(event, context):
    # collect request body variables
    token, measurement = collect_request_body(event)    
    
    #verifica a credencial na requisicao
    validity = verify_token(token)
    
    if validity == False:
        return {
            "statusCode": 401,
            "message": "Invalid token"
        }
    
    #classifica a medicao
    message = classify_measurement(measurement)
    
    # envia a mensagem para o Telegram
    #result = send_Telegram_message(message)
    result = {
        "Token": token,
        "Measurement": measurement,
        "Message": message
    }
    return {
        "statusCode": 200,
        "message": json.dumps(result)
    }
    
# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\event.json") as f:
        event = json.load(f)    
    
    print(lambda_handler(event, None))
    