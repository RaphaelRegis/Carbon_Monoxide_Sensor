import json
import boto3
from dotenv import load_dotenv
import os


load_dotenv()
SAVE_AVERAGE_AND_NOTIFY_FUNCTION = os.getenv("SAVE_AVERAGE_AND_NOTIFY_FUNCTION")
TABLE_NAME = os.getenv("TABLE_NAME")


def collect_event_data(event: dict):
    event_body = json.loads(event['Body'])
    region = event_body['region']
    token = event_body['token']
    telegram_channel= event_body['telegram_channel']

    return region, token, telegram_channel


def create_sqs_queue(region: str):
    sqs = boto3.client('sqs')
    queue_name = f"{region}_QUEUE"

    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '86400' # sqs item exists for 1 day
        }
    )

    return response['QueueUrl']


def create_event(region: str):
    events_client = boto3.client('events')
    lambda_client = boto3.client('lambda')

    rule_name = f"Save_Notify_{region}"

    # cria a regra de agendamento - 1 hora
    response_rule = events_client.put_rule(
        Name=rule_name,
        ScheduleExpression="rate(1 hour)",
        State="ENABLED"
    )

    rule_arn = response_rule['RuleArn']

    # garante que o EventBridge possa invocar a funcao lambda alvo
    try:
        lambda_client.add_permission(
            FunctionName=SAVE_AVERAGE_AND_NOTIFY_FUNCTION,
            StatementId=f"{rule_name}-Permission",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=rule_arn
        )

    except lambda_client.exceptions.ResourceConflictException:
        # Ja existe a permissao - podemos ignorar
        pass

    payload = {
        "region": region
    }

    events_client.put_targets(
        Rule=rule_name,
        Targets=[
            {
                "Id": "TargetLambda1",
                "Arn": f"arn:aws:lambda:REGIAO:CONTA:function:{SAVE_AVERAGE_AND_NOTIFY_FUNCTION}",
                "Input": json.dumps(payload)
            }
        ]
    )


def save_new_region(item: dict):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    table.put_item(item)


def lambda_handler(event, context):
    # coleta dados do event
    region, telegram_token, telegram_channel = collect_event_data

    # cria fila sqs
    queue_url = create_sqs_queue(region)

    # cria evento do EventBridge
    create_event(region)

    # salva dados no dynamodb
    item = {
        "region": region,
        "telegram_token": telegram_token,
        "telegram_channel": telegram_channel,
        "sqs_queue_url": queue_url
    }

    save_new_region(item)

    return {
        "statusCode": 201,
        "body": json.dumps(item)
    }

    pass

# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\01-Save_Region\\event.json") as f:
        event = json.load(f)
    print(lambda_handler(event, None))