"""
AETHER Root Logging controller. Provides root logger and instances for module loggers
"""

import logging
from os.path import exists, getsize, join

import click

DEFAULT_FORMAT = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    "%Y-%m-%d %H:%M:%S",
)
VERBOSE_FORMAT = logging.Formatter(
    "%(asctime)s %(name)s.%(module)s:%(lineno)s [%(levelname)s] %(message)s",
    "%Y-%m-%d %H:%M:%S",
)

CLIENT_LOG = "client_log.txt"
SERVER_LOG = "server_log.txt"


def log_splash_status(progress: int, text: str) -> None:
    click.echo(f"STATUS::{progress}::{text}::END_STATUS")


def setup_module_logger(module_name, log_dir=None, log_file=SERVER_LOG, verbose=True):
    """
    This function returns a module-specific logger instance
    """
    modules = module_name.split(".")
    if modules[-1] == "log":
        modules.pop()

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("tornado").setLevel(logging.WARNING)

    logger = logging.getLogger(".".join(modules))
    logger.setLevel(logging.DEBUG)

    console_format = VERBOSE_FORMAT if verbose else DEFAULT_FORMAT

    # pylint: disable=invalid-name
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(console_format)
    logger.addHandler(sh)

    if log_dir is not None:
        aether_log = join(log_dir, log_file)

        # Delete server log if it reaches 250 kB
        if exists(aether_log) and getsize(aether_log) > 250000:
            with open(aether_log, "r") as f:
                log = f.readlines()
                print(len(log))
                line_start = int(len(log) / 2)
                new_log = log[line_start:]
            with open(aether_log, "w+") as f:
                f.write("".join(new_log))

        fh = logging.FileHandler(aether_log)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(console_format)
        logger.addHandler(fh)

    logger.propagate = False

    return logger
