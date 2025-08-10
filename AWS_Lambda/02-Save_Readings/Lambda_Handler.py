import json
import boto3
from dotenv import load_dotenv
import os

load_dotenv()
TABLE_NAME = os.getenv("TABLE_NAME")


def collect_event_data(event:dict):
    event_body = event['Body']

    date, hour = convert_date_hour(event['requestContext']['requestTime'])

    item = {
        "region" : event_body['region'],
        "measurement" : event_body['measurement'],
        "date" : date,
        "hour" : hour
    }

    return item


def convert_date_hour(requestTime: str):
    months = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }

    date = f"{requestTime[7:11]}-{months[requestTime[3:6]]}-{requestTime[0:2]}"
    hour = requestTime[12:14]

    return date, hour


def save_readings(new_item):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    table.put_item(new_item)


def lambda_handler(event, context):
    # coleta os dados do event e cria o item
    new_item = collect_event_data(event)

    # salva no dynamodb
    save_readings(new_item)

    return {
        "statusCode": 201,
        "body": json.dumps(new_item)
    }


# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\01-Save_Region\\event.json") as f:
        event = json.load(f)
    print(lambda_handler(event, None))