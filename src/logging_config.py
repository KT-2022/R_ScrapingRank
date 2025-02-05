import logging
import os
from logging.handlers import RotatingFileHandler

class SimpleRotatingFileHandler(logging.Handler):
    def __init__(self, filename, maxBytes, encoding=None):
        super().__init__()
        self.filename = filename
        self.maxBytes = maxBytes
        self.encoding = encoding
        self._open_file()

    def _open_file(self):
        self.stream = open(self.filename, 'a', encoding=self.encoding)

    def emit(self, record):
        if self.shouldRollover(record):
            self.doRollover()
        self.stream.write(self.format(record) + '\n')
        self.stream.flush()

    def shouldRollover(self, record):
        return self.stream.tell() + len(self.format(record) + '\n') >= self.maxBytes

    def doRollover(self):
        self.stream.close()
        self._open_file()  # ファイルを上書きモードで開き直す

def configure_logging():
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'assets/logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, 'scraping.log')

    log_handler = RotatingFileHandler(
        log_file_path,  # ../assets/logs/scraping.log に保存
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=5,  # 古いログファイルのバックアップを5つまで保持
        encoding='utf-8'
    )
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

    logger.info('Logger is configured with simple rotating file handler.')
    
    return logger, log_handler

def close_logging(logger):
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)
