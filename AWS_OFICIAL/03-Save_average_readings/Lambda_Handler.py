import json
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo


# load environment variables
load_dotenv()
TABLE_NAME = os.getenv("TABLE_NAME")


def get_date_hour(timezone: str):
    # get datetime without considering timezone
    naive_datetime = datetime.now()
    # convert date to sensor timezone
    zi = ZoneInfo(timezone)
    aware_datetime = naive_datetime.astimezone(zi)

    # prepare date and hour - date formatting: Year-month-day | hour formatting: Hour 00-23
    date = aware_datetime.strftime("%Y-%m-%d")
    hour = aware_datetime.strftime("%H")
    # ele pega a hora atual e volta 1 para poder pegar as leituras
    hour = str(int(hour) - 1)

    return {"date": date, "hour": hour}


def get_event_data(event: dict) -> dict:
    date_hour = get_date_hour(event["detail"]["timezone"])

    return {
        "region": event["detail"]["region"],
        "date": date_hour["date"],
        "hour": date_hour["hour"]
    }


# TO DO: adicionar codigo para fazer a query no dynamodb
def get_last_readings(region: str, date: str, hour: str) -> list:

    response_mock = {
        "Items": [
            {
                "id_reading": {"S": "123"},
                "id_sensor": {"S": "vdc_01"},
                "region": {"S": "Vitoria_da_Conquista-BA"},
                "measurement": {"S": "10"},
                "date": {"S": "2025-05-01"},
                "hour": {"S": "16"}
            },
            {
                "id_reading": {"S": "124"},
                "id_sensor": {"S": "vdc_02"},
                "region": {"S": "Vitoria_da_Conquista-BA"},
                "measurement": {"S": "20"},
                "date": {"S": "2025-05-01"},
                "hour": {"S": "16"}
            },
            {
                "id_reading": {"S": "125"},
                "id_sensor": {"S": "vdc_03"},
                "region": {"S": "Vitoria_da_Conquista-BA"},
                "measurement": {"S": "30"},
                "date": {"S": "2025-05-01"},
                "hour": {"S": "16"}
            }
        ],
        "Count": 3,
        "ScannedCount": 3
    }

    return response_mock["Items"]


def get_average_reading(readings: list) -> str:
    average_measurement = 0.0
    
    # it goes through all the readings and adds them up
    for reading in readings:
        average_measurement += float(reading["measurement"]["S"])

    # divides the measurement by the number of readings
    average_measurement = float(average_measurement/len(readings)).__ceil__()
    
    return str(int(average_measurement))


def generate_new_item(event_data: dict, average_measurement: str) -> dict:
    import uuid

    return {
        "id_average": {"S": str(uuid.uuid4())},
        "region": {"S": event_data["region"]},
        "date": {"S": event_data["date"]},
        "hour": {"S": event_data["hour"]},
        "average_measurement": {"S": average_measurement}
    }


    ...


# TO DO: mudar para o uso do resources ao invés do client
def persist_new_item(new_item: dict):
    # import boto3

    # dynamodb = boto3.client("dynamodb")

    # response = dynamodb.put_item(
    #     Table_name=TABLE_NAME,
    #     Item=new_item
    # )

    # return response
    ...


def lambda_handler(event, context):
    try:
        # gets region, date and hour from the event obj
        event_data = get_event_data(event)

        # query readings with region, date and hour
        readings = get_last_readings(
            event_data["region"], event_data["date"], event_data["hour"])

        # calculates average measurement
        average_measurement = get_average_reading(readings)

        # prepara o item para ser salvo
        new_item = generate_new_item(event_data, average_measurement)

        # salva o novo item
        response = persist_new_item(new_item)

        return {"statusCode": 201, "message": f"Item salvo com sucesso: {response}"}

    except Exception as e:
        return {"statusCode": 500, "message": json.dumps(f"ERROR: {e}")}


# testes locais
if __name__ == "__main__":
    with open("AWS_OFICIAL\\03-Save_average_readings\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
