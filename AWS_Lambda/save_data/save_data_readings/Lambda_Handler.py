import json
from dotenv import load_dotenv
import os
##import boto3

# load environment variables
load_dotenv()
VALIDY_TOKEN = os.getenv("VALIDY_TOKEN")
TABLE_NAME = os.getenv("TABLE_NAME")

# load boto3 dynamodb table
##dynamodb = boto3.resource("dynamodb")
##table = dynamodb.Table(TABLE_NAME)

def convert_date(requestTime: str):
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

def collect_request_body(event):
    body = json.loads(event['body'])
    date, hour = convert_date(event['requestContext']['requestTime'])

    return body['token'], body['measurement'], date, hour, body['region'], body['city']

def verify_token(token):
    return token == VALIDY_TOKEN

def save_data(measurement, date, hour, region, city):
    item = {
        'measurement': measurement,
        'date': date,
        'hour': hour,
        'region': region,
        'city': city
    }

    ##table.put_item(item)
    return item

def lambda_handler(event, context):
    # get request data
    token, measurement, date, hour, region, city = collect_request_body(event)

    # verify request credential
    validity = verify_token(token)

    if validity == False:
        return {
            "statusCode": 401,
            "message": "Invalid token"
        }
    
    # save in DynamoDB
    item = save_data(measurement, date, hour, region, city)
    
    return {
        'statusCode': 201,
        'message': json.dumps(item)
    }

# para realizar testes localmente
if __name__ == "__main__":
    with open("AWS_Lambda\\save_data\\save_data_readings\\event.json") as f:
        event = json.load(f)    
    
    print(lambda_handler(event, None))