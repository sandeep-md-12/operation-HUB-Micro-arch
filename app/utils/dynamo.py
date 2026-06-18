import os
import aioboto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "AuditLogs")


def get_dynamodb():
    return aioboto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


async def init_audit_log_table():
    session = get_dynamodb()
    async with session.client("dynamodb") as client:
        existing = await client.list_tables()
        if DYNAMODB_TABLE_NAME in existing.get("TableNames", []):
            return
        await client.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                {"AttributeName": "request_id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
                {"AttributeName": "actor_id", "AttributeType": "S"},
                {"AttributeName": "action_type", "AttributeType": "S"},
                {"AttributeName": "module_source", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "request_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "ActorIndex",
                    "KeySchema": [
                        {"AttributeName": "actor_id", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "ActionTypeIndex",
                    "KeySchema": [
                        {"AttributeName": "action_type", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "ModuleSourceIndex",
                    "KeySchema": [
                        {"AttributeName": "module_source", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
        )
        waiter = await client.get_waiter("table_exists")
        await waiter.wait(TableName=DYNAMODB_TABLE_NAME)
