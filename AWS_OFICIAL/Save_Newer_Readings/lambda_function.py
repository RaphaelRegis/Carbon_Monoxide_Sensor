import json
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid
import boto3
import os

TABLE_NAME = os.environ['TABLE_NAME']


def get_event_body(event):
    return json.loads(event['body'])


def get_date_hour(timezone: str):
    # get datetime without considering timezone
    naive_datetime = datetime.now()
    # convert date to sensor timezone
    zi = ZoneInfo(timezone)
    aware_datetime = naive_datetime.astimezone(zi)

    # prepare date and hour - date formatting: Year-month-day | hour formatting: Hour 00-23
    date = aware_datetime.strftime("%Y-%m-%d")
    hour = aware_datetime.strftime("%H")

    return {"date": date, "hour": hour}


def generate_new_item(event_body, date_hour):
    return {
        "id_reading": {"S": str(uuid.uuid4())},
        "id_sensor": {"S": event_body["id_sensor"]},
        "reading_region": {"S": event_body["region"]},
        "reading_date_hour": {"S": f"{date_hour["date"]} {date_hour["hour"]}"},
        "measurement": {"S": str(float(event_body["measurement"]).__ceil__())}, # the measurement is rounded up and then converted to a string
    }


def persist_new_item(new_item):
    dynamodb = boto3.client('dynamodb')
    response = dynamodb.put_item(
        TableName=TABLE_NAME,
        Item=new_item
    )


def lambda_handler(event, context):

    try:
        # collect request body
        event_body = get_event_body(event)

        # prepares correct date and hour based on timezone
        date_hour = get_date_hour(event_body["timezone"])

        # creates the new object
        new_item = generate_new_item(event_body, date_hour)
        
        # save the new object into dynamodb
        persist_new_item(new_item)

        # request return
        return {
            'statusCode': 201,
            'body': json.dumps(new_item)
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error: {}'.format(e))
        }




