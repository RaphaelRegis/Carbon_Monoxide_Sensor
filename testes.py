import json

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
    ...



def lambda_handler(event, context):
    date, hour = convert_date(event['requestContext']['requestTime'])


    return f"{date} | {hour}"


if __name__ == "__main__":
    with open("AWS_Lambda\\save_data\\save_data_readings\\event.json") as f:
        event = json.load(f)    
    
    print(lambda_handler(event, None))