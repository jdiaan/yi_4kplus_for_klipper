"""
Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
Date: 2023-09-06 21:58:30
LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
LastEditTime: 2023-09-06 21:59:44
FilePath: /yi_4kplus_for_klipper/test/test.py
Description: 测试相机，这是一个线性工作的脚本
jdiaan@163.com
Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629, All Rights Reserved.
"""
import os
import sys
import time
import random
import logging

# 自己想办法创建环境，谢谢
from yi_4k_plus import camera_api
from yi_4k_plus import image_proc

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 相机实例化
    cam_ip = "192.168.1.10"
    cam = camera_api.CameraAPI(ip=cam_ip)
    is_con = cam.connect(attempts=3)

    if not is_con:
        sys.exit(1)  # 直接异常退出

    # 相机更改模式
    cam.change_mode(cam.MODE_PHOTO)

    # 随机时间拍照
    last_time = time.time()
    number = 0
    while time.time() - last_time < 20:
        cam.take_photo()
        number += 1
        time.sleep(random.randint(1, 10))

    # 获取刚刚拍摄的照片文件列表，获取完后会清空这个缓存
    photp_save_ls = cam.get_photo_files(number)

    # 断开
    cam.disconnect()

    # 连接ftp
    ftp = camera_api.CameraFtp(ip=cam_ip)
    is_con = ftp.connect()

    if not is_con:
        sys.exit(1)

    # 下载刚刚获取到的文件列表中的文件，因为为了在klipper中实现，所以api用了多线程，防止klipper重启
    local_file_ls = []
    for photo_file in photp_save_ls:
        photo_file = photo_file.split("fuse_d")[1]
        local_file = os.path.join(
            os.path.dirname(__file__), "test_img", os.path.basename(photo_file)
        )
        local_file_ls.append(local_file)

        print(photo_file + " -> " + local_file)
        ftp.download_file(local_file, photo_file)
        # time.sleep(1)

    # 等待下载完成
    print("开始下载")
    while not ftp.is_download_complete():
        print("下载中...")
        time.sleep(2)

    ftp.disconnect()

    # 合成视频的准备工作
    out_dir = os.path.dirname(__file__)
    out_img_dir = os.path.join(out_dir, "test_img")
    concat_file_path = os.path.join(out_img_dir, "concat.txt")
    ffmpeg_file_path = "ffmpeg.exe"  # 不提供此文件，自行下载！！！
    video_file_path = os.path.join(out_img_dir, "test.mp4")

    # 创建concat文件
    concat_text = image_proc.get_ffmpeg_concat(
        local_file_ls, min_time=3 / 25, max_time=20 / 25, last_img_time=5 / 25
    )
    image_proc.create_ffmpeg_concat_file(concat_text, concat_file_path)

    # 渲染
    is_success = image_proc.img_2_video_by_concat(
        ffmpeg_file_path, video_file_path, concat_file_path
    )

    # 删除文件
    if is_success:
        image_proc.remove_im_gfiles(local_file_ls)
        image_proc.remove_im_gfiles([concat_file_path])

    print("结束")
