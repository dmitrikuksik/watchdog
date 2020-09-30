import asyncio
import time
import logging

from typing import Optional, List, Dict
from watchdog.core.connectors import SnsConnector
from watchdog.core.service import (
    Service, CommandException
)

logger = logging.getLogger(__name__)

WATHDOG_RELOAD = 15*60


class WatchdogException(Exception):
    pass


class WatchdogContext:

    def __init__(
        self,
        list_of_services: List[str],
        num_of_sec_check: int,
        num_of_sec_wait: int,
        num_of_attempts: int
    ):
        self.services = [
            Service(s) for s in list_of_services
        ]

        if (
            num_of_sec_check < 0 or
            num_of_sec_wait < 0 or
            num_of_attempts < 0
        ):
            raise WatchdogException(
                'Invalid watchdog settings. '
                'Values can\'t be negative.'
            )

        self.num_of_sec_check = num_of_sec_check
        self.num_of_sec_wait = num_of_sec_wait
        self.num_of_attempts = num_of_attempts

    @classmethod
    def from_dict(cls, data: Dict) -> 'WatchdogContext':
        return cls(
            list_of_services=data.get(
                'ListOfServices'
            ),
            num_of_sec_check=int(
                data.get('NumOfSecCheck')
            ),
            num_of_sec_wait=int(
                data.get('NumOfSecWait')
            ),
            num_of_attempts=int(
                data.get('NumOfAttempts')
            )
        )


class Watchdog:
    """
    Class represents watchdog that checks
    the status of Linux services
    """

    def __init__(
        self,
        sns_connector: SnsConnector,
        reload_after: int = WATHDOG_RELOAD,
        context: Optional[WatchdogContext] = None
    ):
        self.sns_connector = sns_connector
        self.reload_after = reload_after
        self.context = context

    def setup(self, context: WatchdogContext):
        self.context = context

    def propogate(self, msg):
        logger.info(msg)
        self.sns_connector.publish(msg)

    async def check(self, service: Service):
        logger.info(f'({service}): checking...')

        if service.ping():
            logger.info(f'({service}): service is up')
            return

        self.propogate(f'({service}): service is down')

        for i in range(self.context.num_of_attempts):
            logger.info(
                f'({service}): attempt to start service ({i+1})'
            )

            service.start()
            if service.ping():
                self.propogate(
                    f'({service}): service is up after {i+1} attempt(s)'
                )
                return

            await asyncio.sleep(
                self.context.num_of_sec_wait
            )

        self.propogate(
            f'({service}): failed to start after '
            f'{self.context.num_of_attempts} attempt(s)'
        )

    def create_service_pool(self):
        futures = []
        for service in self.context.services:
            futures.append(
                asyncio.ensure_future(
                    self.check(service)
                )
            )
        return futures

    async def watch(self):
        if not self.context:
            raise WatchdogException(
                'Watchdog is not configured. Please, '
                'use setup() to set watchdog settings.'
            )

        tick = time.time()
        while True:
            tock = time.time() - tick
            if tock >= self.reload_after:
                break

            try:
                await asyncio.gather(
                    *self.create_service_pool()
                )
            except CommandException as exc:
                raise WatchdogException(exc)

            await asyncio.sleep(
                self.context.num_of_sec_check
            )
