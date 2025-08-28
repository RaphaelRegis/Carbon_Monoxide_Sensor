import json
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# load environment variables
load_dotenv()
TABLE_NAME = os.getenv("TABLE_NAME")


def get_event_body(event: dict):
    return json.loads(event["body"])


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


def generate_new_item(event_body: dict, date_hour: dict) -> dict:
    return {
        "id_sensor": {"S": event_body["id_sensor"]},
        "region": {"S": event_body["region"]},
        "measurement": {"S": str(float(event_body["measurement"]).__ceil__())}, # the measurement is rounded up and then converted to a string
        "date": {"S": date_hour["date"]},
        "hour": {"S": date_hour["hour"]}
    }

# TO DO: implementar codigo para chaves primarias
def persist_new_item(new_item: dict):
    # import boto3

    # dynamodb = boto3.client("dynamodb")

    # response = dynamodb.put_item(
    #     Table_name=TABLE_NAME,
    #     Item=new_item)
    
    # return response
    ...


def lambda_handler(event, context):
    try:

        # collect event data from request body
        event_body: dict = get_event_body(event)

        # prepare date and hour
        date_hour: dict = get_date_hour(event_body["timezone"])

        # generates new item to the database
        new_item = generate_new_item(event_body, date_hour)

        # save new item in DynamoDB
        #response = persist_new_item(new_item)
        response = ""

        return {"statusCode": 201, "message": f"Item salvo com sucesso: {response}"}

    except Exception as e:
        return {"statusCode": 500, "message": json.dumps(f"ERROR: {e}")}


# testes locais
if __name__ == "__main__":
    with open("AWS_OFICIAL\\02-Save_newer_readings\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
