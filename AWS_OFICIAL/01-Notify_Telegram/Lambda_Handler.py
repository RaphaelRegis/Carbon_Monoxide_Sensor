from dotenv import load_dotenv
import os
import requests
import json

# variaveis de ambiente
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


def get_event_data(event: dict) -> dict:
    for record in event["Records"]:
        region = record["dynamodb"]["NewImage"]["region"]["S"]
        average_measurement = record["dynamodb"]["NewImage"]["average_measurement"]["S"]
        date = record["dynamodb"]["NewImage"]["date"]["S"]
        hour = record["dynamodb"]["NewImage"]["hour"]["S"]

    return {
        "region": region,
        "average_measurement": average_measurement,
        "date": date,
        "hour": hour,
    }


def get_ppm_message(event_data: dict, co_recommentations: dict) -> str:
    # define initial message info
    new_message = f"Média mais recente: {int(event_data['average_measurement'])} ppm\nData: {event_data['date']} | Hora: {event_data['hour']}:00\n"

    # run through ppm messages
    for range in co_recommentations["ranges"]:
        min_val = range["min"]
        max_val = range["max"]

        # verify if it's the last posible message
        if max_val is None:
            if int(event_data["average_measurement"]) >= min_val:
                return new_message + range["message"]

        # verify if the ppm measure is in the range of current min and max values
        elif min_val <= int(event_data["average_measurement"]) <= max_val:
            return new_message + range["message"]

    # error in case of incompatible ppm
    raise Exception(f"Valor fora do intervalo conhecido: {int(event_data['average_measurement'])}")


def send_message(message: str):
    # prepara o payload com a mensagem para enviar
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": message}

    # envia a mensagem
    result = requests.post(url=url, data=payload)

    sended_message = False
    if result.status_code == 200:
        sended_message = True
    else:
        print(f"Falha ao enviar a mensagem: {result.text}")
        sended_message = False

    return sended_message


def handle_old_messages(sqs_url: str):
    # procura mensagens no sqs


    # tenta enviar as que ficaram caso tenha alguma


    # se der sucesso, ela eh excluida do sqs
    ...


def handle_new_message(sqs_url: str):
    # tenta enviar a nova mensagem


    # em caso de falha, envia ela pro sqs
    ...


def lambda_handler(event, context):
    try:
        event_data = get_event_data(event=event)

        # query for sqs_url, bot_token and channel_id - FACA ESSA PARTE QUANDO A TABELA CORRETA JA ESTIVER FUNCIONANDO

        # lida com mensagens nao enviadas
        handle_old_messages()

        # creates new message
        with open("AWS_OFICIAL\\01-Notify_Telegram\\co_recommendations.json", encoding="utf-8") as g:
            co_recommentations = json.load(g)

        new_message = get_ppm_message(event_data, co_recommentations)

        # tenta enviar a nova mensagem
        handle_new_message()

        return {"statusCode": 200, "message": new_message}

    except Exception as e:
        return {"statusCode": 500, "message": json.dumps(f"ERROR: {e}")}


# testes locais
if __name__ == "__main__":
    with open("AWS_OFICIAL\\01-Notify_Telegram\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
