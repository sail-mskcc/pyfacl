import logging


def logger_basic(name: str, v: int = 0) -> logging.Logger:
    """
    Set up and return a logger with the specified name and logging level.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (default is logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """

    level = logging.INFO if v == 0 else logging.DEBUG
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger


def logger_print(v: int = 0) -> logging.Logger:
    """
    Set up a print logger without a specific name or other configurations.

    Args:
        v (int): Verbosity level (0 for INFO, 1 for DEBUG).

    Returns:
        logging.Logger: Configured logger instance.
    """
    level = logging.WARNING if v == 0 else logging.DEBUG
    logger = logging.getLogger("print_logger")
    logger.setLevel(level)

    if not logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = logging.Formatter("%(message)s")
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger
