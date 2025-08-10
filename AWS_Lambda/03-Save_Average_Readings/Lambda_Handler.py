import json
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
import os

load_dotenv()

dynamodb = boto3.resources("dynamodb")
readings_table = dynamodb.Table(os.getenv("READINGS_TABLE"))
averages_table = dynamodb.Table(os.getenv("AVERAGES_TABLE"))


def collect_event_data(event: dict):
    dateTime = event['time']
    date = dateTime[0:10]
    hour = dateTime[11:13]
    region = event['detail']['region']

    return date, hour, region


def get_newer_readings(date: str, hour: str, region: str):
    response = readings_table.query(
        KeyConditionExpression=Key('date').eq(date) & Key('hour').eq(hour) & Key('city').eq(region)
    )

    return response["Items"]


def get_average(items: dict):
    average_measurement = 0.0

    for item in items:
        average_measurement += float(item['measurement']['S'])

    average_measurement = average_measurement/len(items)

    return str(average_measurement)


def save_average(new_item: dict):
    averages_table.put_item(new_item)


def lambda_handler(event, context):
    # coleta os dados do event
    date, hour, region = collect_event_data(event)

    # pega as leituras correspondentes
    newer_readings = get_newer_readings(date, hour, region)

    # calcula a media
    average = get_average(newer_readings)

    # salva no dynamodb
    new_item = {
        "region": region,
        "date": date,
        "hour": hour,
        "average_measurement": average
    }

    save_average(new_item)

    return {
        "statusCode": 201,
        "body": json.dumps(new_item)
    }
    ...


# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\01-Save_Region\\event.json") as f:
        event = json.load(f)
    print(lambda_handler(event, None))