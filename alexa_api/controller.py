
from alexa_api.types import LambdaContext, LambdaEvent, LambdaResponse
from ask_sdk_core.skill_builder import SkillBuilder
from typing import Dict, Any
from kink import inject

from alexa_api.intents.alexa_service import LaunchRequestHandler, HelpIntentHandler, CancelOrStopIntentHandler, SessionEndedRequestHandler, IntentReflectorHandler, CatchAllExceptionHandler, EnciendePiscinaIntent, ApagaPiscinaIntent
from alexa_api.intents.alexa_repository import AlexaRepository, IAlexaRepository


def hello_world(event: LambdaEvent, context: LambdaContext) -> LambdaResponse:
    return {"statusCode": 200, "body": "Todo bien"}


@inject
def skill_handler(event: LambdaEvent, context: LambdaContext, alexa_repository: AlexaRepository) -> Dict[str, Any]:

    sb = SkillBuilder()

    sb.add_request_handler(LaunchRequestHandler())
    sb.add_request_handler(EnciendePiscinaIntent(alexa_repository))
    sb.add_request_handler(ApagaPiscinaIntent(alexa_repository))
    sb.add_request_handler(HelpIntentHandler())
    sb.add_request_handler(CancelOrStopIntentHandler())
    sb.add_request_handler(SessionEndedRequestHandler())
    sb.add_request_handler(IntentReflectorHandler())

    sb.add_exception_handler(CatchAllExceptionHandler())

    lambda_handler = sb.lambda_handler()
    return lambda_handler(event, context)

