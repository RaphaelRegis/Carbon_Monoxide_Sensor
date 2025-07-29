import json
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()
VALIDY_TOKEN = os.getenv("VALIDY_TOKEN")
TABLE_NAME = os.getenv("TABLE_NAME")

# load boto3 dynamodb table
#dynamodb = boto3.resource("dynamodb")
#table = dynamodb.Table(TABLE_NAME)

def collect_request_body(event):
    body = json.loads(event['body'])
    return body['token'], body['measurement'], body['dateTime'], body['region'], body['city']

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

    return item

    #table.put_item(item)

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
    with open("AWS_Lambda\\save_data\\event.json") as f:
        event = json.load(f)    
    
    print(lambda_handler(event, None))