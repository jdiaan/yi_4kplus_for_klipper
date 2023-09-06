'''
Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
Date: 2023-09-06 21:51:39
LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
LastEditTime: 2023-09-06 21:57:26
FilePath: /yi_4kplus_for_klipper/yi_4k_plus/yi_4k_plus.py
Description: klipper插件
jdiaan@163.com
Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629, All Rights Reserved.
'''
import os
import datetime


from . import setting
from . import camera_api
from . import image_proc


class CameraForKlipper:
    """
    关于camera的操作脚本
    """

    CAMERA_DICT = {}

    def __init__(self, config):
        self.printer = config.get_printer()
        # 获取名称
        self.cam_name = config.get_name().split()[-1]

        # 获取配置
        self.ip = config.get("ip")
        self.output_path = config.get("output_path")  # 延迟视频输出位置
        self.frame_path = config.get("frame_path", "/tmp/yi4kplus")  # tmp
        self.ffmpeg_binary_path = config.get("ffmpeg_binary_path", "/usr/bin/ffmpeg")

        self.port = config.getint("port", 7878)
        self.resolution = config.get("resolution", "12MP (4000x3000 4:3) fov:w")
        self.shutter = config.get("shutter", "auto")
        self.meter = config.get("meter", "center")
        self.wb = config.get("wb", "5500k")
        self.color = config.get("color", "flat")
        self.iso_min = config.getint("iso_min", 100)
        self.iso = config.getint("iso", 400)
        self.sharpness = config.get("sharpness", "medium")
        self.ev = config.get("ev", "0")
        self.stamp = config.get("stamp", "off")
        self.quick_view = config.get("quick_view", "off")
        self.file_type = config.get("file_type", "jpg")

        self.print_stats = self.printer.load_object(config, "print_stats")
        # 解析参数错误用 raise config.error("my error")

        # 添加参数
        self.gcode = self.printer.lookup_object("gcode")

        self.gcode.register_command(
            "YI_TAKE_PHOTO",
            self.cmd_yi_take_photo,
            desc=self.cmd_YI_TAKE_PHOTO_help,
        )

        self.gcode.register_command(
            "YI_CONNECT_CAMERA",
            self.cmd_yi_connect_camera,
            desc=self.cmd_YI_CONNECT_CAMERA_help,
        )

        self.gcode.register_command(
            "YI_DISCONNECT_CAMERA",
            self.cmd_yi_disconnect_camera,
            desc=self.cmd_YI_DISCONNECT_CAMERA_help,
        )

        self.gcode.register_command(
            "YI_DOWNOLD",
            self.cmd_yi_download,
            desc=self.cmd_YI_DOWNLOAD_help,
        )

        self.gcode.register_command(
            "YI_GET_PHOTO_OPTIONS",
            self.cmd_yi_get_photo_options,
            desc=self.cmd_YI_GET_PHOTO_OPTIONS_help,
        )

        self.gcode.register_command(
            "_YI_RENDER_VIDEO",
            self.cmd_yi_render_video,
            desc=self.cmd_YI_RENDER_VIDEO_help,
        )

        # 创建变量
        CameraForKlipper.CAMERA_DICT[self.cam_name] = CameraControl(
            ip=self.ip, port=self.port, camera_name=self.cam_name, gcode=self.gcode
        )

    # def get_status(self, eventtime):
    #     return self.fan.get_status(eventtime)
    cmd_YI_TAKE_PHOTO_help = "take photo"

    def cmd_yi_take_photo(self, gcmd):
        """
        拍摄的命令
        """
        cam_n = gcmd.get("name", "ALL")

        if cam_n == "ALL":
            for can in CameraForKlipper.CAMERA_DICT.values():
                can.take_photo()
        else:
            if cam_n in CameraForKlipper.CAMERA_DICT:
                CameraForKlipper.CAMERA_DICT[cam_n].take_photo()

    cmd_YI_GET_PHOTO_OPTIONS_help = "get photo setting options"

    def cmd_yi_get_photo_options(self, gcmd):
        """
        获取拍档参数
        """
        _re = f"""YI 4K +:摄像参数
resolution-分辨率:{str(setting.photo_setting[setting.Setting.photo_size])}
shutter-快门速度:{str(setting.photo_setting[setting.Setting.iq_photo_shutter])}
meter-测光模式:{str(setting.photo_setting[setting.Setting.meter_mode])}
wb-白平衡:{str(setting.photo_setting[setting.Setting.iq_photo_wb])}
color-色彩模式:{str(setting.photo_setting[setting.Setting.photo_flat_color])}
iso_min-最小感光度:{str(setting.photo_setting[setting.Setting.iq_photo_iso_min])}
iso-最大感光度:{str(setting.photo_setting[setting.Setting.iq_photo_iso])}
sharpness-锐度:{str(setting.photo_setting[setting.Setting.photo_sharpness])}
ev-曝光补偿:{str(setting.photo_setting[setting.Setting.iq_photo_ev])}
stamp-时间戳:{str(setting.photo_setting[setting.Setting.photo_stamp])}
quick_view-QuickView:{str(setting.photo_setting[setting.Setting.quick_view])}
file_type-文件格式:{str(setting.photo_setting[setting.Setting.photo_file_type])}
"""
        self.gcode.respond_info(_re)

    cmd_YI_CONNECT_CAMERA_help = "connect camera"

    def cmd_yi_connect_camera(self, gcmd):
        """
        连接相机
        """
        cam_n = gcmd.get("name", "ALL")

        if cam_n == "ALL":
            for can in CameraForKlipper.CAMERA_DICT.values():
                can.connect()

        else:
            # is_con = False
            if cam_n in CameraForKlipper.CAMERA_DICT:
                CameraForKlipper.CAMERA_DICT[cam_n].connect()

    cmd_YI_DISCONNECT_CAMERA_help = "disconnect camera"

    def cmd_yi_disconnect_camera(self, gcmd):
        """
        断开连接
        """
        cam_n = gcmd.get("name", "ALL")

        if cam_n == "ALL":
            for can in CameraForKlipper.CAMERA_DICT.values():
                can.disconnect()

        else:
            if cam_n in CameraForKlipper.CAMERA_DICT:
                CameraForKlipper.CAMERA_DICT[cam_n].disconnect()

    cmd_YI_DOWNLOAD_help = "download camera files"

    def cmd_yi_download(self, gcmd):
        """
        从相机下载文件
        """
        cam_n = gcmd.get("name", "ALL")

        if cam_n == "ALL":
            for can in CameraForKlipper.CAMERA_DICT.values():
                can.download_photo(self.frame_path)

        else:
            if cam_n in CameraForKlipper.CAMERA_DICT:
                CameraForKlipper.CAMERA_DICT[cam_n].download_photo(self.frame_path)

    cmd_YI_RENDER_VIDEO_help = "render video"

    def cmd_yi_render_video(self, gcmd):
        """
        视频渲染
        """
        cam_n = gcmd.get("name", "ALL")

        p_name = self.print_stats.filename
        if not p_name:
            now = datetime.datetime.now()
            file_name = now.strftime("timelapse_%Y%m%d_%H%M%S.mp4")
        else:
            file_name = "yi_timelapse_" + os.path.splitext(p_name)[0]

        if cam_n == "ALL":
            for can in CameraForKlipper.CAMERA_DICT.values():
                can.img_to_video(self.ffmpeg_binary_path, self.output_path, file_name)

        else:
            if cam_n in CameraForKlipper.CAMERA_DICT:
                CameraForKlipper.CAMERA_DICT[cam_n].img_to_video(
                    self.ffmpeg_binary_path, self.output_path, file_name
                )


