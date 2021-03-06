import os
import subprocess

from enum import Enum


class ExitCode(Enum):
    SUCCESS = 0
    NONZERO = 3


class CommandException(Exception):
    pass


class Command:
    """
    Class represents interface for executing shell commands.
    """

    def __init__(self):
        pass

    def __call__(self, *args: str):
        return self.exec(*args)

    @classmethod
    def exec(cls, *args) -> int:
        try:
            with open(os.devnull, 'wb') as out:
                code = subprocess.call(
                    args, stdout=out, stderr=out
                )
                return code
        except FileNotFoundError as err:
            raise CommandException(
                'Failed to execute command: {}.\n{}'.format(
                    ' '.join(args),
                    err
                )
            ) from err


class Service:
    """
    Class represents interface for Linux services.
    """

    def __init__(self, name: str):
        self.name = name
        self.cmd = Command()

    def __str__(self):
        return f'{self.name}.service'

    def ping(self) -> bool:
        code = self.cmd(
            'systemctl', 'is-active', '--quiet', str(self)
        )
        return code == ExitCode.SUCCESS.value

    def start(self) -> bool:
        code = self.cmd(
            # TODO: remove sudo
            'sudo', 'systemctl', 'start', str(self)
        )
        return code == ExitCode.SUCCESS.value

    def stop(self) -> bool:
        code = self.cmd(
            # TODO: remove sudo
            'sudo', 'systemctl', 'stop', str(self)
        )
        return code == ExitCode.SUCCESS.value
