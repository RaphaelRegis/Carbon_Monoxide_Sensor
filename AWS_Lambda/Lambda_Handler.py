import json
import os
import urllib
import urllib.parse
import urllib.request

def collect_request_body(event):
    body_str = event.get('body', '{}')
    body = json.loads(body_str)
    return body.get('token'), body.get('measurement')

def verify_token(token):
    return token == os.environ("VALIDY_TOKEN")

def classify_measurement(measurement):
    pass

def send_Telegram_message(message):
    TELEGRAM_BOT_TOKEN = os.environ("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ("TELEGRAM_CHAT_ID")
    
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
    # coleta o corpo da requisicao
    token, measurement = collect_request_body(event)    
    
    #verifica a credencial na requisicao
    validity = verify_token(token)
    
    if not validity:
        return {
            "statusCode": 401,
            "message": "Invalid token"
        }
    
    #classifica a medicao
    message = classify_measurement(measurement)
    
    # envia a mensagem para o Telegram
    result = send_Telegram_message(message)
    
    return {
        "statusCode": 200,
        "message": json.dumps(result)
    }