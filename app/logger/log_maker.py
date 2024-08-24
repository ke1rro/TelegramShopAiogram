from loguru import logger


logger.remove()
logger.add("bot_logs.log",
           rotation="200 MB",
           compression="zip",
           level="INFO",
           format="{time} {level} {message}",
           backtrace=True,
           diagnose=True)
