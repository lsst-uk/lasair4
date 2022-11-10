"""Unit tests for Lasair logging module."""

import context
import lasairLogging
import os
import unittest, unittest.mock
# from manage_status import manage_status


class CommonLoggingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.exists("logging_test.log"):
            os.remove("logging_test.log")
        with unittest.mock.MagicMock() as mock_slack_webhook:
            lasairLogging.basicConfig(
                filename="logging_test.log",
                slack_webhook=mock_slack_webhook
            )


    @classmethod
    def tearDownClass(cls):
        lasairLogging.shutdown()
        if os.path.exists("logging_test.log"):
            os.remove("logging_test.log")

    def test_new_logger(self):
        """Start a new logger with a new output file, log a message. The output
        file should exist and contain the message in the right format."""
        log = lasairLogging.getLogger("test_logger")
        log.info("Test message")
        with open("logging_test.log", "r") as f:
            self.assertEqual("Test message", f.readline().strip())


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
