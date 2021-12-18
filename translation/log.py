import logging

logger = logging.getLogger("translation")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] {%(filename)s}: %(message)s"
)
channel = logging.StreamHandler()

channel.setFormatter(formatter)
logger.addHandler(channel)
