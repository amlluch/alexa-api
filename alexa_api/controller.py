from alexa_api.types import LambdaContext, LambdaEvent, LambdaResponse, IotEvent
from ask_sdk_core.skill_builder import SkillBuilder
from typing import Dict, Any
from kink import inject
import json
from alexa_api.iot.iot import StateMachineErr

from alexa_api.intents.alexa_service import (
    LaunchRequestHandler,
    HelpIntentHandler,
    CancelOrStopIntentHandler,
    SessionEndedRequestHandler,
    IntentReflectorHandler,
    CatchAllExceptionHandler,
    EnciendePiscinaIntent,
    ApagaPiscinaIntent,
)
from alexa_api.intents.alexa_repository import AlexaRepository
from alexa_api.devices.service import (
    DevicesService,
    CreateDeviceRequest,
    GetDeviceRequest,
    UpdateDeviceRequest,
    DeleteDeviceRequest,
)
from alexa_api.serverless import serverless
from alexa_api.iot.service import (
    IIotService,
    SendOrderRequest,
    IotToSnsDispatcherEvent,
)


@serverless
@inject
def get_config(event: LambdaEvent, context: LambdaContext, iot_service: IIotService) -> LambdaResponse:
    result = iot_service.get_config()
    return {"statusCode": 200, "body": json.dumps(result)}


@inject
def skill_handler(
    event: LambdaEvent, context: LambdaContext, alexa_repository: AlexaRepository
) -> Dict[str, Any]:

    sb = SkillBuilder()

    sb.add_request_handler(LaunchRequestHandler(alexa_repository))
    sb.add_request_handler(EnciendePiscinaIntent(alexa_repository))
    sb.add_request_handler(ApagaPiscinaIntent(alexa_repository))
    sb.add_request_handler(HelpIntentHandler(alexa_repository))
    sb.add_request_handler(CancelOrStopIntentHandler(alexa_repository))
    sb.add_request_handler(SessionEndedRequestHandler())
    sb.add_request_handler(IntentReflectorHandler(alexa_repository))

    sb.add_exception_handler(CatchAllExceptionHandler(alexa_repository))

    lambda_handler = sb.lambda_handler()
    return lambda_handler(event, context)


@inject
def iot_to_sns_dispatcher(
    event: IotEvent, context: LambdaContext, iot_service: IIotService
) -> None:

    dispatcher_event = IotToSnsDispatcherEvent(event)
    iot_service.dispatch_sns(dispatcher_event)


@serverless
@inject
def create_device(
    event: LambdaEvent, context: LambdaContext, devices_service: DevicesService
) -> LambdaResponse:
    body = json.loads(event["body"])

    request = CreateDeviceRequest(
        body["name"],
        body.get("description"),
        body["position"],
        body["GPIO"],
        body.get("weather_fence"),
        body.get("timer_fence"),
        body.get("device_fence"),
    )

    device_resource = devices_service.create(request)

    return {"statusCode": 200, "body": json.dumps(dict(device_resource))}


@serverless
@inject
def get_device(
    event: LambdaEvent, context: LambdaContext, devices_service: DevicesService
) -> LambdaResponse:
    request = GetDeviceRequest(event["pathParameters"]["device_id"])
    device_resource = devices_service.get(request)

    return {"statusCode": 200, "body": json.dumps(dict(device_resource))}


@serverless
@inject
def get_device_list(
    event: LambdaEvent, context: LambdaContext, devices_service: DevicesService
) -> LambdaResponse:
    return {"statusCode": 200, "body": json.dumps(devices_service.get_list())}


@serverless
@inject
def update_device(
    event: LambdaEvent, context: LambdaContext, devices_service: DevicesService
) -> LambdaResponse:
    device_id = event["pathParameters"]["device_id"]
    body = json.loads(event["body"])

    request = UpdateDeviceRequest(
        device_id,
        body.get("name"),
        body.get("description"),
        body.get("position"),
        body.get("GPIO"),
        body.get("weather_fence"),
        body.get("timer_fence"),
        body.get("device_fence"),
    )
    device_resource = devices_service.update(request)

    return {"statusCode": 200, "body": json.dumps(dict(device_resource))}


@serverless
@inject
def delete_device(
    event: LambdaEvent, context: LambdaContext, devices_service: DevicesService
) -> LambdaResponse:
    request = DeleteDeviceRequest(event["pathParameters"]["device_id"])
    devices_service.delete(request)

    return {"statusCode": 204, "body": ""}


@inject
def timer_fence(event: LambdaEvent, context: LambdaContext, iot_service: IIotService):
    print("SNS arrived :", event)
    iot_service.timer_fence(json.loads(event["Records"][0]["Sns"]["Message"]))


@serverless
@inject
def iot_send_order(
    event: LambdaEvent,
    context: LambdaContext,
    devices_service: DevicesService,
    iot_service: IIotService,
) -> LambdaResponse:
    body = json.loads(event["body"])
    request = SendOrderRequest(
        event["pathParameters"]["device_id"], body["status"], body.get("timeout")
    )

    iot_resource = iot_service.send_order(request)
    return {"statusCode": 200, "body": json.dumps(iot_resource)}


@inject
def stop_device(
    event: LambdaEvent,
    context: LambdaContext,
    devices_service: DevicesService,
    iot_service: IIotService,
) -> Dict[str, StateMachineErr]:
    stop_device_result = iot_service.stop_device(event["state"]["reported"]["device_id"], event["name"])
    return {**event, **{"result": stop_device_result}}
