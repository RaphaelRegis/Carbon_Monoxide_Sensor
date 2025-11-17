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

    # this value works as a index to control unsent messages
    sent_messages_index = 0

    for message_dict in channel_messages:
        message_sent = send_message(message_dict, region_data["channel_id"], region_data["bot_token"])

        if message_sent:
            sent_messages_index += 1
            print(f"Mensagem enviada: {message_dict['message_text']}")
        
        else:
            print("Falha ao enviar as mensagens!")
            break

    return channel_messages[sent_messages_index:]


def send_message(message_dict: dict, channel_id: str, bot_token:str):
    # prepares the payload with the message to send
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    photo_url = f"{os.environ['BOT_IMAGES_URL']}{message_dict['air_quality']}.png"
    payload = {
        "chat_id": channel_id, 
        "photo": photo_url, 
        "caption": message_dict["message_text"],
        "parse_mode": "HTML"}
    

    # tries to send the message
    result = requests.post(url=url, data=payload)

    sent_message = False
    if result.status_code == 200:
        sent_message = True
    else:
        print(f"Falha ao enviar a mensagem: {result.text}")
        sent_message = False

    return sent_message


def update_sqs_queue(not_sent_messages:list, region_data: dict):
    sqs_client = boto3.client("sqs")

    # if there are unsent messages, send the list with them to the queue
    if len(not_sent_messages) > 0:
        print("Devolvendo mensagens para o SQS")
        response = sqs_client.send_message(
            QueueUrl=region_data["sqs_queue_url"],
            MessageBody=json.dumps(not_sent_messages),
            MessageGroupId="channel_messages",
        )


def lambda_handler(event, context):

    try:
        # get region from sqs event
        event_data = get_event_data(event)
        print(f"Event data: {event_data}")

        # retrieves the data correctly according to the region
        region_data = get_region_data(event_data["reading_region"])
        print(f"Region data: {region_data}")

        # try sending the messages to the Telegram channel
        not_sent_messages = handle_messages(event_data["channel_messages"], region_data)
        print(f"Mensagens nao enviadas: {not_sent_messages}")

        # handles messages that were not sent
        update_sqs_queue(not_sent_messages, region_data)

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