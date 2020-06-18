from typing_extensions import Protocol, runtime_checkable
from typing import Dict, Optional
from kink import inject
from dataclasses import dataclass
from bson import ObjectId
from alexa_api.iot.repository import IotRepository
from alexa_api.devices.repository import DevicesRepository
from alexa_api.errors import RecordNotFound
from alexa_api.iot.iot import IotErr


@dataclass
class IotToSnsDispatcherRequest:
    device_id: ObjectId
    status: bool
    event: Dict
    action: str

    def __init__(self, event):
        self.action = "reported" if "reported" in event["state"] else "desired"
        self.device_id = ObjectId(event["state"][self.action]["device_id"])
        self.status = bool(event["state"][self.action]["is_on"])
        self.event = event


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

    def dispatch_sns(self, request: IotToSnsDispatcherRequest) -> None:
        ...

    def send_order(self, request: SendOrderRequest) -> Dict:
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

    def dispatch_sns(self, request: IotToSnsDispatcherRequest) -> None:

        device = self.devices_repository.get(request.device_id)
        self.iot_repository.dispatch_sns(
            request.action, request.status, request.device_id, request.event
        )

        if request.action == "reported":
            device.status = request.status
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
                        "err": IotErr.FENCED,
                    }

        self.iot_repository.send_order(request.device_id, request.status)

        if request.timeout:
            err_response = self.iot_repository.confirm_status(
                device, request.status, request.timeout
            )

        return err_response
