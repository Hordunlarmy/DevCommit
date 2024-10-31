import logging
import os

from decouple import Config, RepositoryEnv

# Load configuration from the custom file
home_dir = os.path.expanduser("~/.dcommit")

config = Config(RepositoryEnv(home_dir))


class Logger:
    """Class Config For Logger"""

    def __init__(
        self,
        logger_name: str,
        log_file: str = "dc.logs",
        log_level: int = logging.DEBUG,
    ):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)
        self.formatter = logging.Formatter(
            "\n%(levelname)s:   %(asctime)s  (%(name)s) ==  %(message)s"
            "[%(lineno)d]"
        )

        # file handler
        # self.file_handler = logging.FileHandler(log_file)
        # self.file_handler.setFormatter(self.formatter)
        # self.logger.addHandler(self.file_handler)

        # console handler
        # self.console_handler = logging.StreamHandler()
        # self.console_handler.setFormatter(self.formatter)
        # self.logger.addHandler(self.console_handler)

    def get_logger(self):
        return self.logger
