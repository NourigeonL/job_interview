import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
class Logger:

    def __init__(self, name='log', log_level='DEBUG', prefix='local', log_dir='logs'):
        """
        Configures a daily logger
        :param name: logger's name
        :param log_level: logger severity configuration
        :param prefix: a prefix that will be added to the log file
        """
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 1. Creates a logger using Python's logging facility.
        self.logger = logging.getLogger(name)

        # 2. Sets logger's severity threshold.
        self.logger.setLevel(log_level)

        # 3. Creates a daily log file and stores it at log_dir
        # prepending a prefix.
        fh = TimedRotatingFileHandler(
            os.path.join(log_dir, prefix), 
            when='midnight', 
            interval=1
        )

        # 4. Adds the date to the daily log file name.
        fh.suffix = "%Y%m%d.log"

        # 5. Configures the log string format
        formatter = logging.Formatter(
            '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
        )
        fh.setFormatter(formatter)

        # Adds the handler to the logger
        self.logger.addHandler(fh)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger