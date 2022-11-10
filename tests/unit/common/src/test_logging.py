"""Unit tests for Lasair logging module."""
import context
import lasairLogging
import os
import glob
import unittest, unittest.mock
# from manage_status import manage_status


class CommonLoggingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for name in glob.glob("test_*.log"):
            if os.path.exists(name):
                os.remove(name)

    @classmethod
    def tearDownClass(cls):
        lasairLogging.shutdown()

    def test_new_logger(self):
        """Start a new logger with a new output file, log a message. The output
        file should exist and contain the message in the right format."""
        lasairLogging.basicConfig(
            filename="test_new_logger.log",
            force=True
        )
        log = lasairLogging.getLogger("test_logger")
        log.info("Test message")
        with open("test_new_logger.log", "r") as f:
            self.assertRegex(f.readline().strip(),
                             "^\\[.*\\] INFO: test_new_logger: Test message")

    def test_existing_logger(self):
        """Start a logger with an existing output file, log a message.
        The output file should contain both messages in the right format."""
        with open("test_existing_logger.log", "w") as f:
            f.write("An existing line\n")
        lasairLogging.basicConfig(
            filename="test_existing_logger.log",
            force=True
        )
        log = lasairLogging.getLogger("test_logger")
        log.info("Test message 2")
        with open("test_existing_logger.log", "r") as f:
            self.assertRegex(f.readlines()[-1].strip(),
                             "^\\[.*\\] INFO: test_existing_logger: Test message 2")

    def test_slack_error(self):
        """Start a logger configured to send >=ERROR to Slack (mock).
        Send an ERROR message. The (mock) Slack webhook should be called."""
        with unittest.mock.MagicMock() as mock_slack_webhook:
            lasairLogging.basicConfig(
                filename="test_slack_error.log",
                webhook=mock_slack_webhook,
                force=True
            )
            log = lasairLogging.getLogger("test_logger")
            log.error("Test message 3")
            with open("test_slack_error.log", "r") as f:
                self.assertRegex(f.readlines()[-1].strip(),
                                 "^\\[.*\\] ERROR: test_slack_error: Test message 3")
            mock_slack_webhook.send.assert_called_once()

    def test_slack_info(self):
        """Start a logger configured to send >=ERROR to Slack (mock).
        Send an INFO message. The (mock) Slack webhook should NOT be called."""
        with unittest.mock.MagicMock() as mock_slack_webhook:
            lasairLogging.basicConfig(
                filename="test_slack_info.log",
                webhook=mock_slack_webhook,
                force=True
            )
            log = lasairLogging.getLogger("test_logger")
            log.info("Test message 4")
            with open("test_slack_info.log", "r") as f:
                self.assertRegex(f.readlines()[-1].strip(),
                                 "^\\[.*\\] INFO: test_slack_info: Test message 4")
            mock_slack_webhook.send.assert_not_called()


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
