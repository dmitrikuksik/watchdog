import json
import boto3
import typing

from botocore.exceptions import ClientError, ParamValidationError


class DynamoDbException(Exception):
    pass


class AwsConnectorContext:
    """
    Class represents connector context for AWS resources
    """

    def __init__(
        self,
        region: str,
        account_id: str,
        access_key_id: str,
        secret_access_key: str
    ):
        self.region = region
        self.account_id = account_id
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key


class DynamoDbConnector:
    """
    Class represents connector for AWS DynamoDB table
    """

    def __init__(
        self,
        table_name: str,
        context: AwsConnectorContext
    ):
        self.table_name = table_name
        self.context = context
        self._table = None

    @property
    def table(self):
        if not self._table:
            dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.context.access_key_id,
                aws_secret_access_key=self.context.secret_access_key,
                region_name='us-west-2',
            )
            self._table = dynamodb.Table(
                self.table_name
            )
        return self._table

    def fetchone(self, key: dict) -> typing.Dict:
        try:
            response = self.table.get_item(
                Key=key
            )
            return response.get('Item')
        except (
            ParamValidationError,
            ClientError
        ) as err:
            raise DynamoDbException(err)

    def put_item(self, data: dict):
        self.table.put_item(
            Item=data
        )


class SnsConnector:
    """
    Class represents connector for AWS SNS topic
    """

    def __init__(
        self,
        topic_name: str,
        context: AwsConnectorContext
    ):
        self.topic_name = topic_name
        self.context = context
        self._client = None

    @property
    def topic_arn(self):
        return 'arn:aws:sns:{}:{}:{}'.format(
            self.context.region,
            self.context.account_id,
            self.topic_name
        )

    @property
    def client(self):
        if not self._client:
            self._client = boto3.client(
                'sns', self.context.region
            )
        return self._client

    def publish(self, msg: str):
        response = self.client.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(
                {
                    'default': json.dumps(msg)
                }
            ),
            MessageStructure='json'
        )
        return response
