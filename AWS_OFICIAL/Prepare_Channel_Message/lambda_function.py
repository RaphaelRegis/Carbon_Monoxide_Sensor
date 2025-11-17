import json
import boto3
from datetime import datetime
import os

# prepares sqs
sqs = boto3.client('sqs')

def get_event_data(event):
    for record in event["Records"]:
        reading_region = record["dynamodb"]["NewImage"]["reading_region"]["S"]
        reading_date_hour = record["dynamodb"]["NewImage"]["reading_date_hour"]["S"]
        average_measurement = record["dynamodb"]["NewImage"]["average_measurement"]["S"]

    return {
        "reading_region": reading_region,
        "reading_date_hour": reading_date_hour,
        "average_measurement": average_measurement
    }


def get_ppm_message(event_data: dict, co_recommentations: dict) -> str:
    # define initial message info
    data_obj = datetime.strptime(event_data['reading_date_hour'][:10], '%Y-%m-%d')
    new_message = f"Média mais recente: {int(event_data['average_measurement'])} ppm\nData: {data_obj.strftime("%d/%m/%Y")} | Hora: {event_data['reading_date_hour'][11:]}:00\n"

    # run through ppm messages
    for range in co_recommentations["ranges"]:
        min_val = range["min"]
        max_val = range["max"]

        # verify if it's the last posible message
        if max_val is None:
            if int(event_data["average_measurement"]) >= min_val:
                return {"message_text": f"{new_message}{range['message']}", "air_quality": range["air_quality"]}

        # verify if the ppm measure is in the range of current min and max values
        elif min_val <= int(event_data["average_measurement"]) <= max_val:
            return {"message_text": f"{new_message}{range['message']}", "air_quality": range["air_quality"]}

    # error in case of incompatible ppm
    raise Exception(f"Valor fora do intervalo conhecido: {int(event_data['average_measurement'])}")


def get_sqs_messages(sqs_queue_url: str):
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url
    )

    if "Messages" in response:
        # delete the message from the queue
        sqs.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=response["Messages"][0]["ReceiptHandle"]
        )

        return json.loads(response["Messages"][0]["Body"])

    return []


def get_new_message_list(sqs_messages: list, new_message: str) -> list:
    new_message_list = []

    # get the list with previous messages if there are any and put them in the new list
    for old_message in sqs_messages:
        new_message_list.append(old_message)
            

    # add the new message
    new_message_list.append(new_message)

    return new_message_list


def call_lambda_function(reading_region: str, channel_messages: list, lambda_function_name: str):
    lambda_client = boto3.client('lambda')

    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType='Event',
        Payload=json.dumps({"reading_region": reading_region, "channel_messages": channel_messages})
    )

    return response


def lambda_handler(event, context):
    try:
        # get the new object
        event_data = get_event_data(event)
        print(f"Dados do evento: {event_data}")

        # creates the new message
        with open("co_recommendations.json", encoding="utf-8") as f:
            co_recommendations = json.load(f)

        new_message = get_ppm_message(event_data, co_recommendations)
        print(f"Nova messagem: {new_message}")

        # get sqs_queue_url
        sqs_queue_url = os.environ[f"{event_data["reading_region"].upper()}_SQS_QUEUE_URL"]

        # procura outras mensagens no sqs
        sqs_messages = get_sqs_messages(sqs_queue_url)
        print(f"Mensagens anteriores: {sqs_messages}")

        # prepare channel messages list
        channel_messages = get_new_message_list(sqs_messages, new_message)
        print(f"Nova mensagens para o canal: {channel_messages}")

        # calls the Lambda function to send the messages
        lambda_function_name = os.environ["LAMBDA_FUNCTION_NAME"]

        response = call_lambda_function(event_data["reading_region"], channel_messages, lambda_function_name)
        print(f"{response}")

        return {
            'statusCode': 200,
            'body': json.dumps(f"New message: {new_message}")
        }


    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {e}")
        }
