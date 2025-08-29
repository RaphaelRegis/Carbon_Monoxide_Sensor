import json
from datetime import datetime
from zoneinfo import ZoneInfo

def get_date_hour(timezone: str):
    # get datetime without considering timezone
    naive_datetime = datetime.now()
    # convert date to sensor timezone
    zi = ZoneInfo(timezone)
    aware_datetime = naive_datetime.astimezone(zi)

    # prepare date and hour - date formatting: Year-month-day | hour formatting: Hour 00-23
    date = aware_datetime.strftime("%Y-%m-%d")
    hour = aware_datetime.strftime("%H")
    hour = str(int(hour) - 1) # ele pega a hora atual e volta 1 para poder pegar as leituras

    return {"date": date, "hour": hour}

def get_event_data(event: dict) -> dict:
    date_hour = get_date_hour()

    return {
        "region": event["detail"]["region"],
        "hour": ""
    }
    
    
    ...


def get_last_readings(region: str, hour: str) -> list : ...


def get_average_reading(readings: list): ...


def generate_new_item(): ...


def save_new_item(): ...


def lambda_handler(event, context):
    try:
        # pega data, hora e região
        event_data = get_event_data(event)

        # primeiro pega as leituras corretas
        readings = get_last_readings()

        # calcula a média


        # prepara o item para ser salvo

        # salva o novo item
        response = ""

        return {"statusCode": 201, "message": f"Item salvo com sucesso: {response}"}

    except Exception as e:
        return {"statusCode": 500, "message": json.dumps(f"ERROR: {e}")}


# testes locais
if __name__ == "__main__":
    with open("AWS_OFICIAL\\03-Save_average_readings\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
