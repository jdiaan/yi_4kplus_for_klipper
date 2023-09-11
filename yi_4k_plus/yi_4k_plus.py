"""
Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
Date: 2023-09-06 21:51:39
LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
LastEditTime: 2023-09-07 16:06:46
FilePath: /yi_4kplus_for_klipper/yi_4k_plus/yi_4k_plus.py
Description: klipper插件
jdiaan@163.com
Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629, All Rights Reserved.
"""
import os
import time
import datetime
import threading


from . import setting
from . import camera_api
from . import image_proc
from . import log


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
        log_path = config.get("log_path")
        log_level = config.get("log_level", "info")

        self.port = config.getint("port", 7878)

        resolution = config.get("resolution", "12MP (4000x3000 4:3) fov:w")
        shutter = config.get("shutter", "auto")
        meter = config.get("meter", "center")
        wb = config.get("wb", "5500k")
        color = config.get("color", "flat")
        iso_min = config.get("iso_min", "100")
        iso = config.get("iso", "400")
        sharpness = config.get("sharpness", "medium")
        ev = config.get("ev", "0")
        stamp = config.get("stamp", "off")
        quick_view = config.get("quick_view", "off")
        file_type = config.get("file_type", "jpg")

        # log
        log.LOGGER = log.create_log(
            log_out_path=os.path.expanduser(log_path), log_level=log_level
        )

        __setting = setting.Setting
        self.photo_setting_dict = {
            __setting.photo_size: resolution,
            __setting.iq_photo_shutter: shutter,
            __setting.meter_mode: meter,
            __setting.iq_photo_wb: wb,
            __setting.photo_flat_color: color,
            __setting.iq_photo_iso_min: iso_min,
            __setting.iq_photo_iso: iso,
            __setting.photo_sharpness: sharpness,
            __setting.iq_photo_ev: ev,
            __setting.photo_stamp: stamp,
            __setting.quick_view: quick_view,
            __setting.photo_file_type: file_type,
        }

        # 解析参数,解析参数错误用 raise config.error("my error")
        for key, value in self.photo_setting_dict.items():
            if key in setting.photo_setting:
                if value not in setting.photo_setting[key]:
                    raise config.error(f"参数{key}错误:{value}")

        # 添加参数
        self.print_stats = self.printer.load_object(config, "print_stats")
        gcode = self.printer.lookup_object("gcode")

        gcode.register_command(
            "YI_TAKE_PHOTO",
            self.cmd_yi_take_photo,
            desc=self.cmd_YI_TAKE_PHOTO_help,
        )

        gcode.register_command(
            "YI_CONNECT_CAMERA",
            self.cmd_yi_connect_camera,
            desc=self.cmd_YI_CONNECT_CAMERA_help,
        )

        gcode.register_command(
            "YI_DISCONNECT_CAMERA",
            self.cmd_yi_disconnect_camera,
            desc=self.cmd_YI_DISCONNECT_CAMERA_help,
        )

        gcode.register_command(
            "YI_DOWNOLD",
            self.cmd_yi_download,
            desc=self.cmd_YI_DOWNLOAD_help,
        )

        gcode.register_command(
            "YI_GET_PHOTO_OPTIONS",
            self.cmd_yi_get_photo_options,
            desc=self.cmd_YI_GET_PHOTO_OPTIONS_help,
        )

        gcode.register_command(
            "_YI_RENDER_VIDEO",
            self.cmd_yi_render_video,
            desc=self.cmd_YI_RENDER_VIDEO_help,
        )

        # 创建变量
        self.printer.add_object("yi_4k+_img_path_object", Img(config))

        CameraForKlipper.CAMERA_DICT[self.cam_name] = CameraControl(
            config=config, ip=self.ip, port=self.port, camera_name=self.cam_name
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
        gcmd.respond_info(_re)

    cmd_YI_CONNECT_CAMERA_help = "connect camera"

    def cmd_yi_connect_camera(self, gcmd):
        """
        连接相机
        """
        cam_n = gcmd.get("name", "ALL")

        if cam_n == "ALL":
            for can in CameraForKlipper.CAMERA_DICT.values():
                can.connect()
                can.change_photo_settings(self.photo_setting_dict)

        else:
            # is_con = False
            if cam_n in CameraForKlipper.CAMERA_DICT:
                CameraForKlipper.CAMERA_DICT[cam_n].connect()
                CameraForKlipper.CAMERA_DICT[cam_n].change_photo_settings(
                    self.photo_setting_dict
                )

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
        now = datetime.datetime.now()
        now_time = now.strftime("timelapse_%Y%m%d_%H%M%S.mp4")
        if not p_name:
            file_name = now_time
        else:
            file_name = f"yi_timelapse_{os.path.splitext(p_name)[0]}_{now_time}.mp4"

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

    def __init__(self, config, ip, port, camera_name) -> None:
        self.__name = camera_name
        self.__ip = ip
        self.__port = port

        self.__printer = config.get_printer()
        self.__gcode = self.__printer.lookup_object("gcode")
        self.__img_obj = self.__printer.load_object(config, "yi_4k+_img_path_object")

        self.__api = camera_api.CameraAPI(self.__ip, self.__port)
        self.__ftp = camera_api.CameraFtp(self.__ip)

        self.__is_con_cam = False
        # self.__is_con_ftp = False

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

    def download_photo(self, out_dir: str) -> None:
        """
        下载本次拍摄的照片

        :param out_dir: str, 输出地址
        """
        photo_ls = self.__api.get_photo_files(file_number=0)
        if photo_ls:
            log.LOGGER.debug("需要下载的图片：%s", photo_ls)
        else:
            log.LOGGER.debug("没有照片需要下载")
            return

        # if self.__is_con_ftp:
        for photo in photo_ls:
            photo = photo.split("fuse_d")[1]
            photo_old_n = os.path.basename(photo)
            photo_new_n = (
                f"{self.__name}_{self.__img_obj.get_img_number(self.__name)}"
                f"{os.path.splitext(photo_old_n)[1]}"
            )

            local_img_path = os.path.join(out_dir, photo_new_n)
            self.__img_obj.add_img_path(self.__name, local_img_path)

            log.LOGGER.info("准备下载%s=>%s", photo, local_img_path)
            self.__ftp.download_file(local_img_path, photo)
        # else:
        #     self.__gcode.respond_info(f"由于无法连接到相机{self.__name}的ftp服务，因此无法下载图片")

    def img_to_video(self, ffmpeg_path: str, out_dir: str, video_name: str) -> None:
        """
        合成视频，多线程

        :param ffmpeg_path: str, ffmpeg路径
        :param out_file: str, 输出文件夹
        :param out_file: str, 视频名称包括后缀
        :return: None
        """
        thread = threading.Thread(
            target=self.__img_to_video,
            kwargs={
                "ffmpeg_path": ffmpeg_path,
                "out_dir": out_dir,
                "video_name": video_name,
            },
            daemon=False,
        )
        thread.start()

    def __img_to_video(self, **kwargs) -> None:
        """
        图片合成视频

        :param ffmpeg_path: str, ffmpeg路径
        :param out_file: str, 输出文件夹
        :param out_file: str, 视频名称包括后缀
        :return: None
        """
        ffmpeg_path = kwargs["ffmpeg_path"]
        out_dir = kwargs["out_dir"]
        video_name = kwargs["video_name"]

        while not self.__ftp.is_download_complete():
            time.sleep(2)

        log.LOGGER.info("图片全部下载完成")

        out_dir = os.path.expanduser(out_dir)

        concat_file_path = os.path.join(out_dir, f"concat-{video_name}.txt")
        video_file_path = os.path.join(out_dir, video_name)

        concat_text = image_proc.get_ffmpeg_concat(
            self.__img_obj.get_imgs_path(self.__name),
            min_time=3 / 25,
            max_time=20 / 25,
            last_img_time=5 / 25,
        )
        image_proc.create_ffmpeg_concat_file(concat_text, concat_file_path)

        # render
        is_success = image_proc.img_2_video_by_concat(
            ffmpeg_path, video_file_path, concat_file_path
        )

        if is_success:
            image_proc.remove_im_gfiles(self.__img_obj.get_imgs_path(self.__name))
        image_proc.remove_im_gfiles([concat_file_path])
        self.__img_obj.clean_img_path(self.__name)

        log.LOGGER.info("渲染完成")

    def change_photo_settings(self, setting_dict):
        """
        设置相机拍照参数
        """
        for key, value in setting_dict.items():
            self.__api.set_setting(key, value)


class Img:
    """
    存储img path
    """

    def __init__(self, config) -> None:
        self.__config = config

        self.__img_path_dixt = {}

    def get_imgs_path(self, camera_name: str) -> list:
        """
        获得保存的图片列表
        """
        _re = None
        if camera_name in self.__img_path_dixt:
            _re = self.__img_path_dixt[camera_name]

        return _re

    def add_img_path(self, camera_name: str, img_path: str) -> None:
        """
        添加图片
        """
        if camera_name not in self.__img_path_dixt:
            self.__img_path_dixt[camera_name] = []
        self.__img_path_dixt[camera_name].append(img_path)

    def clean_img_path(self, camera_name: str) -> None:
        """
        删除图片
        """
        if camera_name in self.__img_path_dixt:
            del self.__img_path_dixt[camera_name]

    def get_img_number(self, camera_name: str) -> int:
        """
        获取图片数量
        """
        _re = 0
        if camera_name in self.__img_path_dixt:
            _re = len(self.__img_path_dixt[camera_name])

        return _re


def load_config(config):
    """
    应该是用来加载的函数,作为klipper插件必须要有
    """
    return CameraForKlipper(config)
