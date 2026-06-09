"""
utils/logger.py
===============
ระบบ Logging สำหรับทั้ง Bot
"""

import logging
import os
from datetime import datetime
from config.settings import LOG_LEVEL, LOG_TO_FILE, LOG_DIR


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    fmt = "%(asctime)s [%(name)-14s] %(levelname)-8s %(message)s"
    datefmt = "%H:%M:%S"

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(fmt, datefmt))
    logger.addHandler(ch)

    # File handler
    if LOG_TO_FILE:
        os.makedirs(LOG_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        fh = logging.FileHandler(f"{LOG_DIR}/nexus_{today}.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter(fmt, datefmt))
        logger.addHandler(fh)

    return logger
