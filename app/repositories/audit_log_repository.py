from app.utils.dynamo import get_dynamodb, DYNAMODB_TABLE_NAME
from boto3.dynamodb.conditions import Key


class AuditLogRepository:
    async def _query(self, index: str, key_attr: str, key_val: str, start: str, end: str) -> list[dict]:
        session = get_dynamodb()
        async with session.resource("dynamodb") as dynamodb:
            table = await dynamodb.Table(DYNAMODB_TABLE_NAME)
            kc = Key(key_attr).eq(key_val)
            if start and end:
                kc &= Key("timestamp").between(start, end)
            result = await table.query(IndexName=index, KeyConditionExpression=kc)
        return result.get("Items", [])

    async def write(self, item: dict) -> dict:
        session = get_dynamodb()
        async with session.resource("dynamodb") as dynamodb:
            table = await dynamodb.Table(DYNAMODB_TABLE_NAME)
            await table.put_item(Item=item)
        return item

    async def query_by_actor(self, actor_id: str, start: str, end: str) -> list[dict]:
        return await self._query("ActorIndex", "actor_id", actor_id, start, end)

    async def query_by_action_type(self, action_type: str, start: str, end: str) -> list[dict]:
        return await self._query("ActionTypeIndex", "action_type", action_type, start, end)

    async def query_by_module_source(self, module_source: str, start: str, end: str) -> list[dict]:
        return await self._query("ModuleSourceIndex", "module_source", module_source, start, end)
