"""
Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
Date: 2023-09-06 21:51:39
LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
LastEditTime: 2023-09-07 15:51:18
FilePath: /yi_4kplus_for_klipper/yi_4k_plus/camera_api.py
Description: 操控相机的api
jdiaan@163.com
Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629, All Rights Reserved.
"""
import os
import socket
import json
import time
import threading
import traceback
import ftplib
import telnetlib
import queue

from . import log

logging = log.LOGGER


class CameraAPI:
    """
    摄像头控制,
    相机使用安霸芯片,关于安霸芯片
    https://www.rigacci.org/wiki/doku.php/doc/appunti/hardware/sjcam-8pro-ambarella-wifi-api
    """

    AMBA_START_SESSION = 257  # 获取初始会话令牌
    AMBA_STOP_SESSION = 258  # 终止会话
    AMBA_GET_SETTING = 1  # 获取单个相机设置的值
    AMBA_SET_SETTING = 2  # 设置相机设置的值
    AMBA_GET_ALL_CURRENT_SETTINGS = 3  # 获取当前相机设置
    AMBA_GET_SPACE = 5  # 获得卡空间，总计和剩余
    AMBA_NOTIFICATION = 7  # 通知消息
    AMBA_GET_SINGLE_SETTING_OPTIONS = 9  # 获取某项参数有哪些可以设置的值
    AMBA_GET_DEVICEINFO = 11  # 获取相机品牌，型号，固件和API版本等
    # AMBA_CAMERA_OFF = 12  # 关闭相机电源
    AMBA_GET_BATTERY_LEVEL = 13  # 获取电源状态和电池电量百分比
    AMBA_BOSS_RESETVF = 259  # 用端口 554/TCP 上的 RTSP 从摄像机启动视频流
    AMBA_STOP_VF = 260  # 停止端口 554/TCP 上的视频流
    AMBA_RECORD_START = 513  # 开始录制
    AMBA_RECORD_STOP = 514  # 停止录制
    AMBA_GET_RECORD_TIME = 515  # 获取当前录制长度
    AMBA_TAKE_PHOTO = 769  # 拍照
    # AMBA_GET_CURRENT_MODE_SETTINGS = 2053  # 获取当前模式（视频、照片等）设置
    # AMBA_SET_WIFI = 2055  # 更改 WiFi 连接参数

    MODE_PHOTO = "precise quality"
    MODE_TIMELAPSE_PHOTO = "precise quality cont."
    MODE_CONTINUOUS_PHOTO = "burst quality"
    MODE_DELAYED_PHOTO = "precise self quality"

    MODE_RECORD = "record"
    MODE_TIMELAPSE_RECORD = "record_timelapse"
    MODE_LOOP_RECORD = "record_loop"
    MODE_PHOTO_RECORD = "record_photo"
    MODE_SLOW_RECORD = "record_slow_motion"

    def __init__(self, ip, port=7878) -> None:
        self.__ip = ip
        self.__port = port

        self.__token = None
        self.__rtsp = None
        self.__sock = None
        self.__recv_thread = None
        self.__recv_event = threading.Event()
        self.__send_thread = None
        self.__send_queue = queue.Queue()
        self.__send_event = threading.Event()

        self.__data_ls = None
        self.__temp_data = ""
        self.__is_con = False
        self.__video_save_path = None
        self.__photo_data_ls = []
        self.__photo_data_lock = threading.Lock()

    def __del__(self) -> None:
        if self.__is_con:
            try:
                self.disconnect()
                self.__sock.close()
                logging.info("自动关闭连接")
            except Exception:
                logging.debug("del无法正常关闭socket,可能是已经关闭了")

        self.__sock = None
        self.__recv_event.set()
        self.__send_event.set()

    def connect(
        self, time_out: int = 10, attempts: int = 10, heartbeat: int = None
    ) -> bool:
        """
        连接相机

        :param time_out: int, 连接超时时长
        :param attempts: int, 尝试重连次数
        :param msg_id: int, 心跳
        :return: bool 是否成功
        """
        if self.__is_con:
            return True

        # 连接socket
        is_con = False
        _start_times = 0
        for i in range(attempts):
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.settimeout(time_out)
            try:
                logging.debug("准备连接相机%s:%d", self.__ip, self.__port)
                self.__sock.connect((self.__ip, self.__port))
                is_con = True
                break
            except TimeoutError:
                logging.debug("连接socket超时")
            except Exception:
                logging.debug("连接失败,错误信息:\n%s", traceback.format_exc())

            _start_times += 1
            logging.warning("连接失败,准备第%d次重试,共%d次", i + 1, attempts)
            time.sleep(0.1)

        if is_con:
            logging.debug("连接相机socket成功,ip:%s", self.__ip)
        else:
            logging.error("连接相机失败,ip:%s", self.__ip)
            return False

        # 创建接收线程
        if not isinstance(self.__recv_thread, threading.Thread):
            self.__recv_event.clear()
            self.__recv_thread = threading.Thread(target=self.__recv_run)
            self.__recv_thread.daemon = True
            self.__recv_thread.start()

        # 创建发送线程
        if not isinstance(self.__send_thread, threading.Thread):
            self.__send_event.clear()
            self.__send_thread = threading.Thread(target=self.__send_run)
            self.__send_thread.daemon = True
            self.__send_thread.start()

        # 发送连接指令并接收消息
        data = None
        for i in range(_start_times, attempts):
            if heartbeat:
                send_data = self.__get_send_data(
                    self.AMBA_START_SESSION, token=0, heartbeat=heartbeat
                )
            else:
                send_data = self.__get_send_data(self.AMBA_START_SESSION, token=0)
            self.__send_queue.put(send_data)

            # 接收消息
            data = self.__get_data(self.AMBA_START_SESSION)[0]
            if data:
                break
            logging.warning("连接失败,准备第%d次重试,共%d次", i + 1, attempts)
            time.sleep(0.5)

        if data:
            logging.info("连接相机成功!ip:%s", self.__ip)
        else:
            logging.error("连接相机失败,ip:%s", self.__ip)
            return False

        # 处理
        self.__token = data["param"]

        _rtsp_ls = data["rtsp"].split("/")
        _rtsp_ls[2] = self.__ip
        self.__rtsp = ""
        for i, obj in enumerate(_rtsp_ls):
            self.__rtsp += obj
            if i != len(_rtsp_ls) - 1:
                self.__rtsp += "/"
        logging.debug("rtsp服务器为:%s", self.__rtsp)

        self.__is_con = True
        return True

    def disconnect(self) -> bool:
        """
        断开连接

        :return: bool 是否成功
        """
        send_data = self.__get_send_data(self.AMBA_STOP_SESSION)
        self.__send_queue.put(send_data)

        self.__token = None
        self.__rtsp = None

        # 接收
        data = self.__get_data(msgid=self.AMBA_STOP_SESSION)[0]

        # 处理
        if self.__is_success_run(data):
            logging.info("成功断开连接")
        else:
            logging.info("断开连接")

        self.__is_con = False
        return True

    def get_all_setting(self) -> dict:
        """
        获取当前所有的设置

        :return: dict
        """
        send_data = self.__get_send_data(self.AMBA_GET_ALL_CURRENT_SETTINGS)
        self.__send_queue.put(send_data)

        # 接收
        data = self.__get_data(msgid=self.AMBA_GET_ALL_CURRENT_SETTINGS)[0]

        # 处理
        param = self.__get_param(data)

        logging.info("相机所有参数为:%s", param)

        return data

    def get_setting(self, _type: str) -> object:
        """
        获取单个值

        :param _type: str, 参数
        :return: object, 返回None 则为没有这个属性
        """
        send_data = self.__get_send_data(self.AMBA_GET_SETTING, type=str(_type))
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_GET_SETTING)[0]

        param = self.__get_param(data)
        if param is None:
            logging.error("相机没有%s参数", _type)
        else:
            logging.info("相机参数%s值为:%s", _type, param)

        return param

    def set_setting(self, key: str, value: str) -> bool:
        """
        设置单一值

        :param key: str, 参数
        :param value: str, 值
        :return: bool
        """
        _re = False
        send_data = self.__get_send_data(
            self.AMBA_SET_SETTING, type=str(key), param=str(value)
        )
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_SET_SETTING)[0]

        param = self.__get_param(data)
        _type = self.__get_type(data)
        if param is None:
            logging.error("相机没有%s参数", key)
        else:
            logging.info("参数%s值为:%s", _type, param)
            _re = True

        return _re

    def get_sd_space(self, is_total: bool = False) -> int:
        """
        获取卡的空间

        :param msg_id: bool, 是否是总的空间。如果是False,则查询剩余空间
        :return: int
        """
        if is_total:
            send_data = self.__get_send_data(self.AMBA_GET_SPACE, _type="total")
        else:
            send_data = self.__get_send_data(self.AMBA_GET_SPACE, _type="free")
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_GET_SPACE)[0]

        param = self.__get_param(data)
        if is_total:
            logging.info("SD卡总容量为:%s", param)
        else:
            logging.info("SD卡剩余容量为:%s", param)

        return param

    def get_setting_options(self, key: str) -> list:
        """
        获取单一设置的参数

        :param key: str, 参数
        :return: list
        """
        send_data = self.__get_send_data(
            self.AMBA_GET_SINGLE_SETTING_OPTIONS, param=str(key)
        )
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_GET_SINGLE_SETTING_OPTIONS)[0]

        if data is None:
            logging.error("相机没有%s参数", key)
            return None
        param = self.__get_param(data)

        _re = None
        if param == key:
            if "permission" in data and data["permission"] == "readonly":
                _re = "readonly"
            else:
                _re = data["options"]

        if _re is None:
            logging.info("参数%s没有可选的值,key")
        else:
            logging.info("参数%s值有:%s", key, _re)

        return _re

    def get_device_info(self) -> dict:
        """
        获取硬件信息

        :return: dict
        """
        send_data = self.__get_send_data(self.AMBA_GET_DEVICEINFO)
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_GET_DEVICEINFO)[0]

        if data is None:
            logging.info("无法查看硬件信息")
        else:
            if "msg_id" in data:
                del data["msg_id"]
            if "rval" in data:
                del data["rval"]

            logging.info("硬件信息为:%s", data)

        return data

    def get_battery_level(self) -> int:
        """
        获取电量

        :return: int
        """
        send_data = self.__get_send_data(self.AMBA_GET_BATTERY_LEVEL)
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_GET_BATTERY_LEVEL)[0]

        param = self.__get_param(data)

        if param:
            logging.info("相机电量剩余:%s%%", param)
        else:
            logging.info("无法查看相机电量剩余")
        return param

    def start_rtsp(self) -> bool | str:
        """
        设置启用RTSP

        :return: bool | str
        """
        send_data = self.__get_send_data(self.AMBA_BOSS_RESETVF, _type="none_force")
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_BOSS_RESETVF)[0]

        _re = False
        if self.__is_success_run(data):
            _re = self.__rtsp

            logging.info("已成功打开视频流,rtsp服务器为:%s", self.__rtsp)
        else:
            logging.error("无法打开视频流")

        return _re

    def stop_rtsp(self) -> bool:
        """
        设置关闭RTSP

        :return: bool
        """
        send_data = self.__get_send_data(self.AMBA_STOP_VF)
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_STOP_VF)[0]

        _re = False
        if self.__is_success_run(data):
            _re = True
            logging.info("已成功关闭视频流")
        else:
            logging.warning("无法正常关闭视频流,也许已经关闭或从未启动")

        return _re

    def get_rtsp_address(self) -> str:
        """
        获取流视频地址
        """
        logging.info("rtsp的地址为:%s", self.__rtsp)
        return self.__rtsp

    def start_record(self) -> bool:
        """
        定时录像
        """
        send_data = self.__get_send_data(self.AMBA_RECORD_START)
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_RECORD_START)[0]

        _re = False
        if self.__is_success_run(data):
            _re = True

            logging.info("已成功开始录像")
        else:
            logging.error("无法开始录像")

        return _re

    def stop_record(self) -> str:
        """
        停止录像

        :return: str, 录制文件地址
        """
        send_data = self.__get_send_data(self.AMBA_RECORD_STOP)
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_RECORD_STOP)[0]

        _re = None
        if self.__is_success_run(data):
            logging.info("已成功关闭录像")

            _re = self.__get_video_save_file()
            while not _re:
                _re = self.__get_video_save_file()

            logging.info("相机完成一次录制，文件为：%s", _re)

        else:
            logging.warning("无法正常关闭录像,也许已经结束或从未开始录像")

        return _re

    def get_record_time(self) -> int:
        """
        获取录像时间
        """
        send_data = self.__get_send_data(self.AMBA_GET_RECORD_TIME)
        self.__send_queue.put(send_data)

        data = self.__get_data(msgid=self.AMBA_GET_RECORD_TIME)[0]
        param = self.__get_param(data)

        logging.info("目前拍摄时长:%s", param)

        return param

    def take_photo(self) -> None:
        """
        拍照
        """
        send_data = self.__get_send_data(self.AMBA_TAKE_PHOTO)
        self.__send_queue.put(send_data)

    def get_photo_files(self, file_number=1, timeout=10) -> list:
        """
        获取保存的图片文件路径

        :param param: int, 获取照片的数量,0为所有
        :param timeout: int, 超时
        :return: list
        """
        _re = []
        _last_time = time.time()

        while time.time() - _last_time < timeout:
            with self.__photo_data_lock:
                if file_number <= 0:
                    _re = self.__photo_data_ls
                    self.__photo_data_ls = []
                elif file_number < len(self.__photo_data_ls):
                    _re = self.__photo_data_ls[0:file_number]
                    self.__photo_data_ls = self.__photo_data_ls[file_number:]
                elif file_number == len(self.__photo_data_ls):
                    _re = self.__photo_data_ls
                    self.__photo_data_ls = []
                else:
                    time.sleep(0.5)
                    continue

                break

        return _re

    def clean_photo_files(self) -> None:
        """
        把图片文件消除掉
        """
        with self.__photo_data_lock:
            self.__photo_data_ls = []

    def change_mode(self, mode: str = MODE_PHOTO) -> bool:
        """
        改变拍摄模式

        :param mode: str, MODE_*
        :return: bool
        """
        _re = False
        if "record" in mode:
            _re = self.set_setting("rec_mode", mode)
        elif "quality" in mode:
            _re = self.set_setting("capture_mode", mode)

        if not _re:
            logging.error("无法将相机设置为此模式，%s", mode)
        else:
            logging.info("相机成功设置为%s模式", mode)

        return _re

    def __get_param(self, data: dict) -> object:
        """
        获取参数

        :param param: str, 参数
        :return: dict
        """
        _re = None
        if data and "rval" in data and data["rval"] == 0:
            if "param" in data:
                _re = data["param"]

        return _re

    def __get_msgid(self, data: dict) -> int:
        """
        获取msgid

        :param param: str, 参数
        :return: dict
        """
        _re = None
        if "msg_id" in data:
            _re = data["msg_id"]

        return _re

    def __get_type(self, data: dict) -> object:
        """
        获取type

        :param param: str, 参数
        :return: dict
        """
        _re = None
        if "type" in data:
            _re = data["type"]

        return _re

    def __get_video_save_file(self) -> str:
        """
        获取保存的视频文件路径

        :return: str
        """
        _re = self.__video_save_path
        self.__video_save_path = None

        return _re

    def __get_data(self, msgid: int, timeout: int = 5, attempts: int = 5) -> dict:
        """
        获取返回的信息, 这会阻塞

        :param msgid: int, msg的id
        :param timeout: int, 超时
        :param attempts: int, 次数
        :return: dict
        """
        _re = [None]
        for i in range(attempts):
            __last_time = time.time()
            while not self.__data_ls:
                if time.time() - __last_time > timeout:
                    break
            else:
                if self.__data_ls[0]["msg_id"] == msgid:
                    _re = self.__data_ls

                self.__data_ls = None  # 清除缓存

            if _re is not None:
                break

            time.sleep(0.5)

        return _re

    def __get_send_data(
        self,
        msg_id: int,
        token: int = None,
        param: object = None,
        _type: object = None,
        **kwargs,
    ) -> str:
        """
        发送数据

        :param msg_id: int, 动作编号,AMBA_*
        :param token: int, 当前会话代号,一开始就需要获取,填写None将自动获取当前会话
        :param param: object, 参数,例如：[{"camera_clock": "2015-04-07 02:32:29"},{"video_standard": "NTSC"}]
        :param type: object, 类型
        :return: str
        """
        _dict = {"msg_id": msg_id}
        if token is None:
            token = self.__token
        _dict["token"] = token
        if param is not None:
            _dict["param"] = param
        if _type is not None:
            _dict["type"] = _type
        if kwargs is not None:
            _dict.update(kwargs)

        _send_data = json.dumps(_dict)

        return _send_data

    def __is_success_run(self, data: dict) -> bool:
        """
        判断是否成功执行

        :param data: dict,
        :return: bool
        """
        _re = False
        if "rval" in data and data["rval"] == 0:
            _re = True
        return _re

    def __analysis_msgid7_data(self, data: str) -> None:
        """
        处理消息id为7的数据

        :param data: str,
        :return: None
        """
        logging.debug("一份msgid7消息处理")
        if data["type"] == "video_record_complete":
            self.__video_save_path = data["param"]

        elif data["type"] == "photo_taken":
            logging.info("收到一份照片存储信息，%s", data["param"])

            with self.__photo_data_lock:
                self.__photo_data_ls.append(data["param"])

    def __analysis_data(self, data: str) -> dict:
        """
        数据分析处理

        :param data: str,
        :return: dict
        """
        msg_ls = []

        if not data:
            logging.warning("收到空消息，可能是相机拒绝连接")
            # 执行退出
            self.disconnect()
            return None

        if self.__temp_data:
            data = self.__temp_data + data
        try:
            _data = json.loads(data)
            msg_ls.append(_data)

            __temp_data = ""  # 清除缓存

        except json.decoder.JSONDecodeError:
            if data.count(b"{") == data.count(b"}"):
                data_ls = data.split(b"{")
                len_r = 0
                len_str = 0
                last_len = 0  # 开始位置
                for i, text in enumerate(data_ls):
                    logging.debug("数据可能是多个json的组合")
                    logging.debug("    第%d数据:%s", i, text)
                    if i == 0:  # 第一位永远是空 ""
                        continue

                    # 计算目前所在位置的字符串长度,1为中间{的个数
                    len_str += 1 + len(text)

                    if b"}" in text:
                        len_r += 1

                    if len_r == i:
                        __data = data[last_len:len_str]
                        logging.debug("分离第%d个json,%s", len(msg_ls) + 1, __data)

                        _data = json.loads(__data)
                        msg_ls.append(_data)

                        last_len = len_str

                __temp_data = ""  # 清除缓存

            else:
                logging.debug("无法解析json,应该是不完整的.写入缓存,准备下一个数据")

                __temp_data = data

        self.__temp_data = __temp_data  # 清除缓存

        # 消息处理
        _re_ls = []
        for msg in msg_ls:
            # 处理msg_id 7
            msg_id = self.__get_msgid(msg)
            if msg_id == 7:
                self.__analysis_msgid7_data(msg)

            elif msg_id == 16777220:
                if msg["rval"] != 0:
                    logging.debug("接收到一条无法拍照的信息，自动重新发送拍照指令")
                    self.take_photo()
                else:
                    logging.info("成功发送一条拍照指令")

            else:
                _re_ls.append(msg)

        if _re_ls:
            self.__data_ls = _re_ls
        return _re_ls

    def __recv_run(self):
        """
        多线程主循环,用来接收消息
        接收信息参考：
        https://gist.github.com/franga2000/1be2aa18cb3409e57af149883c06e34a
        """
        logging.debug("接收消息的多线程开始运行")
        self.__sock.setblocking(False)
        self.__sock.settimeout(0.0)
        while True:
            try:
                # _dict = self.__recv_data()
                data = self.__sock.recv(1024)
                logging.debug("接收到一条新消息,%s", data)
                # 处理接收到的信息
                data = self.__analysis_data(data)

            except IOError:
                pass

            # 退出线程
            if self.__recv_event.is_set():
                break
            time.sleep(0.1)

        # 退出线程的工作
        self.__recv_thread = None
        logging.debug("接收消息的多线程退出")

    def __send_run(self):
        """
        多线程发消息使用
        """
        logging.debug("发送消息的多线程开始运行")
        while True:
            if not self.__send_queue.empty():
                send_data = self.__send_queue.get()
                # is_send_success = False
                try:
                    self.__sock.send(bytes(send_data, "utf-8"))
                    logging.debug("发送json至相机,%s", send_data)
                    # is_send_success = True
                except Exception:
                    logging.debug("发送json至相机失败。%s", send_data)

                # if is_send_success:
                #     # 接收返回消息
                #     pass

            # 退出线程
            elif self.__recv_event.is_set():
                break

            else:
                time.sleep(0.1)

        # 退出线程的工作
        self.__send_thread = None
        logging.debug("发送消息的多线程退出")


