import os

def collect_request_body(event):
    pass

def verify_token(token):
    return token == os.environ("VALIDY_TOKEN")

def classify_measurement(measurement):
    pass

def send_message(message):
    pass


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
    send_message(message)
    
    return {
        "statusCode": 200,
        "message": "Measurement processed sucessfully"
    }