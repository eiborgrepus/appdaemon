import logging
from logging.handlers import RotatingFileHandler
import sys


_NAME_TO_STREAM = {
    'STDERR' : sys.stderr,
    'STDOUT' : sys.stdout
}


def setup_default_logger(name, level, filename=sys.stderr):
    if filename in _NAME_TO_STREAM:
        filename = _NAME_TO_STREAM[filename]

    logger = logging.getLogger(name)
    numeric_level = getattr(logging, level, None)
    logger.setLevel(numeric_level)
    logger.propagate = False
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.StreamHandler(stream=filename) \
        if filename == sys.stderr or filename == sys.stdout \
        else RotatingFileHandler(filename, maxBytes=1000000, backupCount=3)
    handler.setLevel(numeric_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger, handler


def setup_logging(conf):
    if conf.logfile is None:
        conf.logfile = "STDOUT"

    if conf.errorfile is None:
        conf.errorfile = "STDERR"

    if conf.app_daemon_config.daemon and (
                conf.logfile == "STDOUT" or conf.errorfile == "STDERR"
                or conf.logfile == "STDERR" or conf.errorfile == "STDOUT"
    ):
        raise ValueError("STDOUT and STDERR not allowed with -d")

    conf.logger,fh = setup_default_logger('log1', conf.loglevel, conf.logfile)
    conf.error,efh = setup_default_logger('log2', conf.loglevel, conf.errorfile)

    return [fh.stream.fileno(), efh.stream.fileno()]
