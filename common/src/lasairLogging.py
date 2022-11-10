"""Common Lasair logging module. Based on standard logging module with sensible default
values for Lasair. Sets up a log file and also sends error and above messages to Slack."""

import os, logging
#import slack_webhook


class SlackHandler(logging.Handler):
    def __init__(self, webhook):
        super().__init__()
        self.webhook = webhook

    def emit(self, record):
        """Emit a record."""
        msg = self.format(record)
        self.webhook.send(msg)


def basicConfig(filename, webhook=None, level=logging.INFO, force=False):
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


def getLogger(name):
    return logging.getLogger(name)


def shutdown():
    logging.shutdown()
