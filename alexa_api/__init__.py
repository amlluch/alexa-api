import boto3
from kink import di
from os import environ
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

di["dynamo_db"] = boto3.resource(
    "dynamodb", region_name=environ.get("AWS_REGION", "us-east-1")
)

di["devices_table"] = di["dynamo_db"].Table(environ.get("DB_DEVICES_TABLE", "devices"))
di["dialogs_table"] = di["dynamo_db"].Table(environ.get("DB_INTENTS_TABLE", "devices"))

s3 = boto3.resource("s3")
bucket = s3.Bucket(environ.get("S3_CERTIFICATES"))

S3_CERTIFICATES = environ.get("S3_CERTIFICATES")
S3_CLIENT_CERTIFICATES = environ.get("S3_CLIENT_CERTIFICATES")
IOT_CA_ROOT = environ.get('IOT_CA_ROOT')
IOT_PRIV_PEM = environ.get('IOT_PRIV_PEM')
IOT_CERT_PEM = environ.get('IOT_CERT_PEM')
IOT_ENDPOINT = environ.get("IOT_ENDPOINT")
IOT_PORT = int(environ.get("IOT_PORT"))

for cert_file in bucket.objects.all():
    s3.Object(S3_CERTIFICATES, cert_file.key).download_file(f"/tmp/{cert_file.key}")

myAWSIoTMQTTShadowClient = AWSIoTMQTTClient(environ.get("IOT_CLIENT_ID", "AWSIoT"), cleanSession=False)
myAWSIoTMQTTShadowClient.configureEndpoint(
    IOT_ENDPOINT, IOT_PORT
)

myAWSIoTMQTTShadowClient.configureCredentials(
    f"/tmp/{IOT_CA_ROOT}",
    f"/tmp/{IOT_PRIV_PEM}",
    f"/tmp/{IOT_CERT_PEM}"
)
device_handler = myAWSIoTMQTTShadowClient
device_handler.configureMQTTOperationTimeout(25)

di["iot"] = device_handler
