
import boto3
import typing


class DynamoDbConnector:

    def __init__(
        self,
        table_name,
        access_key_id,
        secret_access_key
    ):
        self.table_name = table_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self._table = None

    @property
    def table(self):
        if not self._table:
            dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name='us-west-2',
            )
            self._table = dynamodb.Table(
                self.table_name
            )
        return self._table

    def fetchone(self, key: dict) -> typing.Dict:
        response = self.table.get_item(
            Key=key
        )
        return response.get('Item')

    def put_item(self, data: dict):
        self.table.put_item(
            Item=data
        )
