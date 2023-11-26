from loguru import logger as loguru_logger
import logging

class InterceptHandler(logging.Handler):
    def emit(self, record):
        loguru_logger.opt(depth=6, exception=record.exc_info).log(
            record.levelname, record.getMessage()
        )