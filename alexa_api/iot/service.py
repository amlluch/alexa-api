from typing_extensions import Protocol, runtime_checkable
from typing import Dict, Optional
from kink import inject
from dataclasses import dataclass
from bson import ObjectId
from alexa_api.iot.repository import IotRepository
from alexa_api.devices.repository import DevicesRepository
from alexa_api.errors import RecordNotFound
from alexa_api.iot.iot import IotErr
import boto3
from alexa_api.iot import TIMER_FENCE_ARN, DESIRED_TOPIC, REPORTED_TOPIC, BASE_TOPIC
from alexa_api import S3_CERTIFICATES, IOT_ENDPOINT, IOT_PORT


@dataclass
class IotToSnsDispatcherEvent:
    device_id: ObjectId
    status: bool
    raw_event: Dict
    action: str

    def __init__(self, event: Dict):
        self.action = "reported" if "reported" in event["state"] else "desired"
        self.device_id = ObjectId(event["state"][self.action]["device_id"])
        self.status = bool(event["state"][self.action]["is_on"])
        self.raw_event = event


@dataclass
class SendOrderRequest:
    device_id: ObjectId
    status: bool
    timeout: Optional[int]

    def __init__(self, device_id: str, status: str, timeout: str):
        self.device_id = ObjectId(device_id)
        self.status = bool(status)
        self.timeout = int(timeout) if timeout else None


@runtime_checkable
class IIotService(Protocol):
    def send(self):
        ...

    def activate_device(self, event: Dict) -> None:
        ...

    def dispatch_sns(self, request: IotToSnsDispatcherEvent) -> None:
        ...

    def send_order(self, request: SendOrderRequest) -> Dict:
        ...

    def timer_fence(self, event: Dict) -> None:
        ...

    def stop_device(self, device_id: str, name: str) -> None:
        ...

    def get_config(self) -> Dict:
        ...


@inject(alias=IIotService)
class IotService(IIotService):
    def __init__(
        self, iot_repository: IotRepository, devices_repository: DevicesRepository
    ):
        self.iot_repository = iot_repository
        self.devices_repository = devices_repository

    def activate_device(self, event: Dict) -> None:

        device = self.devices_repository.get(
            ObjectId(event["state"]["desired"]["device_id"])
        )
        if not device:
            raise RecordNotFound("That device doesn't exist")

        self.iot_repository.activate_device(event)

    def dispatch_sns(self, event: IotToSnsDispatcherEvent) -> None:

        device = self.devices_repository.get(event.device_id)
        self.iot_repository.dispatch_sns(
            event.action, event.status, event.device_id, event.raw_event
        )

        if event.action == "reported":
            device.status = event.status
            self.devices_repository.update(device)

    def send_order(self, request: SendOrderRequest) -> Dict:
        device = self.devices_repository.get(request.device_id)
        if not device:
            raise RecordNotFound(f"Device {str(request.device_id)} doesn't exist")

        err_response: Dict = {
            "info": "Device status not confirmed",
            "err": IotErr.UNCONFIRMED,
        }
        if device.status == request.status:
            return {
                "info": f"Device status already {request.status}",
                "err": IotErr.EXISTING,
            }

        if request.status:
            for device_fence in self.devices_repository.get_device_fence_list(
                device.device_fence
            ):
                if device_fence.status:
                    return {
                        "info": f"Incompatible device {device_fence.device_id} is on",
                        "err": IotErr.DEVICE_FENCED,
                    }

            if device.weather_fence and device.weather_fence != 0:
                if self.iot_repository.weather_fence(device.weather_fence):
                    return {
                        "info": f"Device {device.device_id} stopped by weather fence",
                        "err": IotErr.WEATHER_FENCED,
                    }

        self.iot_repository.send_order(request.device_id, request.status)

        if request.timeout:
            err_response = self.iot_repository.confirm_status(
                device, request.status, request.timeout
            )

        return err_response

    def timer_fence(self, event: Dict) -> None:
        device_id = event["state"]["reported"]["device_id"]
        device = self.devices_repository.get(ObjectId(device_id))
        if not device.timer_fence or device.timer_fence == 0:
            return
        self.iot_repository.start_timer_fence(event, device_id, device.timer_fence)

    def stop_device(self, device_id: str, name: str) -> None:
        state_machine = boto3.client("stepfunctions")
        response = state_machine.list_executions(stateMachineArn=TIMER_FENCE_ARN, statusFilter='RUNNING')
        for machine in response["executions"]:
            if f"{device_id}-timer_fence" in machine["name"] and machine["name"] != name:
                return
        self.iot_repository.send_order(ObjectId(device_id), False)

    def get_config(self) -> Dict:
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(S3_CERTIFICATES)
        certificates = {obj.key: obj.get()['Body'].read().decode('utf-8') for obj in bucket.objects.all()}
        iot_server = {"endpoint": IOT_ENDPOINT, "port": IOT_PORT}
        topics = {"desired": DESIRED_TOPIC, "reported": REPORTED_TOPIC, "base": BASE_TOPIC}
        return {**certificates, **iot_server, **topics}
