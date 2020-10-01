import unittest
from decimal import Decimal

from watchdog.core.watchdog import (
    WatchdogContext, WatchdogException
)


class WatchdogContextTestCase(unittest.TestCase):

    def test_watchdog_context_from_dict(self):
        data = {
            'ListOfServices': [
                'mysql', 'docker'
            ],
            'NumOfSecCheck': Decimal(60),
            'NumOfSecWait': Decimal(10),
            'NumOfAttempts': Decimal(4)
        }

        context = WatchdogContext.from_dict(data)

        self.assertEqual(len(context.services), 2)
        self.assertEqual(context.services[0].name, 'mysql')
        self.assertEqual(context.num_of_sec_check, 60)
        self.assertEqual(context.num_of_sec_wait, 10)
        self.assertEqual(context.num_of_attempts, 4)

    def test_invalid_watchdog_context_from_dict(self):
        data = {
            'ListOfServices': [],
            'NumOfSecCheck': Decimal(-60),
            'NumOfAttempts': Decimal(-4)
        }

        with self.assertRaises(WatchdogException):
            WatchdogContext.from_dict(data)


if __name__ == '__main__':
    unittest.main()