class CameraControl:
    """
    相机控制
    """

    def __init__(self, ip, port, camera_name, gcode) -> None:
        self.__name = camera_name
        self.__ip = ip
        self.__port = port
        self.__gcode = gcode

        self.__api = camera_api.CameraAPI(self.__ip, self.__port)
        self.__ftp = camera_api.CameraFtp(self.__ip)

        self.__photo_number = 0
        self.__photo_ls = []
        self.__is_con_cam = False
        self.__is_con_ftp = False

    def cam_init(self) -> None:
        """
        相机初始化
        """
        self.__api.set_setting("auto_power_off", "off")

        now = datetime.datetime.now()
        self.__api.set_setting("camera_clock", now.strftime("%Y-%m-%d %H:%M:%S"))

        self.__api.change_mode(self.__api.MODE_PHOTO)

    def connect(self) -> None:
        """
        连接
        """
        self.__is_con_cam = self.__api.connect()
        if not self.__is_con_cam:
            self.__gcode.respond_info(f"相机{self.__name}无法连接")

        self.__is_con_ftp = self.__ftp.connect()
        if not self.__is_con_ftp:
            self.__gcode.respond_info(f"相机{self.__name}无法连接到ftp服务器,会导致无法使用下载服务")

        self.cam_init()

        return True

    def disconnect(self) -> None:
        """
        断开
        """
        self.__ftp.disconnect()
        if self.__is_con_cam:
            self.__api.disconnect()

    def take_photo(self) -> None:
        """
        拍照
        """
        if self.__is_con_cam:
            self.__api.take_photo()

            self.__photo_number += 1

    def download_photo(self, out_dir: str) -> None:
        """
        下载本次拍摄的照片

        :param out_dir: str, 输出地址
        """
        photo_ls = self.__api.get_photo_files(self.__photo_number)

        if self.__is_con_ftp:
            for photo in photo_ls:
                photo = photo.split("fuse_d")[1]
                photo_n = os.path.basename(photo)

                local_img_path = os.path.join(out_dir, photo_n)
                self.__photo_ls.append(local_img_path)
                self.__ftp.download_file(local_img_path, photo)
        else:
            print(f"由于无法连接到相机{self.__name}的ftp服务，因此无法下载图片")

    def img_to_video(self, ffmpeg_path: str, out_dir: str, video_name: str) -> None:
        """
        图片合成视频

        :param ffmpeg_path: str, ffmpeg路径
        :param out_file: str, 输出文件夹
        :param out_file: str, 视频名称包括后缀
        :return: None
        """
        out_dir = os.path.expanduser(out_dir)

        concat_file_path = os.path.join(out_dir, f"concat-{video_name}.txt")
        video_file_path = os.path.join(out_dir, video_name)

        concat_text = image_proc.get_ffmpeg_concat(
            self.__photo_ls, min_time=3 / 25, max_time=20 / 25, last_img_time=5 / 25
        )
        image_proc.create_ffmpeg_concat_file(concat_text, concat_file_path)

        # render
        is_success = image_proc.img_2_video_by_concat(
            ffmpeg_path, video_file_path, concat_file_path
        )

        if is_success:
            image_proc.remove_im_gfiles(self.__photo_ls)
        image_proc.remove_im_gfiles([concat_file_path])
        self.__photo_ls = []


def load_config(config):
    """
    应该是用来加载的函数,作为klipper插件必须要有
    """
    return CameraForKlipper(config)
