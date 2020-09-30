import os
import asyncio
import logging

from watchdog.core.connectors import DynamoDbConnector
from watchdog.core.watchdog import (
    Watchdog, WatchdogContext, WatchdogException
)


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s, %(levelname)s/%(module)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('watchdog')

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

    def load_watchdog_settings(self):
        item = self.db_connector.fetchone(
            key={
                'id': self.context.watchdog_settings_id
            }
        )
        return item

    async def start(self):
        logger.info('Starting watchdog...')
        while True:
            logger.info('Loading watchdog settings from database...')
            settings = self.load_watchdog_settings()
            if not settings:
                logger.error('Failed to load watchdog settings.')
                break

            try:
                self.watchdog.setup(
                    WatchdogContext.from_dict(
                        settings
                    )
                )
                await self.watchdog.watch()
            except WatchdogException:
                break

        logger.info(
            'Stopping watchdog...'
        )


def run_app(watchdog_settings_id: str):
    loop = asyncio.get_event_loop()
    try:
        app = Application(
            Watchdog(),
            DynamoDbConnector(
                AWS_WATCHDOG_TABLE,
                AWS_ACCESS_KEY_ID,
                AWS_SECRET_ACCESS_KEY,
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
