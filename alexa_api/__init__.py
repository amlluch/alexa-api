import boto3
from kink import di
from os import environ

di["dynamo_db"] = boto3.resource(
    "dynamodb", region_name=environ.get("AWS_REGION", "us-east-1")
)

di["devices_table"] = di["dynamo_db"].Table(environ.get("DB_DEVICES_TABLE", "devices"))
di["dialogs_table"] = di["dynamo_db"].Table(environ.get("DB_INTENTS_TABLE", "devices"))