class CameraFtp:
    """
    在相机上使用ftp下载文件
    参考:https://github.com/ffonord/yi4kplus-video-export
    """

    def __init__(self, ip, port=21) -> None:
        self.__ip = ip
        self.__port = port

        self.__ftp = ftplib.FTP()
        self.__tn = telnetlib.Telnet()

        self.__download_thread = None
        self.__download_queue = queue.Queue()
        self.__download_event = threading.Event()
        self.__is_download = False

        self.__redownload_number_dict = {}

    def connect(self) -> bool:
        """
        连接相机

        :return: bool
        """
        if not self.__open_port():
            return False

        try:
            self.__ftp.connect(self.__ip, self.__port)
        except Exception:
            logging.error("无法连接相机ftp服务")
            logging.debug(traceback.format_exc())
            return False

        if not self.__login():
            return False

        logging.info("成功连接相机ftp")

        if not isinstance(self.__download_thread, threading.Thread):
            self.__download_event.clear()
            self.__download_thread = threading.Thread(target=self.__download_file_run)
            self.__download_thread.daemon = True
            self.__download_thread.start()

        return True

    def download_file(self, local_file, remote_file) -> bool:
        """
        下载文件

        :param local_file: str, 本地文件路径
        :param remote_file: str, 远程文件路径
        :return: bool
        """
        _data_dict = {"local_file": local_file, "remote_file": remote_file}
        self.__download_queue.put(_data_dict)

    def disconnect(self) -> None:
        """
        断开连接

        :return: None
        """
        try:
            self.__tn.close()
            logging.debug("成功关闭telent连接")
        except Exception:
            logging.debug("无法正常关闭telent，%s", traceback.format_exc())

        try:
            self.__ftp.quit()
            logging.info("成功断开ftp")

        except Exception:
            logging.debug(traceback.format_exc())
            logging.info("无法正常关闭ftp，可能是已经断开或者从未启动")

        self.__download_event.set()

    def is_download_complete(self) -> bool:
        """
        是否下载完成

        :return: bool
        """
        _re = True
        if self.__is_download or not self.__download_queue.empty():
            _re = False

        return _re

    def __open_port(self) -> bool:
        """
        打开ftp的端口

        :return: bool
        """

        self.__tn.open(self.__ip, port=23)
        try:
            self.__tn.read_until(b"H2 login:", timeout=10)
        except Exception:
            logging.error("无法连接相机telent服务")
            return False
        logging.debug("成功登录telent端口")
        self.__tn.write(b"root\n")
        time.sleep(2)

        self.__tn.write(
            f"tcpsvd -u root -vE 0.0.0.0 {self.__port} ftpd -w /tmp/fuse_d/ >/dev/null 2>&1 &\n".encode(
                "utf-8"
            )
        )  # 打开ftp端口

        time.sleep(2)
        logging.debug(self.__tn.read_very_eager())

        return True

    def __login(self, user="root", passwd="") -> bool:
        """
        登录ftp

        :param user: str,
        :param passwd: str,
        :return: bool
        """
        try:
            self.__ftp.login(user, passwd)
        except Exception:
            logging.error("无法登录ftp服务")
            return False

        logging.debug("成功登录ftp端口")
        return True

    def __download_file_run(self):
        logging.debug("下载的多线程开始运行")
        while True:
            if not self.__download_queue.empty():
                self.__is_download = True

                data_dict = self.__download_queue.get()
                local_file = data_dict["local_file"]
                remote_file = data_dict["remote_file"]
                logging.debug("准备开始下载%s", remote_file)

                local_dir = os.path.dirname(local_file)
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)

                try:
                    with open(local_file, "wb") as file:
                        self.__ftp.retrbinary(f"RETR {remote_file}", file.write)

                except Exception:
                    logging.error("无法下载文件：%s。准备重试", remote_file)
                    logging.debug(traceback.format_exc())

                    logging.info("准备重连相机,%s:%d", self.__ip, self.__port)
                    self.disconnect()
                    self.connect()

                    time.sleep(5)

                    if remote_file not in self.__redownload_number_dict:
                        self.__redownload_number_dict[remote_file] = 1
                    else:
                        self.__redownload_number_dict[remote_file] += 1

                    if self.__redownload_number_dict[remote_file] <= 5:
                        self.download_file(
                            local_file=local_file, remote_file=remote_file
                        )
                    else:
                        logging.error("下载文件：%s超时，取消下载", remote_file)
                        del self.__redownload_number_dict[remote_file]

                    continue

                logging.info("成功下载文件：%s", local_file)

                self.__is_download = False

            elif self.__download_event.is_set():
                break

            else:
                time.sleep(0.1)

            self.__is_download = False

        self.__is_download = False
        logging.debug("下载的多线程结束运行")
