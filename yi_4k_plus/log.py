"""
Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
Date: 2023-09-07 17:18:20
LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
LastEditTime: 2023-09-07 17:19:49
FilePath: /yi_4kplus_for_klipper/yi_4k_plus/log.py
Description: 自己用的log
jdiaan@163.com
Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629, All Rights Reserved.
"""
import logging


def create_log(
    log_out_path: str = None, log_name: str = "yi4k+", log_level: str = "debug"
):
    """
    创建logger
    """
    if log_level == "debug":
        __log_level = logging.DEBUG
    elif log_level == "warning":
        __log_level = logging.WARNING
    elif log_level == "error":
        __log_level = logging.ERROR
    elif log_level == "critical":
        __log_level = logging.CRITICAL
    else:
        __log_level = logging.INFO

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    logger = logging.getLogger(log_name)
    logger.setLevel(__log_level)

    console_hander = logging.StreamHandler()
    console_hander.setFormatter(formatter)
    logger.addHandler(console_hander)
    console_hander.setLevel(logging.DEBUG)

    if log_out_path:
        file_hander = logging.FileHandler(log_out_path, encoding="utf-8", mode="a")
        file_hander.setFormatter(formatter)
        logger.addHandler(file_hander)
        file_hander.setLevel(logging.DEBUG)

    return logger


LOGGER = create_log(log_name="yi4k+_main")
