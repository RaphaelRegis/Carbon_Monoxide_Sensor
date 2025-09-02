import json

def lambda_handler(event, context):
    try:
        # get region, bot_token and channel_id from request body

        # create sqs queue

        # create event in eventbridge

        # generate new item

        # save new item

        return {"statusCode": 201, "message": f"Item salvo com sucesso"}

    except Exception as e:
        return {"statusCode": 500, "message": json.dumps(f"ERROR: {e}")}


# testes locais
if __name__ == "__main__":
    with open("AWS_OFICIAL\\04-Save_average_region\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
