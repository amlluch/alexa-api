from typing import Dict, Any
from kink import inject
from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class IAlexaRepository(Protocol):

    def get_dialog(self,  intent_name: str) ->  Dict:
        ...


@inject(alias=IAlexaRepository)
class AlexaRepository(IAlexaRepository):

    def __init__(self, dialogs_table: Any):
        self.table = dialogs_table

    def get_dialog(self,  intent_name: str) -> Dict:
        return {}
