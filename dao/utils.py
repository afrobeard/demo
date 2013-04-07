import logging
from logging.handlers import RotatingFileHandler

def addFileLogger(logger_object, log_name, level=2):
    rotating_file_handler = RotatingFileHandler(log_name)
    rotating_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    logger_object.addHandler(rotating_file_handler)
    logger_object.level = level
