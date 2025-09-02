import json
import boto3
from dotenv import load_dotenv
import os


load_dotenv()
SAVE_AVERAGE_FUNCTION = os.getenv("SAVE_AVERAGE_FUNCTION")
TABLE_NAME = os.getenv("TABLE_NAME")


def get_event_data(event: dict): 
    return json.loads(event["body"])


def create_sqs_queue(region: str):
    sqs = boto3.client('sqs')
    queue_name = f"{region}_QUEUE"

    response = sqs.create_queue(
        QueueName = queue_name,
        Atributes={
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '86400' # sqs item exists for 1 day
        }
    )

    return response['QueueUrl']


def create_save_averages_event(region: str, timezone: str):
    events_client = boto3.client('events')
    lambda_client = boto3.client('lambda')

    rule_name = f"Save_Notify_{region}"

    # creates scheduling rule - 1 hour
    response_rule = events_client.put_rule(
        Name=rule_name,
        ScheduleExpression="rate(1 hour)",
        State="ENABLED"
    )

    rule_arn = response_rule['RuleArn']

    # ensures that EventBridge can invoke the target lambda function
    try:
        lambda_client.add_permission(
            FunctionName=SAVE_AVERAGE_FUNCTION,
            StatementId=f"{rule_name}-Permission",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=rule_arn
        )
    except lambda_client.exceptions.ResourceConflictException:
        # permission already exists - we can ignore it
        pass

    payload = {
        "region": region,
        "timezone": timezone
    }

    # adds detail to event
    events_client.put_targets(
        Rule=rule_name,
        Targets=[
            {
                "Id": "TargetLambda1",
                "Arn": f"arn:aws:lambda:REGIAO:CONTA:function:{SAVE_AVERAGE_FUNCTION}",
                "Input": json.dumps(payload)
            }
        ]
    )



def generate_new_item(event_data: dict, queue_url: str):
    import uuid

    return {
        "id_region": {"s": str(uuid.uuid4())},
        "region": {"S": event_data["region"]},
        "timezone": {"S": event_data["timezone"]},
        "bot_token": {"S": event_data["bot_token"]},
        "channel_id": {"S": event_data["channel_id"]},
        "queue_url": {"S": queue_url}
    }


def save_new_item(new_item: dict): 
    dynamodb = boto3.client("dynamodb")

    response = dynamodb.put_item(
        Table = TABLE_NAME,
        Item=new_item
    )
    
    return response


def lambda_handler(event, context):
    try:
        # get region, bot_token and channel_id from request body
        event_data = get_event_data(event)
        print(event_data)

        # create sqs queue
        queue_url = create_sqs_queue(event_data["region"])

        # create event in eventbridge
        create_save_averages_event(event_data["region"], event_data["timezone"])

        # generate new item
        new_item = generate_new_item(event_data, queue_url)

        # save new item
        response = save_new_item(new_item)

        return {"statusCode": 201, "message": f"Item salvo com sucesso: {response}"}

    except Exception as e:
        return {"statusCode": 500, "message": json.dumps(f"ERROR: {e}")}


# testes locais
if __name__ == "__main__":
    with open("AWS_OFICIAL\\04-Save_new_region\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
