from typing_extensions import runtime_checkable, Protocol
from typing import Any, Dict, Iterable, Optional, List, Generator
from alexa_api.intents.alexa_data import Device
from kink import inject
from botocore.exceptions import ClientError
from alexa_api.errors import AWSError
from bson import ObjectId
from boto3.dynamodb import conditions
from alexa_api.errors import RepositoryError, RecordNotFound


@runtime_checkable
class IDevicesRepository(Protocol):
    def insert(self, device: Device) -> None:
        ...

    def get(self, device_id: ObjectId) -> Device:
        ...

    def update(self, device: Device) -> None:
        ...

    def delete(self, device_id: ObjectId) -> None:
        ...

    def position_exists(self, position: int) -> Optional[ObjectId]:
        ...

    def gpio_exists(self, gpio: int) -> Optional[ObjectId]:
        ...

    def get_list(self) -> Iterable[Device]:
        ...

    def get_device_fence_list(self, devices: Optional[List[ObjectId]]) -> Iterable[Device]:
        ...


@inject(alias=IDevicesRepository)
class DevicesRepository(IDevicesRepository):
    def __init__(self, devices_table: Any):
        self.table = devices_table

    def insert(self, device: Device) -> None:
        try:
            self.table.put_item(Item=dict(device.serialize()))
        except ClientError as e:
            raise AWSError(
                f"AWS error {e.response['Error']['Code']} inserting {str(device.device_id)}"
            ) from e

    def get(self, device_id: ObjectId) -> Device:
        condition = conditions.Key("device_id").eq(str(device_id))
        result = self.table.query(KeyConditionExpression=condition)

        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise RepositoryError("error occurred when retrieving device details")

        if not result["Count"]:
            raise RecordNotFound(f"Device with id {device_id} was not found")

        return self._hydrate_device(result["Items"][0])

    def update(self, device: Device) -> None:

        device_id = device.device_id
        record = dict(device.serialize())
        record.pop("device_id")
        update_set_expr = "set " + ", ".join(f"#{k} = :{k}" for k, v in record.items())
        attr_set_names = {f"#{k}": k for k, v in record.items()}
        attr_values = {f":{k}": v for k, v in record.items()}

        try:
            self.table.update_item(
                Key={"device_id": str(device_id)},
                UpdateExpression=update_set_expr,
                ExpressionAttributeValues=attr_values,
                ExpressionAttributeNames=attr_set_names,
                ReturnValues="ALL_NEW",
            )
        except ClientError as e:
            raise AWSError(
                f"AWS error {e.response['Error']['Code']} updating record {str(device_id)}"
            ) from e

    def delete(self, device_id: ObjectId) -> None:
        try:
            self.table.delete_item(Key={"device_id": str(device_id)})
        except ClientError as e:
            raise AWSError(
                f"AWS error {e.response['Error']['Code']} updating record {str(device_id)}"
            ) from e

    def position_exists(self, position: int) -> Optional[ObjectId]:
        condition = conditions.Key("position").eq(position)
        result = self.table.query(
            IndexName="by_position", KeyConditionExpression=condition
        )

        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise RepositoryError("error occurred when retrieving device details")

        if result["Items"]:
            return ObjectId(result["Items"][0]["device_id"])
        return None

    def gpio_exists(self, gpio: int) -> Optional[ObjectId]:
        condition = conditions.Key("GPIO").eq(gpio)
        result = self.table.query(IndexName="by_GPIO", KeyConditionExpression=condition)

        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise RepositoryError("error occurred when retrieving device details")

        if result["Items"]:
            return ObjectId(result["Items"][0]["device_id"])
        return None

    def get_list(self) -> Iterable[Device]:
        result = self.table.scan()
        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise RepositoryError("error occurred when retrieving device details")

        if not result["Count"]:
            raise RecordNotFound(f"No devices yet")
        for item in result["Items"]:
            yield self._hydrate_device(item)

    def get_device_fence_list(self, devices: Optional[List[ObjectId]]) -> Iterable[Device]:
        if not devices:
            return
        for device in devices:
            yield self.get(device)

    def _hydrate_device(self, item: Dict) -> Device:
        return Device(
            device_id=ObjectId(item["device_id"]),
            name=item["name"],
            description=item.get("description"),
            position=int(item["position"]),
            GPIO=int(item["GPIO"]),
            status=item.get("status"),
            weather_fence=int(item.get("weather_fence")) if "weather_fence" in item else 0,
            timer_fence=int(item.get("timer_fence")) if "timer_fence" in item else 0,
            device_fence=self._hydrate_device_fence(item.get("device_fence"))
        )

    @staticmethod
    def _hydrate_device_fence(item: Optional[List[str]]) -> Optional[List[ObjectId]]:
        if not item:
            return None
        return [ObjectId(element) for element in item]
