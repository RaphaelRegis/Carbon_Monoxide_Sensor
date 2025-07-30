import json
from dotenv import load_dotenv
import os
#from boto3.dynamodb.conditions import Key

# load environment variables
load_dotenv()
TABLE_NAME = os.getenv("TABLE_NAME")
SQS_URL = os.getenv("SQS_URL")

# load boto3 dynamodb utils
#dynamodb = boto3.resources("dynamodb")
#table = dynamodb.Table(TABLE_NAME)

#load boto3 sqs utils
#sqs = boto3.client("sqs")

def get_query_criteria(event):
    ...

def get_measurement_data(date, hour):
    # query measurements based in date and hour
    # response = table.query(
    #     KeyConditionExpression=Key('date').eq(date) & Key('hour').eq(hour)
    # )

    # return response['Items']
    ...

def get_average_measurement(items: list):
    average_measurement = 0.0

    for i in range(items):
        average_measurement += items[i]['measurement']

    average_measurement = average_measurement/len(items)

    return average_measurement
    ...

def get_recomendation(new_average_measurement):
    ...

def create_new_message(new_average_measurement, recomendation):
    new_message = f"PPM CO: {new_average_measurement}; Recomendação: {recomendation}"
    return new_message

def get_pending_notifications():
    pending_notifications = []
    response = sqs.receive_message(
        QueueUrl=SQS_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=0
    )

    if 'Messages' in response:
        return response['Messages']
    else:
        return pending_notifications

def send_message(message):
    ...

def handle_old_messages(old_messages):
    for i in range(old_messages):
        result = send_message(old_messages[i])

        # apaga a mensagem do sqs se ela tiver sido enviada corretamente
        if result == True:
            sqs.delete_message(
                QueueUrl=SQS_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )

def handle_new_message(new_message):
    result = send_message(new_message)

    # se nao tiver sucesso, manda a mensagem pro sqs
    if result == False:
        sqs.send_message(
            QueueUrl = SQS_URL,
            MessageBody = new_message
        )

def lambda_handler(event, context):
    # get query criteria
    date, hour = get_query_criteria(event)

    # query dynamodb data
    measurement_data = get_measurement_data(date, hour)

    # calcular media, classificar leitura e criar mensagem
    new_average_measurement = get_average_measurement(measurement_data)
    recomendation = get_recomendation(new_average_measurement)
    new_message = create_new_message(new_average_measurement, recomendation)

    # ele vai pegar uma lista com as mensagens pendentes
    old_messages: list = get_pending_notifications()

    # vai tentar enviar as mensagens pendentes e excluí-las de acordo
    handle_old_messages(old_messages)
    
    # tenta enviar a mensagem atual
    handle_new_message(new_message)
    
    return {
        'statusCode': 200,
        'message': new_message
    }
    
# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\notify_telegram\\event.json") as f:
        event = json.load(f)    
    
    print(lambda_handler(event, None))