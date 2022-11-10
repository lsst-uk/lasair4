"""Common Lasair logging module. Based on standard logging module with sensible default
values for Lasair. Sets up a log file and also sends error and above messages to Slack."""

import os, logging
from slack_webhook import SlackWebhook


class SlackHandler(logging.Handler):
    """Logging handler to send Slack messages"""
    def __init__(self, webhook: SlackWebhook):
        super().__init__()
        self.webhook = webhook

    def emit(self, record):
        """Emit a record."""
        msg = self.format(record)
        self.webhook.send(msg)


class DuplicateFilter(logging.Filter):
    def __init__(self, webhook: SlackWebhook):
        super().__init__()
        self.n_msg = 0
        self.webhook = webhook

    def filter(self, record):
        current_log = (record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None) or self.n_msg > 19:
            if self.n_msg > 0:
                self.webhook.send("Suppressed {} identical messages".format(self.n_msg))
            self.last_log = current_log
            self.n_msg = 0
            return True
        self.n_msg += 1
        return False


def basicConfig(filename, webhook: SlackWebhook = None, level=logging.INFO, force=False, merge=False):
    logging.basicConfig(
        filename=filename,
        level=level,
        format="[%(asctime)s] %(levelname)s: %(funcName)s: %(message)s",
        force=force
    )
    if webhook is not None:
        hostname = os.uname().nodename
        slack_formatter = logging.Formatter(
            "%(levelname)s: {}: %(funcName)s: %(message)s".format(hostname))
        slack_handler = SlackHandler(webhook)
        slack_handler.setLevel(logging.ERROR)
        slack_handler.setFormatter(slack_formatter)
        logging.getLogger().addHandler(slack_handler)
        if merge:
            slack_handler.addFilter(DuplicateFilter(webhook))


def getLogger(name):
    return logging.getLogger(name)


def shutdown():
    logging.shutdown()
