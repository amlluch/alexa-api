from os import environ

DESIRED_TOPIC = environ.get("IOT_DESIRED_TOPIC", "")
REPORTED_TOPIC = environ.get("IOT_REPORTED_TOPIC", "")
BASE_TOPIC = environ.get("IOT_BASE_TOPIC", "")
OW_ENDPOINT = environ.get("OW_ENDPOINT", "")
OW_APPID = environ.get("OW_APPID", "")
OW_LAT = environ.get("OW_LAT", "")
OW_LON = environ.get("OW_LON", "")
TIMER_FENCE_ARN = environ.get("TIMER_FENCE_ARN", "")
SNS_ARN = environ.get("SNS_ARN", "")
