"""
Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
Date: 2023-09-06 17:52:32
LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
LastEditTime: 2023-09-06 17:55:09
FilePath: /yi_4kplus_for_klipper/yi_4k_plus/__init__.py
Description: 入口文件
jdiaan@163.com
Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629 All Rights Reserved.
"""
from . import yi_4k_plus


def load_config_prefix(config):
    """
    加载主要的配置
    """
    return yi_4k_plus.load_config(config)
