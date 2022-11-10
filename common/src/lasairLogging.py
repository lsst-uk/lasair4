"""Common Lasair logging module. Based on standard logging module with sensible default
values for Lasair. Sets up a log file and also sends error and above messages to Slack."""

import logging


def basicConfig(filename, slack_webhook=None, level=logging.INFO):
    logging.basicConfig(
        filename=filename,
        level=level,
        format="[%(asctime)s]:%(levelname)s:%(funcName)s:%(message)s"
    )


def getLogger(name):
    return logging.getLogger(name)


def shutdown():
    logging.shutdown()
