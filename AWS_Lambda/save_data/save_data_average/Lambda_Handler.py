import json
from dotenv import load_dotenv
import os
from boto3.dynamodb.conditions import Key
import boto3

# load environment variables
load_dotenv()
READINGS_TABLE = os.getenv("READINGS_TABLE")
AVERAGES_TABLE = os.getenv("AVERAGES_TABLE")

# load boto3 utils
dynamodb = boto3.resources("dynamodb")
readings_table = dynamodb.Table(READINGS_TABLE)
averages_table = dynamodb.Table(AVERAGES_TABLE)


# TO DO: implementar get_query_parameters
def get_query_parameters(event):
    
    ...

def get_newer_reading_items(date, hour):
    response = readings_table.query(
        KeyConditionExpression=Key('date').eq(date) & Key('hour').eq(hour)
    )

    return response["Items"]

def get_average_measurement(items: list):
    average_measurement = 0.0

    for i in range(items):
        average_measurement += items[i]['measurement']

    average_measurement = average_measurement/len(items)

    return average_measurement

def save_average(new_average, date, hour, city):
    item = {
        'average': str(new_average),
        'date': date,
        'hour': hour,
        'city': city
    }

    averages_table.put_item(item)

    return item

def lambda_handler(event, context):

    # primeiro pega as leituras guardadas da ultima hora
    date, hour = get_query_parameters(event)
    items = get_newer_reading_items(date, hour)

    # em seguida calcula a media
    new_average = get_average_measurement(items)

    # por fim salva na tabela de medias do DynamoDB
    new_item = save_average(new_average)

    return {
        'statusCode': 201,
        'message': json.dumps(new_item)
    }

# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\save_data\\save_data_average\\event.json") as f:
        event = json.load(f)    
    
    print(lambda_handler(event, None))