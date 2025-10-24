import json
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from boto3.dynamodb.conditions import Key
import boto3
import uuid

# variaveis de ambiente
NEWER_READINGS_TABLE = os.environ["NEWER_READINGS_TABLE"]
AVERAGE_READINGS_TABLE = os.environ["AVERAGE_READINGS_TABLE"]

# prepara o dynamodb
dynamodb = boto3.client("dynamodb")


def get_query_parameters(event):
    reading_region = event["detail"]["reading_region"]
    reading_date_hour = get_date_hour(event["detail"]["timezone"])

    return {
        "reading_region": reading_region, 
        "reading_date_hour": reading_date_hour
    }


def get_date_hour(timezone: str):
    # get datetime without considering timezone
    naive_datetime = datetime.now()
    # convert date to sensor timezone
    zi = ZoneInfo(timezone)
    aware_datetime = naive_datetime.astimezone(zi)

    # prepare date and hour - date formatting: Year-month-day | hour formatting: Hour 00-23
    reading_date = aware_datetime.strftime("%Y-%m-%d")
    reading_hour = aware_datetime.strftime("%H")
    # ele pega a hora atual e volta 1 para poder pegar as leituras
    reading_hour = str(int(reading_hour) - 1)

    return f"{reading_date} {reading_hour}"


def get_newer_readings(query_parameters: dict):

    response = dynamodb.query(
        TableName=NEWER_READINGS_TABLE,
        IndexName="reading_region-reading_date_hour-index",
        KeyConditionExpression="reading_region = :reading_region AND reading_date_hour = :reading_date_hour",
        ExpressionAttributeValues={
            ":reading_region": {"S": query_parameters["reading_region"]},
            ":reading_date_hour": {"S": query_parameters["reading_date_hour"]}
        }
    )

    return response["Items"]


def calculate_average(newer_readings: list):
    average_measurement = 0.0
    
    # it goes through all the readings and adds them up
    for reading in newer_readings:
        average_measurement += float(reading["measurement"]["S"])

    # divides the measurement by the number of readings
    average_measurement = float(average_measurement/len(newer_readings)).__ceil__()
    
    return str(int(average_measurement))


def generate_new_item(query_parameters: dict, average_measurement: str):
    return {
        "id_average_measurement": {"S": str(uuid.uuid4())},
        "reading_region": {"S": query_parameters["reading_region"]},
        "reading_date_hour": {"S": query_parameters["reading_date_hour"]},
        "average_measurement": {"S": average_measurement}
    }


def persist_average_reading_item(new_item: dict):
    response = dynamodb.put_item(
        TableName=AVERAGE_READINGS_TABLE,
        Item=new_item
    )


def lambda_handler(event, context):
    try:
        # primeiro pega os dados necessarios para a consulta (regiao, data e hora)
        query_parameters = get_query_parameters(event)

        # consulta as leituras correspondentes
        newer_readings = get_newer_readings(query_parameters)

        # calcula a media
        average_measurement = calculate_average(newer_readings)

        # gera o novo item
        new_item = generate_new_item(query_parameters, average_measurement)

        # salva na tabela de medias
        persist_average_reading_item(new_item)

        return {
            'statusCode': 201,
            'body': json.dumps(new_item)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {e}')
        }
