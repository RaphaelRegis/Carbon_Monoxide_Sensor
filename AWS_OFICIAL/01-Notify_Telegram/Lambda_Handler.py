import json
import os
from datetime import datetime
import requests
import boto3




def get_event_data(event):
    return {"reading_region": event.get("reading_region"), "channel_messages": event.get("channel_messages")}
   

def get_region_data(reading_region: str):
    region_data = json.loads(os.environ[f"{reading_region.upper()}_DATA"])

    return {
        "sqs_queue_url": region_data["sqs_queue_url"],
        "channel_id": region_data["channel_id"],
        "bot_token": region_data["bot_token"]
    }


def handle_messages(channel_messages: list, region_data: dict):

    for message in channel_messages:
        message_sended = send_message(message, region_data["channel_id"], region_data["bot_token"])

        if message_sended:
            channel_messages.remove(message)
        
        else:
            print("Falha ao enviar as mensagens!")
            break

    return channel_messages


def send_message(message: str, channel_id: str, bot_token:str):
    # prepara o payload com a mensagem para enviar
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": channel_id, "text": message}

    # envia a mensagem
    result = requests.post(url=url, data=payload)

    sended_message = False
    if result.status_code == 200:
        sended_message = True
    else:
        print(f"Falha ao enviar a mensagem: {result.text}")
        sended_message = False

    return sended_message


def update_sqs_queue(not_sended_messages:list, region_data: dict):
    sqs_client = boto3.client("sqs")

    # caso hajam mensagens nao enviadas, envia a lista com elas para a fila novamente
    if len(not_sended_messages) > 0:
        response = sqs_client.send_message(
            QueueUrl=region_data["sqs_queue_url"],
            MessageBody=json.dumps(not_sended_messages),
            MessageGroupId="channel_messages",
        )


def lambda_handler(event, context):

    try:
        # get region from sqs event
        event_data = get_event_data(event)
        print(f"Event data: {event_data}")

        # pega os dados corretamente de acordo com a regiao
        region_data = get_region_data(event_data["reading_region"])
        print(f"Region data: {region_data}")

        # tenta enviar as mensagens pro canal do telegram
        not_sended_messages = handle_messages(event_data["channel_messages"], region_data)
        print(f"Mensagens nao enviadas: {not_sended_messages}")

        # lida com as mensagens que nao foram enviadas
        update_sqs_queue(not_sended_messages, region_data)

        # sucess return
        return {
            'statusCode': 200,
            'body': json.dumps(f"MENSAGENS ENVIADAS!")
        }
    
    except Exception as e:
        print(f"ERRO: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"ERRO: {e}")
        }