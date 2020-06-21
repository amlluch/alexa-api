from dataclasses import dataclass, field
from bson import ObjectId
from typing import Optional, Iterator, Tuple, Any, Generator, List
from datetime import datetime


@dataclass
class Dialog:

    id: ObjectId
    intent_id: str
    speak: str
    ask: Optional[str]
    iot_err: int
    device_id: ObjectId


@dataclass
class Device:

    name: str
    description: Optional[str]
    position: int
    GPIO: int
    device_fence: Optional[List[ObjectId]]
    status: Optional[bool] = False
    device_id: ObjectId = field(default_factory=ObjectId)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    weather_fence: Optional[int] = 0
    timer_fence: Optional[int] = 0

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        for key, value in self.__dict__.items():
            if key == "device_id":
                value = str(self.device_id)
            if key == "updated_at":
                value = int(datetime.utcnow().timestamp())
            if key == "device_fence" and self.device_fence:
                value = [str(element) for element in value]
            yield key, value

    def serialize(self) -> Generator[Tuple[str, Any], None, None]:
        device_properties = {
            key: value for key, value in self.__dict__.items() if value is not None
        }
        for key, value in device_properties.items():
            if key == "device_id":
                value = str(self.device_id)
            if key == "updated_at":
                value = int(datetime.utcnow().timestamp())
            if key == "device_fence":
                value = [str(element) for element in value]
            yield key, value
