from typing_extensions import Protocol, runtime_checkable
from typing import Any, Dict
from kink import inject
import json
from os import environ
import time
import boto3


@runtime_checkable
class IIotService(Protocol):
    def send(self):
        ...

    def activate_device(self, event: Dict) -> None:
        ...

    def dispatch_sns(self, event: Dict) -> None:
        ...


@inject(alias=IIotService)
class IotService(IIotService):
    def __init__(self, iot: Any):
        self.iot = iot

    def activate_device(self, event: Dict) -> None:

        payload = {
            "state": event["state"],
            "action": "changed",
            "device_id": event["device_id"],
            "device_name": event["device_name"]
            }

        time.sleep(3)

        self.iot.shadowUpdate(json.dumps(payload), None, 5)

    def dispatch_sns(self, event: Dict) -> None:
        client = boto3.client('sns')
        arn = environ.get('SNS_ARN')
        message_attributes = {
            'action': {
                'DataType': 'String',
                'StringValue': event['action']
            },
            'status': {
                'DataType': 'String',
                'StringValue': str(event['state'])
            },
            'device_id': {
                'DataType': 'String',
                'StringValue': event['device_id']
            }
        }

        client.publish(
            TopicArn=arn,
            Message=json.dumps({"default": json.dumps(event)}),
            MessageStructure='json',
            MessageAttributes=message_attributes
        )
