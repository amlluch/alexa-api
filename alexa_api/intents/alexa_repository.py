from typing import Dict, Any
from kink import inject
from typing_extensions import Protocol, runtime_checkable
from boto3.dynamodb import conditions
from alexa_api.errors import AlexaRepositoryError
from alexa_api.intents.alexa_data import Dialog
from bson import ObjectId
from alexa_api.iot.service import SendOrderRequest, IIotService


@runtime_checkable
class IAlexaRepository(Protocol):
    def get_dialog(self, intent_name: str, iot_err: int, locale: str = "es-ES") -> Dialog:
        ...

    def get_device_id(self, intent_name: str) -> ObjectId:
        ...

    def send_order(self, device_id: ObjectId, status: bool, timeout: int) -> int:
        ...


@inject(alias=IAlexaRepository)
class AlexaRepository(IAlexaRepository):
    def __init__(self, dialogs_table: Any, iot_service: IIotService):
        self.table = dialogs_table
        self.iot_service = iot_service

    def get_dialog(self, intent_name: str, iot_err: int = 0, locale: str = "es-ES") -> Dialog:
        condition = conditions.Key("intent_id").eq(intent_name) & conditions.Key("iot_err").eq(iot_err)
        result = self.table.query(
            IndexName="by_intent_id_and_iot_err", KeyConditionExpression=condition
        )

        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise AlexaRepositoryError("error occurred when retrieving dialog details")

        if len(result["Items"]) > 1:
            for item in result["Items"]:
                if item["locale"] == locale:
                    return self._hydrate_record(item)

        return self._hydrate_record(result["Items"][0])

    def get_device_id(self, intent_name: str) -> ObjectId:
        condition = conditions.Key("intent_id").eq(str(intent_name))
        result = self.table.query(
            IndexName="by_intent_id", KeyConditionExpression=condition
        )
        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise AlexaRepositoryError("error occurred when retrieving device_id")
        return ObjectId(result["Items"][0]["device_id"])

    def send_order(self, device_id: ObjectId, status: bool, timeout: int) -> int:
        request = SendOrderRequest(str(device_id), str(status), str(timeout))
        result = self.iot_service.send_order(request)
        return result["err"]

    @staticmethod
    def _hydrate_record(item: Dict) -> Dialog:
        return Dialog(
            id=item["id"],
            intent_id=item["intent_id"],
            speak=item["speak"],
            ask=item.get("ask"),
            iot_err=int(item["iot_err"]),
            device_id=ObjectId(item["device_id"]),
            locale=item.get("locale"),
            description=item.get("description")
        )
