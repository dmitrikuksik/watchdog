import os
import sys
import asyncio
import logging

from typing import Optional

from watchdog.core.connectors import (
    AwsConnectorContext, DynamoDbConnector,
    DynamoDbException, SnsConnector,
)
from watchdog.core.watchdog import (
    Watchdog, WatchdogContext, WatchdogException
)

logger = logging.getLogger(__name__)

LINUX = 'linux'

AWS_REGION = os.environ.get(
    'AWS_REGION', ''
)

AWS_ACCOUNT_ID = os.environ.get(
    'AWS_ACCOUNT_ID', ''
)

AWS_ACCESS_KEY_ID = os.environ.get(
    'AWS_ACCESS_KEY_ID', ''
)

AWS_SECRET_ACCESS_KEY = os.environ.get(
    'AWS_SECRET_ACCESS_KEY', ''
)

AWS_WATCHDOG_TABLE = os.environ.get(
    'AWS_WATCHDOG_TABLE', ''
)

AWS_WATCHDOG_SNS_TOPIC = os.environ.get(
    'AWS_WATCHDOG_SNS_TOPIC', ''
)


class ApplicationContext:

    def __init__(self, watchdog_settings_id: str):
        self.watchdog_settings_id = watchdog_settings_id


class Application:
    """
    Class represents Watchdog application
    """

    def __init__(
        self,
        watchdog: Watchdog,
        db_connector: DynamoDbConnector,
        context: ApplicationContext
    ):
        self.watchdog = watchdog
        self.db_connector = db_connector
        self.context = context

    def fetch_watchdog_settings(self):
        item = self.db_connector.fetchone(
            key={
                'id': self.context.watchdog_settings_id
            }
        )
        return item

    async def start(self):
        logger.info('Starting watchdog...')
        while True:
            logger.info(
                'Fetching watchdog settings from database...'
            )
            try:
                settings = self.fetch_watchdog_settings()
                if not settings:
                    logger.error(
                        'Failed to fetch watchdog settings.'
                    )
                    break
            except DynamoDbException as exc:
                logger.error(exc)
                break

            try:
                self.watchdog.setup(
                    WatchdogContext.from_dict(
                        settings
                    )
                )
                await self.watchdog.watch()
            except WatchdogException as exc:
                logger.error(exc)
                break

        logger.info(
            'Stopping watchdog...'
        )


def setup_logging(logfile: Optional[str] = None):
    handlers = [logging.StreamHandler()]
    if logfile:
        handlers = [
            logging.FileHandler(
                filename=logfile,
                mode='a',
            )
        ]
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s, %(levelname)s/%(module)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )


def run_app(
    watchdog_settings_id: str,
    logfile: Optional[str] = None
):
    print(
        '############################################################\n'
        '##                                                        ##\n'
        '##                 Linux Service Watchdog                 ##\n'
        '##                                                        ##\n'
        '############################################################\n\n'
        'Author:\n'
        '\t Dmitri Kuksik\n'
        'Configs:\n'
        f'\t Platform: {sys.platform}\n'
        f'\t DynamoDB table: {AWS_WATCHDOG_TABLE}\n'
        f'\t SNS topic: {AWS_WATCHDOG_SNS_TOPIC}\n'
        f'\t Watchdog settings id: {watchdog_settings_id}\n'
    )

    setup_logging(logfile=logfile)

    if sys.platform != LINUX:
        logger.error(
            'Watchdog application is only supported '
            'on Linux platforms.'
        )
        return

    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        logger.error(
            'AWS credentials wasn\'t found. '
            'Export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY '
            'to run watchdog.'
        )
        return

    if not AWS_REGION:
        logger.error(
            'AWS region wasn\'t found. '
            'Export AWS_REGION to run watchdog.'
        )
        return

    if not AWS_ACCOUNT_ID:
        logger.error(
            'AWS account id wasn\'t found. '
            'Export AWS_ACCOUNT_ID to run watchdog.'
        )
        return

    if not AWS_WATCHDOG_TABLE:
        logger.error(
            'AWS DynamoDB table wasn\'t found. '
            'Export AWS_WATCHDOG_TABLE to run watchdog.'
        )
        return

    if not AWS_WATCHDOG_SNS_TOPIC:
        logger.error(
            'AWS SNS topic wasn\'t found. '
            'Export AWS_WATCHDOG_SNS_TOPIC to run watchdog.'
        )
        return

    loop = asyncio.get_event_loop()
    try:
        aws_context = AwsConnectorContext(
            AWS_REGION,
            AWS_ACCOUNT_ID,
            AWS_ACCESS_KEY_ID,
            AWS_SECRET_ACCESS_KEY,
        )
        app = Application(
            Watchdog(
               SnsConnector(
                   AWS_WATCHDOG_SNS_TOPIC,
                   aws_context
               )
            ),
            DynamoDbConnector(
                AWS_WATCHDOG_TABLE,
                aws_context
            ),
            ApplicationContext(
                watchdog_settings_id
            )
        )
        loop.run_until_complete(app.start())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
