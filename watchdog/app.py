import os
import asyncio
import logging

from dataclasses import dataclass
from watchdog.core.connectors import DynamoDbConnector
from watchdog.core.watchdog import Watchdog, WatchdogContext

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s, %(levelname)s/%(module)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
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

WATHDOG_SETTINGS_REFRESH_TIME = 15*60


@dataclass
class ApplicationContext:
    watchdog_settings_id: str


class Application:
    """
    Class represents Watchdog application
    """

    def __init__(
        self,
        db_connector: DynamoDbConnector,
        context: ApplicationContext
    ):
        self.context = context
        self.db_connector = db_connector

    async def start(self):
        watchdog = Watchdog()
        while True:
            watchdog.watch(
                WatchdogContext(
                    self.db_connector.fetchone(
                        key={
                            'id': self.context.watchdog_settings_id
                        }
                    )
                )
            )
            await asyncio.sleep(
                WATHDOG_SETTINGS_REFRESH_TIME
            )


def run_app(watchdog_settings_id: str):
    loop = asyncio.get_event_loop()
    try:
        app = Application(
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
