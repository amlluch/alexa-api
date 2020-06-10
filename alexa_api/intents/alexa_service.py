import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from kink import inject

from ask_sdk_model import Response
from alexa_api.intents.alexa_repository import AlexaRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@inject
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input:  HandlerInput) -> bool:

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Bienvenido. Quieres encender o apagar la piscina, el riego de arriba, el riego de abajo o la zona chill out?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


@inject
class EnciendePiscinaIntent(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Handler for Hello World Intent."""
    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_intent_name("EnciendePiscinaIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        print(self.alexa_repository.get_dialog(ask_utils.get_intent_name(handler_input)))
        speak_output = "Voy a encender la piscina"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


@inject
class ApagaPiscinaIntent(AbstractRequestHandler):
    def __init__(self, alexa_repository: AlexaRepository) -> None:
        self.alexa_repository = alexa_repository

    """Handler for Hello World Intent."""
    def can_handle(self, handler_input: HandlerInput) -> bool:

        print(ask_utils.get_intent_name(handler_input))
        return ask_utils.is_intent_name("ApagaPiscinaIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        speak_output = "Voy a apagar la piscina"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


@inject
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input: HandlerInput) -> bool:

        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:

        speak_output = "Esta aplicacion te permite controlar distintos dispositivos del jardín. Puedes encender o apagar la piscina, el riego de arriba, el riego de abajo y la zona chill out."
        ask_output = "Qué quieres hacer?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


@inject
class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hasta luego MariCarmen!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


@inject
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


@inject
class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Disparaste " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


@inject
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Lo siento. Tengo problemas entendiendo lo que pides. Inténtalo de nuevo"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
