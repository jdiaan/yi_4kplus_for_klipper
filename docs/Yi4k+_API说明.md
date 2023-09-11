<!--
 * @Author: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
 * @Date: 2023-09-11 17:00:41
 * @LastEditors: github @jdiaan, bilibili @i典典典典 UID=24334629, jdiaan@163.com
 * @LastEditTime: 2023-09-11 17:30:55
 * @FilePath: \yi_4kplus_for_klipper\docs\Yi4k+_API说明.md
 * @Description: 使用API说明
 * jdiaan@163.com
 * Copyright (c) 2023 by github @jdiaan, bilibili @i典典典典 UID=24334629, All Rights Reserved.
-->
# 如何单独使用小蚁4K+的API

## 文件：
* camera_api.py......................API主要程序
* image_proc.py......................图片处理程序（其实没啥用）
* log.py.............................为了可以单独导出log文件而准备的（也没啥用）
* setting.py.........................小蚁相机可以使用的一些参数
* yi_4k_plus.py......................给klipper用的（没用）


## 连接相机：
API与FTP是分开的两套东西
### API的连接和初始化：
```python
camera = camera_api.CameraAPI(ip=111.111.111.111)
camera.connect()
```
### FTP的连接和初始化：
```python
ftp = camera_api.CameraFtp(ip=111.111.111.111)
ftp.connect()
```
## 断开相机：
### API的断开：
```python
camera.disconnect()
```
### FTP的断开：
注意：断开的只是链接，并没有把ftp端口断开。相机关机后，会自动切断ftp端口
```python
ftp.disconnect()
```

## 使用相机功能：
### API使用：
> 注意：
> * 因为拍照会有快门速度之类的影响，因此拍照命令可能会延迟发送，直到可以使用相机为止
> * 开始录像、停止录像、拍照，是拍照的一个动作（相当于按快门的一个动作），具体拍的是什么取决于当前设置的参数
> * 有API标注的方法是相机直接的API功能，你可以以此来开发更多可用的功能
```python
# API 获取所有参数设置
camera.get_all_setting
# API 获取单个参数设置
camera.get_setting
# API 设置单个参数值
camera.set_setting
# API 获取sd卡储存空间或剩余空间
camera.get_sd_space
# API 获取参数有哪些选项
camera.get_setting_options
# API 获取硬件参数
camera.get_device_info
# API 获取电池剩余
camera.get_battery_level
# API 开启rtsp流服务
camera.start_rtsp
# API 停止rtsp流服务
camera.stop_rtsp
# 获取rtsp地址
camera.get_rtsp_address
# API 开始录像
camera.start_record
# API 停止录像
camera.stop_record
# API 获取当前录像时间
camera.get_record_time
# API 拍照
camera.take_photo
# 获取所有保存的图片路径
camera.get_photo_files
# 清空保存图片路径的变量
camera.clean_photo_files
# 修改模式
camera.change_mode
```
### FTP使用：
因为是打开了telnet和FTP端口，所以你可以自己开发其他功能
```python
# 远程下载文件
ftp.download_file
# 当前是否有下载任务
ftp.is_download_complete
```