from dataclasses import dataclass
from bson import ObjectId
from typing import Optional


@dataclass
class Dialog:

    id: ObjectId
    intent_id: str
    speak: str
    ask: Optional[str]
