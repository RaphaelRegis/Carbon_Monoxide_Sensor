import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
from boto3.dynamodb.conditions import Key
import boto3
import uuid

# environment variables
NEWER_READINGS_TABLE = os.environ["NEWER_READINGS_TABLE"]
AVERAGE_READINGS_TABLE = os.environ["AVERAGE_READINGS_TABLE"]

# prepares dynamodb
dynamodb = boto3.client("dynamodb")


def get_query_parameters(event):
    reading_region = event["detail"]["reading_region"]
    reading_date_hour = get_date_hour(event["detail"]["timezone"])

    return {
        "reading_region": reading_region, 
        "reading_date_hour": reading_date_hour
    }


def get_date_hour(timezone: str):
    # get the correct time according to the time zone
    zi = ZoneInfo(timezone)
    aware_datetime = datetime.now(zi)

    # subtract one hour, since the readings were taken over the previous hour
    aware_datetime = aware_datetime - timedelta(hours=1)

    # format the date and time — date formatting: Year-month-day | hour formatting: Hour 00-23
    reading_date = aware_datetime.strftime("%Y-%m-%d")
    reading_hour = aware_datetime.strftime("%H")

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
    
    # if there is no reading, it returns an error
    if newer_readings == []:
        raise Exception("No readings found")

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
        # first, retrieve the data needed for the query (region, date, and time)
        query_parameters = get_query_parameters(event)

        # query the corresponding readings
        newer_readings = get_newer_readings(query_parameters)

        # calculate the average
        average_measurement = calculate_average(newer_readings)

        # generate the new item
        new_item = generate_new_item(query_parameters, average_measurement)

        # save in the averages table
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
