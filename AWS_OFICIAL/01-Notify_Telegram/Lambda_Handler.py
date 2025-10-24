import json
import os
from datetime import datetime
import requests
import boto3

sqs_client = boto3.client("sqs")


def get_event_region(event):
    return event.get("reading_region")
   

def get_region_data(reading_region: str):
    region_data = json.loads(os.environ[f"{reading_region.upper()}_DATA"])

    return {
        "sqs_queue_url": region_data["sqs_queue_url"],
        "channel_id": region_data["channel_id"],
        "bot_token": region_data["bot_token"]
    }


def get_sqs_messages(sqs_queue_url: str):
    print("Buscando mensagens no sqs...")
    response = sqs_client.receive_message(
        QueueUrl=sqs_queue_url
    )

    if "Messages" in response:

        print(f"MENSAGENS ENCONTRADAS NA FILA: {response["Messages"]}")

        return response["Messages"]

    else:
        print("Nenhuma mensagem encontrada!")
        return []


def organize_messages(messages: list):
    organized_messages = []

    for msg in messages:
        body_dict = json.loads(msg["Body"])

        # incrementa a lista com o receipthandle da mensagem para que possamos exclui-la da fila depois
        body_dict["ReceiptHandle"] = msg["ReceiptHandle"]
        organized_messages.append(body_dict)

    # Ordenar pela chave "data_hora"
    organized_messages.sort(key=lambda x: datetime.strptime(x["reading_date_hour"], "%Y-%m-%d %H"))

    return organized_messages


def handle_messages(messages: list, region_data: dict):

    for message in messages:
        message_sended = send_message(message["message"], region_data["channel_id"], region_data["bot_token"])

        if message_sended:
            sqs_client.delete_message(
                QueueUrl=region_data["sqs_queue_url"],
                ReceiptHandle=message["ReceiptHandle"]
            )

        else:
            raise Exception("Falha ao enviar as mensagens!")


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


def lambda_handler(event, context):

    try:
        # get region from sqs event
        reading_region = get_event_region(event)
        print(f"REGIAO: {reading_region}")

        # pega os dados corretamente de acordo com a regiao
        region_data = get_region_data(reading_region)
        print(f"DADOS DA REGIAO: {region_data}")

        # busca as mensagens na fila sqs e depois organiza
        messages =  get_sqs_messages(region_data["sqs_queue_url"])
        organized_messages = organize_messages(messages)
        print(f"MENSAGENS DO SQS ORGANIZADAS: {organized_messages}")

        # tenta enviar as mensagens pro canal correto do telegram
        handle_messages(organized_messages, region_data)

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