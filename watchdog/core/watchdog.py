import logging

from typing import Dict
from watchdog.core.service import Service

logger = logging.getLogger('watchdog')


class WatchdogContext:

    def __init__(self, item: Dict):
        self.list_of_sevices = [
            Service(s) for s in item['ListOfServices']
        ]
        self.num_of_sec_check = int(
            item['NumOfSecCheck']
        )
        self.num_of_sec_wait = int(
            item['NumOfSecWait']
        )
        self.num_of_attempts = int(
            item['NumOfAttempts']
        )


class Watchdog:

    def watch(self, context: WatchdogContext):
        logger.info('Watchdog started...')

        for service in context.list_of_sevices:
            if service.ping():
                logger.info(f'Service {service} is up.')
