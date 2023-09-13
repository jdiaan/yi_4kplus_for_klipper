"""
Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
Date: 2023-09-06 21:51:39
LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
LastEditTime: 2023-09-07 14:17:58
FilePath: \yi_4kplus_for_klipper\yi_4k_plus\image_proc.py
Description: 图像处理
jdiaan@163.com
Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629, All Rights Reserved.
"""
import time
import os
import subprocess

import exifread

from . import log


def get_ffmpeg_concat(
    img_file_list: list, min_time: int = 0.2, max_time: int = 0.4, last_img_time=0.5
) -> str:
    """
    从图像列表里获取时间戳,制作成ffmpeg concat 的文件格式

    :param img_file_list: list,
    :param min_time: int, 映射的最短时间
    :param max_time: int, 映射的最长时间
    :param last_img_time: int, 最后一帧持续时间
    :return: str
    """
    __concat_ls = []
    real_min_time = None
    real_max_time = None

    __last_time_stamp = None
    for index, file_path in enumerate(img_file_list):
        # img_name = os.path.basename(file_path)
        if not os.path.exists(file_path):
            continue

        img = exifread.process_file(open(file_path, "rb"))

        if "EXIF DateTimeOriginal" not in img:
            continue
        img_time = img["EXIF DateTimeOriginal"]
        img_time_array = time.strptime(str(img_time), "%Y:%m:%d %H:%M:%S")
        img_time_stamp = int(time.mktime(img_time_array))

        if __last_time_stamp is not None:
            delta = img_time_stamp - __last_time_stamp
            __concat_ls.append(delta)

            # 修改实际的最大最小间隔
            if real_max_time is None:
                real_max_time = delta
            elif delta < real_min_time:
                real_min_time = delta

            if real_min_time is None:
                real_min_time = delta
            elif delta > real_max_time:
                real_max_time = delta
            # ffmpeg_concat_text += f"duration {}\n"

        __concat_ls.append(file_path)

        if index == len(img_file_list) - 1:
            __concat_ls.append(last_img_time)
            __concat_ls.append(file_path)
            # ffmpeg_concat_text += f"duration {last_img_time}\nfile '{file_path}'\n"

        __last_time_stamp = img_time_stamp

    # 更改实际的最大最小值
    if min_time is None:
        min_time = real_min_time
    if max_time is None:
        max_time = real_max_time

    ffmpeg_concat_text = ""
    for index, item in enumerate(__concat_ls):
        if index % 2 == 0:
            ffmpeg_concat_text += f"file '{item}'\n"

        else:
            if index == len(__concat_ls) - 2:  # 最后一帧
                real_time = item
            elif real_min_time == real_max_time:
                real_time = (max_time - min_time) / 2
            else:
                nor_time = (item - real_min_time) / (real_max_time - real_min_time)
                real_time = nor_time * (max_time - min_time) + min_time

            ffmpeg_concat_text += f"duration {real_time}\n"

    return ffmpeg_concat_text


def create_ffmpeg_concat_file(ffmpeg_concat_text: str, out_file_path: str) -> None:
    """
    生成ffmpeg concat 文件

    :param ffmpeg_concat_text: str,
    :param out_file_path: str,
    :return: None
    """
    with open(out_file_path, "w", encoding="utf-8") as file:
        file.write(ffmpeg_concat_text)
    log.LOGGER.debug("concat文件路径:%s", out_file_path)


def img_2_video_by_concat(
    ffmpeg_path: str,
    out_file_path: str,
    concat_file_path: str,
    video_fps=25,
    video_resolution: tuple = (1200, 900),
) -> bool:
    """
    将图片列表合称为视频

    :param ffmpeg_path: str,
    :param out_file_path: str,
    :param concat_file_path: str,
    :param video_fps: int, 视频渲染帧率
    :param video_resolution: (int,int), 视频渲染分辨率宽*高
    :return: bool
    """

    ffmpeg_cmd = [
        ffmpeg_path,
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file_path,
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-vf",
        f"scale={video_resolution[0]}:{video_resolution[1]},fps={str(video_fps)}",
        out_file_path,
    ]

    log.LOGGER.debug("准备渲染:%s", out_file_path)

    popen = subprocess.Popen(
        ffmpeg_cmd,
        shell=False,
    )

    _re = popen.wait()
    log.LOGGER.debug("视频文件路径:%s", out_file_path)
    if _re == 0:
        return True

    return False


def remove_im_gfiles(img_file_list: list) -> None:
    """
    删除文件

    :param img_file_list: list,
    :return: None
    """
    for file in img_file_list:
        if os.path.exists(file):
            os.remove(file)
