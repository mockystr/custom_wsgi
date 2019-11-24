import logging


def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s [%(name)s.%(filename)s:%(lineno)s '
        '%(funcName)s]  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


wsgi_logger = set_logger('wsgi_logger')
