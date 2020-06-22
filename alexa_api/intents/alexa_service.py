import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.utils.request_util import get_locale

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from alexa_api.intents.alexa_repository import AlexaRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Handler for Skill Launch."""

    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        dialog = self.alexa_repository.get_dialog("LaunchRequest")

        return (
            handler_input.response_builder.speak(dialog.speak).ask(dialog.ask).response
        )


class EnciendePiscinaIntent(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Handler for turning on pool lights"""

    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_intent_name("EnciendePiscinaIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        locale = get_locale(handler_input)
        device_id = self.alexa_repository.get_device_id("EnciendePiscinaIntent")
        iot_err = self.alexa_repository.send_order(device_id, True, 25)
        dialog = self.alexa_repository.get_dialog(
            ask_utils.get_intent_name(handler_input),
            iot_err,
            locale
        )

        return (
            handler_input.response_builder.speak(dialog.speak).ask(dialog.ask).response
            if dialog.ask
            else handler_input.response_builder.speak(dialog.speak).response
        )


class ApagaPiscinaIntent(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Handler for switching off pool lights"""

    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_intent_name("ApagaPiscinaIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        dialog = self.alexa_repository.get_dialog(
            ask_utils.get_intent_name(handler_input)
        )

        return (
            handler_input.response_builder.speak(dialog.speak).ask(dialog.ask).response
            if dialog.ask
            else handler_input.response_builder.speak(dialog.speak).response
        )


class HelpIntentHandler(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Handler for Help Intent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        dialog = self.alexa_repository.get_dialog("AMAZON.HelpIntent")

        return (
            handler_input.response_builder.speak(dialog.speak).ask(dialog.ask).response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        dialog = self.alexa_repository.get_dialog("AMAZON.CancelIntent")

        return handler_input.response_builder.speak(dialog.speak).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        dialog = self.alexa_repository.get_dialog("IntentRequest")

        return (
            handler_input.response_builder.speak(dialog.speak).ask(dialog.ask).response
            if dialog.ask
            else handler_input.response_builder.speak(dialog.speak).response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.error(exception, exc_info=True)
        dialog = self.alexa_repository.get_dialog("Exception")

        return (
            handler_input.response_builder.speak(dialog.speak).ask(dialog.ask).response
        )
