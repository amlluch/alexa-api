from dataclasses import dataclass
from typing import Optional, Iterator, Tuple, Any, Dict
from bson import ObjectId
from typing_extensions import runtime_checkable, Protocol
from alexa_api.intents.alexa_data import Device
from kink import inject
from alexa_api.devices.repository import IDevicesRepository
from alexa_api.errors import RecordExists, RecordNotFound


@dataclass
class CreateDeviceRequest:
    device_id: ObjectId
    name: str
    description: Optional[str]
    position: int
    GPIO: int
    status: Optional[bool] = False

    def __init__(self, name: str, description: str, position: int, gpio: int) -> None:
        self.device_id = ObjectId()
        self.name = name
        self.description = description
        self.position = position
        self.GPIO = gpio

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        for key, value in self.__dict__.items():
            yield key, value


@dataclass
class GetDeviceRequest:
    device_id: ObjectId

    def __init__(self, object_id: str) -> None:
        self.device_id = ObjectId(object_id)


@dataclass
class UpdateDeviceRequest:
    device_id: ObjectId
    name: Optional[str]
    description: Optional[str]
    position: Optional[int]
    GPIO:Optional[int]

    def __init__(self, device_id: str, name: str, description: str, position: str, gpio: str):
        self.device_id = ObjectId(device_id)
        self.name = name
        self.description = description
        self.position = int(position) if position is not None else None
        self.GPIO = int(gpio) if gpio is not None else None

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        for key, value in self.__dict__.items():
            yield key, value


@dataclass
class DeleteDeviceRequest:
    device_id: ObjectId

    def __init__(self, device_id: str) -> None:
        self.device_id = ObjectId(device_id)


@runtime_checkable
class IDevicesService(Protocol):

    def create(self, request: CreateDeviceRequest) -> Device:
        ...

    def get(self, request: GetDeviceRequest) -> Device:
        ...

    def get_list(self) -> Dict:
        ...

    def update(self, request: UpdateDeviceRequest) -> Device:
        ...

    def delete(self,  request: DeleteDeviceRequest) -> None:
        ...


@inject(alias=IDevicesService)
class DevicesService(IDevicesService):
    def __init__(self, devices_repository: IDevicesRepository) -> None:
        self.devices_repository = devices_repository

    def create(self, request: CreateDeviceRequest) -> Device:
        device = Device(**dict(request))

        existing_position = self.devices_repository.position_exists(request.position)
        if existing_position:
            raise RecordExists(f"this position is already used by device {existing_position}")
        existing_gpio = self.devices_repository.position_exists(request.GPIO)
        if existing_gpio:
            raise RecordExists(f"this GPIO is already used by device {existing_position}")

        self.devices_repository.insert(device)
        return device

    def get(self, request: GetDeviceRequest) -> Device:
        return self.devices_repository.get(request.device_id)

    def get_list(self) -> Dict:
        return {"devices": [dict(device) for device in self.devices_repository.get_list()]}

    def update(self, request: UpdateDeviceRequest) -> Device:
        if request.position:
            existing_position_device = self.devices_repository.position_exists(request.position)
            if existing_position_device and existing_position_device != request.device_id:
                raise RecordExists(f"this position is already used by device {existing_position_device}")
        if request.GPIO:
            existing_gpio_device = self.devices_repository.gpio_exists(request.GPIO)
            if existing_gpio_device and existing_gpio_device != request.device_id:
                raise RecordExists(f"this GPIO is already used by device {existing_gpio_device}")

        actual_device = self.devices_repository.get(request.device_id)
        if not actual_device:
            raise RecordNotFound(f"Device with id {request.device_id} was not found")

        new_device = self._make_device_entity(actual_device, **dict(request))
        self.devices_repository.update(new_device)
        return new_device

    def delete(self,  request: DeleteDeviceRequest) -> None:
        self.devices_repository.delete(request.device_id)

    @staticmethod
    def _make_device_entity(actual_device: Device, **kwargs) -> Device:
        new_device = {
            key: kwargs[key] if key in kwargs and kwargs[key] is not None else value
            for key, value in dict(actual_device).items()
        }
        return Device(**new_device)
