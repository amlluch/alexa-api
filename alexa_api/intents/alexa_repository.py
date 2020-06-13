from typing import Dict, Any
from kink import inject
from typing_extensions import Protocol, runtime_checkable
from boto3.dynamodb import conditions
from alexa_api.errors import AlexaRepositoryError
from alexa_api.intents.alexa_data import Dialog


@runtime_checkable
class IAlexaRepository(Protocol):
    def get_dialog(self, intent_name: str) -> Dialog:
        ...


@inject(alias=IAlexaRepository)
class AlexaRepository(IAlexaRepository):
    def __init__(self, dialogs_table: Any):
        self.table = dialogs_table

    def get_dialog(self, intent_name: str) -> Dialog:
        condition = conditions.Key("intent_id").eq(str(intent_name))
        result = self.table.query(
            IndexName="by_intent_id", KeyConditionExpression=condition
        )

        if result["ResponseMetadata"]["HTTPStatusCode"] not in range(200, 300):
            raise AlexaRepositoryError("error occurred when retrieving dialog details")

        return self._hydrate_record(result["Items"][0])

    def _hydrate_record(self, item: Dict) -> Dialog:
        return Dialog(
            id=item["id"],
            intent_id=item["intent_id"],
            speak=item["speak"],
            ask=item.get("ask"),
        )
