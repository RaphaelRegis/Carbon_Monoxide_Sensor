import json


def get_event_data(event: dict): 
    return json.loads(event["body"])


def create_sqs_queue(region: str): ...


def create_save_averages_event(region: str, timezone: str): ...


def generate_new_item(event_data: dict, queue_url: str): ...


def save_new_item(new_item: dict): ...


def lambda_handler(event, context):
    try:
        # get region, bot_token and channel_id from request body
        event_data = get_event_data(event)
        print(event_data)

        # create sqs queue
        queue_url = create_sqs_queue(event_data["region"])

        # create event in eventbridge
        create_save_averages_event(event_data["region"], event_data["timezone"])

        # generate new item
        new_item = generate_new_item(event_data, queue_url)

        # save new item
        response = save_new_item(new_item)

        return {"statusCode": 201, "message": f"Item salvo com sucesso: {response}"}

    except Exception as e:
        return {"statusCode": 500, "message": json.dumps(f"ERROR: {e}")}


# testes locais
if __name__ == "__main__":
    with open("AWS_OFICIAL\\04-Save_new_region\\event.json") as f:
        event = json.load(f)

    print(lambda_handler(event, None))
