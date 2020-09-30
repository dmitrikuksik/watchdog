import asyncio
import time
import logging

from typing import Optional, List, Dict
from watchdog.core.service import Service

logger = logging.getLogger('watchdog')

WATHDOG_RELOAD = 15*60


class WatchdogException(Exception):
    pass


class WatchdogContext:

    def __init__(
        self,
        listofservices: List,
        numofseccheck: int,
        numofsecwait: int,
        numofattempts: int
    ):
        self.services = [Service(s) for s in listofservices]
        self.numofseccheck = numofseccheck
        self.numofsecwait = numofsecwait
        self.numofattempts = numofattempts

    @classmethod
    def from_dict(cls, data: Dict) -> 'WatchdogContext':
        return cls(
            listofservices=data.get(
                'ListOfServices'
            ),
            numofseccheck=int(
                data.get('NumOfSecCheck')
            ),
            numofsecwait=int(
                data.get('NumOfSecWait')
            ),
            numofattempts=int(
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
        reload_after: int = WATHDOG_RELOAD,
        context: Optional[WatchdogContext] = None
    ):
        self.reload_after = reload_after
        self.context = context

    def setup(self, context: WatchdogContext):
        self.context = context

    async def check(self, service: Service):
        logger.info(f'Checking {service}...')

        if service.ping():
            logger.info(f'Service {service} is up.')
            return

        for i in range(self.context.numofattempts):
            logger.info(
                f'#{i+1}: Attempt to start service {service}.'
            )

            service.start()
            if service.ping():
                logger.info(
                    f'Service {service} is up after {i+1} attempts.'
                )
                return

            await asyncio.sleep(
                self.context.numofsecwait
            )

        logger.info(
            f'Failed to start {service} after '
            f'{self.context.numofattempts} attempts.'
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
            logger.error(
                'Watchdog is not configured. '
                'Please, use setup() to set context.'
            )
            raise WatchdogException(
                'Watchdog is not configured.'
            )

        tick = time.time()
        while True:
            tock = time.time() - tick
            if tock >= self.reload_after:
                break

            await asyncio.gather(
                *self.create_service_pool()
            )

            await asyncio.sleep(
                self.context.numofseccheck
            )
