from typing_extensions import Protocol, runtime_checkable
from typing import Dict, Any
import boto3
from os import environ
import json
from kink import inject
import time
from bson import ObjectId
from alexa_api.devices.repository import Device, DevicesRepository
from alexa_api.iot.iot import IotErr


@runtime_checkable
class IIotRepository(Protocol):

    def activate_device(self, event: Dict) -> None:
        ...

    def dispatch_sns(self, action: str, status: bool, device_id: ObjectId, event: Dict) -> None:
        ...

    def send_order(self, device_id: ObjectId, status: bool) -> None:
        ...

    def get_device_status(self, device_id: ObjectId) -> bool:
        ...

    def confirm_status(self, device: Device, desired_status: bool, timeout: int) -> Dict:
        ...


@inject(alias=IIotRepository)
class IotRepository(IIotRepository):
    def __init__(self, iot: Any, devices_repository: DevicesRepository):
        self.iot = iot
        self.devices_repository = devices_repository

    def activate_device(self, event: Dict) -> None:

        payload = {
            "state": {
                "reported": event["state"]["desired"]
            }
        }

        time.sleep(3)

        self.iot.connect()
        self.iot.publish("device/reported", json.dumps(payload), 0)

    def dispatch_sns(self, action: str, status: bool, device_id: ObjectId, event: Dict) -> None:

        client = boto3.client('sns')
        arn = environ.get('SNS_ARN')
        message_attributes = {
            'action': {
                'DataType': 'String',
                'StringValue': action
            },
            'status': {
                'DataType': 'String',
                'StringValue': str(status)
            },
            'device_id': {
                'DataType': 'String',
                'StringValue': str(device_id)
            }
        }
        client.publish(
            TopicArn=arn,
            Message=json.dumps({"default": json.dumps(event)}),
            MessageStructure='json',
            MessageAttributes=message_attributes
        )

    def send_order(self, device_id: ObjectId, status: bool) -> None:
        payload = {
            "state": {
                "desired": {
                    "is_on": status,
                    "device_id": str(device_id)
                }
            }
        }

        self.iot.connect()
        self.iot.publish("device/desired", json.dumps(payload), 0)

    def confirm_status(self, current_device: Device, desired_status: bool, timeout: int) -> Dict:
        max_time = time.time() + timeout
        while time.time() < max_time:
            time.sleep(2)
            device = self.devices_repository.get(current_device.device_id)
            if device.status == desired_status:
                return {"info": "Device status confirmed", "err": IotErr.CONFIRMED}

        return {"info": "Device status confirmation failed", "err": IotErr.FAILED}
