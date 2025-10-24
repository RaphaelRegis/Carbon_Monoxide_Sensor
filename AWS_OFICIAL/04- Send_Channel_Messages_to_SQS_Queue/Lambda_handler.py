import json
import boto3
import os


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
    new_message = f"Média mais recente: {int(event_data['average_measurement'])} ppm\nData: {event_data['reading_date_hour'][:10]} | Hora: {event_data['reading_date_hour'][11:]}:00\n"

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


def send_message_to_sqs(body_message: str, sqs_queue_url):
    sqs = boto3.client('sqs')

    response = sqs.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=body_message
    )

    print(f"Message sent to SQS: {response}")


def call_lambda_function(reading_region: str, lambda_function_name: str):
    lambda_client = boto3.client('lambda')

    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType='Event',
        Payload=json.dumps({"reading_region": reading_region})
    )

    print(f"Lambda function called: {response}")


def lambda_handler(event, context):
    try:
        print(f"Event: {event}")
        # get the new object
        event_data = get_event_data(event)

        # creates the new message
        with open("co_recommendations.json", encoding="utf-8") as f:
            co_recommendations = json.load(f)

        new_message = get_ppm_message(event_data, co_recommendations)

        # get sqs_queue_url
        sqs_queue_url = os.environ[f"{event_data["reading_region"].upper()}_SQS_QUEUE_URL"]

        # prepare sqs body message
        message_body = json.dumps({"message": new_message, "reading_date_hour": event_data["reading_date_hour"]})

        # send message to sqs
        send_message_to_sqs(message_body, sqs_queue_url)

        # chama a funcao lambda para mandar mensagens
        lambda_function_name = os.environ["LAMBDA_FUNCTION_NAME"]

        call_lambda_function(event_data["reading_region"], lambda_function_name)


        return {
            'statusCode': 200,
            'body': json.dumps(f"New message: {new_message}")
        }


    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {e}")
        }
