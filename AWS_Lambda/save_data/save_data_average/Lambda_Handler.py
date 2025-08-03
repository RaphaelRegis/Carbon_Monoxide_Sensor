import json
from dotenv import load_dotenv
import os
# from boto3.dynamodb.conditions import Key
# import boto3

# load environment variables
load_dotenv()
READINGS_TABLE = os.getenv("READINGS_TABLE")
AVERAGES_TABLE = os.getenv("AVERAGES_TABLE")

# load boto3 utils
##dynamodb = boto3.resources("dynamodb")
##readings_table = dynamodb.Table(READINGS_TABLE)
##averages_table = dynamodb.Table(AVERAGES_TABLE)


def get_query_parameters(event):
    dateTime = event['time']
    date = dateTime[0:10]
    hour = dateTime[11:13]
    city = event['detail']['city']

    return date, hour, city


def get_newer_reading_items(date, hour, city):
    ##response = readings_table.query(
    ##KeyConditionExpression=Key('date').eq(date) & Key('hour').eq(hour) & Key('city').eq(city)
    ##)
    response = {
        "Items": [
            {
                "measurement": {"S": "10"},
                "date": {"S": "2025-08-01"},
                "hour": {"S": "14"},
                "region": {"S": "southeast"},
                "city": {"S": "Sao Paulo - SP"}
            },
            {
                "measurement": {"S": "20"},
                "date": {"S": "2025-08-01"},
                "hour": {"S": "15"},
                "region": {"S": "southeast"},
                "city": {"S": "Sao Paulo - SP"}
            },
            {
                "measurement": {"S": "30"},
                "date": {"S": "2025-08-01"},
                "hour": {"S": "16"},
                "region": {"S": "southeast"},
                "city": {"S": "Sao Paulo - SP"}
            }
        ],
        "Count": 3,
        "ScannedCount": 3
    }

    return response["Items"]


def get_average_measurement(items: list):
    average_measurement = 0.0

    for item in items:
        average_measurement += float(item['measurement']['S'])

    average_measurement = average_measurement/len(items)

    return str(average_measurement)


def save_average(new_average, date, hour, city):
    item = {
        'average': new_average,
        'date': date,
        'hour': hour,
        'city': city
    }

    ##averages_table.put_item(item)

    return item


def lambda_handler(event, context):

    # primeiro pega as leituras guardadas da ultima hora
    date, hour, city = get_query_parameters(event)
    items = get_newer_reading_items(date, hour, city)

    # em seguida calcula a media
    new_average = get_average_measurement(items)

    # por fim salva na tabela de medias do DynamoDB
    new_item = save_average(new_average, date, hour, city)

    return {
        'statusCode': 201,
        'message': json.dumps(new_item)
    }


# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\save_data\\save_data_average\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
