import json
from dotenv import load_dotenv
import os
##import boto3
##from boto3.dynamodb.conditions import Key

#load environment variables
load_dotenv()
CITIES_TABLE = os.getenv("CITIES_TABLE")

# load boto3 utils
##sqs = boto3.client("sqs")
##dynamodb = boto3.resources("dynamodb")
##table = dynamodb.Table(CITIES_TABLE)

def get_pending_notifications(city):
    
    # primeiro pega a fila certa do sqs
    ##response_query = table.query(
    ##    KeyConditionExpression=Key('city').eq(city)
    ##)

    ##SQS_URL = response_query['Items'][0]['sqs_url']['S']
    

    # em seguida pega as notificacoes pendentes
    ##response = sqs.receive_message(
    ##    QueueUrl=SQS_URL,
    ##    MaxNumberOfMessages=10,
    ##    WaitTimeSeconds=0
    ##)

    ##if 'Messages' in response:
    ##    return response['Messages']
    
    return []

# TO DO: implementar o send_message
def send_message():
    ...

def handle_old_messages(old_messages):
    for i in range(old_messages):
        result = send_message(old_messages[i])

        # se a mensagem tiver sido enviada, ela eh excluido da fila sqs
        ##if result == True:
        ##    sqs.delete_message(
        ##        QueueUrl=SQS_URL,
        ##        ReceiptHandle=old_messages[i]['ReceiptHandle']
        ##    )

def get_new_average(event):
    for record in event['Records']:
        new_average = record['dynamodb']['NewImage']['average']['S']    

    return float(new_average)

def handle_new_message(new_message):
    result = send_message(new_message)

    ##if result == False:
    ##    sqs.send_message(
    ##        QueueUrl = SQS_URL,
    ##        MessageBody = new_message
    ##    )

# TO DO: implementar get_recomendation
def get_recomendation(newer_average):
    ...

def lambda_handler(event, context):
    # cuida de mensagens no sqs
    old_messages = get_pending_notifications(event['Records'][0]['dynamodb']['NewImage']['city']['S'])
    handle_old_messages(old_messages)

    # pega a nova recomendacao
    newer_average = get_new_average(event)
    new_message = get_recomendation(newer_average)
    
    # cuida da mensagem atual
    handle_new_message(new_message)

    return {
        'statusCode': 200,
        'message': new_message
    }

# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\notify_telegram\\send_average\\event.json") as f:
        event = json.load(f)    
    
    print(lambda_handler(event, None))