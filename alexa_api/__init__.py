import boto3
from kink import di
from os import environ
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

di["dynamo_db"] = boto3.resource(
    "dynamodb", region_name=environ.get("AWS_REGION", "us-east-1")
)

di["devices_table"] = di["dynamo_db"].Table(environ.get("DB_DEVICES_TABLE", "devices"))
di["dialogs_table"] = di["dynamo_db"].Table(environ.get("DB_INTENTS_TABLE", "devices"))

s3 = boto3.resource('s3')
bucket = s3.Bucket(environ.get('S3_CERTIFICATES'))
for key in bucket.objects.all():
    s3.Object(environ.get('S3_CERTIFICATES'), key.key).download_file(f"/tmp/{key.key}")

myAWSIoTMQTTShadowClient = AWSIoTMQTTClient(environ.get("IOT_CLIENT_ID", "AWSIoT"))
myAWSIoTMQTTShadowClient.configureEndpoint(environ.get("IOT_ENDPOINT"), int(environ.get("IOT_PORT")))

myAWSIoTMQTTShadowClient.configureCredentials(f"/tmp/{environ.get('IOT_CA_ROOT')}", f"/tmp/{environ.get('IOT_PRIV_PEM')}", f"/tmp/{environ.get('IOT_CERT_PEM')}")
device_handler = myAWSIoTMQTTShadowClient

di["iot"] = device_handler
