# import uuid
import json
from datetime import datetime

# print(str(uuid.uuid4()))

# date_hour = "2025-09-25 15"

# print(f"Data: {date_hour[:10]}")
# print(f"Hora: {date_hour[11:]}")

mensagens = {
    "Messages": [
        {
            "MessageId": "string",
            "ReceiptHandle": "MensagemDoBrian",
            "MD5OfBody": "string",
            "Body": '{"nome": "Brian", "data_hora": "2025-10-02 19"}',
            "Attributes": {"string": "string"},
            "MD5OfMessageAttributes": "string",
            "MessageAttributes": {
                "string": {
                    "StringValue": "string",
                    "BinaryValue": b"bytes",
                    "StringListValues": [
                        "string",
                    ],
                    "BinaryListValues": [
                        b"bytes",
                    ],
                    "DataType": "string",
                }
            },
        },
        {
            "MessageId": "string",
            "ReceiptHandle": "MensagemDoPedro",
            "MD5OfBody": "string",
            "Body": '{"nome": "Pedro", "data_hora": "2025-10-02 18"}',
            "Attributes": {"string": "string"},
            "MD5OfMessageAttributes": "string",
            "MessageAttributes": {
                "string": {
                    "StringValue": "string",
                    "BinaryValue": b"bytes",
                    "StringListValues": [
                        "string",
                    ],
                    "BinaryListValues": [
                        b"bytes",
                    ],
                    "DataType": "string",
                }
            },
        },
        {
            "MessageId": "string",
            "ReceiptHandle": "MensagemDoAntonio",
            "MD5OfBody": "string",
            "Body": '{"nome": "Antonio", "data_hora": "2025-09-02 20"}',
            "Attributes": {"string": "string"},
            "MD5OfMessageAttributes": "string",
            "MessageAttributes": {
                "string": {
                    "StringValue": "string",
                    "BinaryValue": b"bytes",
                    "StringListValues": [
                        "string",
                    ],
                    "BinaryListValues": [
                        b"bytes",
                    ],
                    "DataType": "string",
                }
            },
        },
    ]
}


messages = mensagens["Messages"]
bodies = []

for msg in messages:
    body_dict = json.loads(msg["Body"])
    body_dict["ReceiptHandle"] = msg["ReceiptHandle"]
    bodies.append(body_dict)


# Ordenar pela chave "data_hora"
bodies.sort(key=lambda x: datetime.strptime(x["data_hora"], "%Y-%m-%d %H"))

print(bodies)
