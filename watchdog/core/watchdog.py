import asyncio
import time
import logging

from typing import Optional, List, Dict
from watchdog.core.connectors import SnsConnector
from watchdog.core.service import (
    Service, CommandException
)

logger = logging.getLogger(__name__)


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
        if (
            num_of_sec_check < 0 or
            num_of_sec_wait < 0 or
            num_of_attempts < 0
        ):
            raise WatchdogException(
                'Invalid watchdog settings. '
                'Values can\'t be negative.'
            )

        self.services = [
            Service(s) for s in list_of_services
        ]
        self.num_of_sec_check = num_of_sec_check
        self.num_of_sec_wait = num_of_sec_wait
        self.num_of_attempts = num_of_attempts

    @classmethod
    def from_dict(cls, data: Dict) -> 'WatchdogContext':
        return cls(
            list_of_services=data.get(
                'ListOfServices', []
            ),
            num_of_sec_check=int(
                data.get('NumOfSecCheck', 0)
            ),
            num_of_sec_wait=int(
                data.get('NumOfSecWait', 0)
            ),
            num_of_attempts=int(
                data.get('NumOfAttempts', 0)
            )
        )


class Watchdog:
    """
    Class represents watchdog that checks
    the status of Linux services
    """

    def __init__(
        self,
        context: Optional[WatchdogContext] = None,
        sns_connector: Optional[SnsConnector] = None
    ):
        self.context = context
        self.sns_connector = sns_connector

    def setup(self, context: WatchdogContext):
        self.context = context

    def propagate(self, msg):
        logger.info(msg)
        if self.sns_connector:
            self.sns_connector.publish(msg)

    async def check(self, service: Service):
        logger.info(
            '({}): checking...'.format(service)
        )

        if service.ping():
            logger.info(
                '({}): service is up'.format(service)
            )
            return

        self.propagate(
            '({}): service is down'.format(service)
        )

        for i in range(self.context.num_of_attempts):
            logger.info(
                '({}): attempt to start service ({})'.format(
                    service, i+1
                )
            )

            service.start()
            if service.ping():
                self.propagate(
                    '({}): service is up after {} attempt(s)'.format(
                        service, i+1
                    )
                )
                return

            await asyncio.sleep(
                self.context.num_of_sec_wait
            )

        self.propagate(
            '({}): failed to start after {} attempt(s)'.format(
                service, self.context.num_of_attempts
            )
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

    async def watch(self, lifetime: Optional[int] = None):
        """
        Function starts checking watchdog services in loop

        :param lifetime: optional, determines after what time
        period exit the loop
        """

        if not self.context:
            raise WatchdogException(
                'Watchdog is not configured. Please, '
                'use setup() to set watchdog settings.'
            )

        tick = time.time()
        while True:
            tock = time.time() - tick
            if lifetime is not None and tock >= lifetime:
                break

            try:
                await asyncio.gather(
                    *self.create_service_pool()
                )
            except CommandException as exc:
                raise WatchdogException(exc) from exc

            await asyncio.sleep(
                self.context.num_of_sec_check
            )
