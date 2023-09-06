class Setting:
    """
    列举了可以获取或可以设置的参数
    """

    camera_clock = "camera_clock"  # "2023-08-27 17:14:26"
    video_standard = "video_standard"  # "PAL"
    app_status = "app_status"  # "idle"
    video_resolution = "video_resolution"  # "1280x720 50P 16:9 super"
    video_stamp = "video_stamp"  # "off"
    video_quality = "video_quality"  # "S.Fine"
    timelapse_video = "timelapse_video"  # "0.5"
    capture_mode = "capture_mode"  # 拍照模式
    photo_size = "photo_size"  # 分辨率
    photo_stamp = "photo_stamp"  # 时间戳

    photo_quality = "photo_quality"  # "S.Fine"
    precise_cont_time = "precise_cont_time"  # "0.5 sec"
    precise_cont_poweroff = "precise_cont_poweroff"  # "off"
    precise_cont_poweroff_settable = "precise_cont_poweroff_settable"  # "off"
    buzzer_volume = "buzzer_volume"  # "mute"
    buzzer_ring = "buzzer_ring"  # "off"
    burst_capture_number = "burst_capture_number"  # "3 p / s"
    restore_factory_settings = "restore_factory_settings"  # "on"
    restore_wifi = "restore_wifi"  # "on"
    restore_bt = "restore_bt"  # "on"

    wifi_update = "wifi_update"  # "TRUE"
    wifi_ssid = "wifi_ssid"  # "YDXJ_0154419_5G"
    wifi_password = "wifi_password"  # "1234567890"
    sta_ssid = "sta_ssid"  # ""
    sta_password = "sta_password"  # ""
    sta_connect_password = "sta_connect_password"  # ""
    sta_ip = "sta_ip"  # ""
    wifi_mode = "wifi_mode"  # "ap"
    led_mode = "led_mode"  # "on"
    restore_bt = "restore_bt"  # "status enable"

    meter_mode = "meter_mode"  # 测光模式
    sd_card_status = "sd_card_status"  # "insert"
    cvbs_enable = "cvbs_enable"  # "off"
    bt_button_mode = "bt_button_mode"  # "switch"
    sw_version = (
        "sw_version"  # "Z18V13L_1.4.14_build-20180622051900_git-bd1c9b2c_r1019"
    )
    hw_version = "hw_version"  # "YDXJ2_V13LB"
    dual_stream_status = "dual_stream_status"  # "on"
    streaming_status = "streaming_status"  # "off"
    precise_cont_capturing = "precise_cont_capturing"  # "off"
    piv_enable = "piv_enable"  # "on"

    auto_low_light = "auto_low_light"  # "on"
    warp_enable = "warp_enable"  # "on"
    support_auto_low_light = "support_auto_low_light"  # "on"
    precise_selftime = "precise_selftime"  # "5s"
    precise_self_running = "precise_self_running"  # "off"
    auto_power_off = "auto_power_off"  # "off"
    serial_number = "serial_number"  # "Z18V13LB730LCN0154419"
    system_mode = "system_mode"  # "capture"
    system_default_mode = "system_default_mode"  # "last used mode"
    precise_self_remain_time = "precise_self_remain_time"  # "0"

    sdcard_need_format = "sdcard_need_format"  # "no-need"
    video_rotate = "video_rotate"  # "auto"
    rec_mode = "rec_mode"  # "record"
    record_photo_time = "record_photo_time"  # "5"
    dev_functions = "dev_functions"  # "8967"
    timelapse_video_duration = "timelapse_video_duration"  # "off"
    timelapse_video_resolution = "timelapse_video_resolution"  # "1920x1080 25P 16:9"
    video_photo_resolution = "video_photo_resolution"  # "1920x1080 50P 16:9"
    slow_motion_rate = "slow_motion_rate"  # "4"
    slow_motion_res = "slow_motion_res"  # "1280x720x4"

    loop_rec_duration = "loop_rec_duration"  # "20 minutes"
    iq_eis_enable = "iq_eis_enable"  # "on"
    iq_photo_iso_min = "iq_photo_iso_min"  # 拍照最小感光度
    iq_photo_iso = "iq_photo_iso"  # 拍照最大感光度
    iq_video_iso = "iq_video_iso"  # "1600"
    iq_photo_shutter = "iq_photo_shutter"  # 快门速度
    iq_photo_ev = "iq_photo_ev"  # 曝光补偿
    iq_video_ev = "iq_video_ev"  # "0"
    iq_photo_wb = "iq_photo_wb"  # 白平衡
    iq_video_wb = "iq_video_wb"  # "native"

    protune = "protune"  # "off"
    screen_auto_lock = "screen_auto_lock"  # "60s"
    out_mic = "out_mic"  # "off"
    dewarp_support_status = "dewarp_support_status"  # "on"
    eis_support_status = "eis_support_status"  # "off"
    mic_level = "mic_level"  # "high"
    photo_flat_color = "photo_flat_color"  # 色彩模式
    video_flat_color = "video_flat_color"  # "flat"
    long_shutter_define = "long_shutter_define"  # "power_off"
    product_name = "product_name"  # "YIAC 3"

    stamp_enable = "stamp_enable"  # "on"
    ev_enable = "ev_enable"  # "on"
    fov = "fov"  # "wide"
    wifi_country = "wifi_country"  # "CN"
    wifi_country_editable = "wifi_country_editable"  # "on"
    rec_audio_support = "rec_audio_support"  # "off"
    photo_sharpness = "photo_sharpness"  # 锐度
    video_sharpness = "video_sharpness"  # "high"
    support_flat_color = "support_flat_color"  # "on"
    support_sharpness = "support_sharpness"  # "on"

    timelapse_photo_shutter = "timelapse_photo_shutter"  # "1/500s"
    support_fov = "support_fov"  # "off"
    support_iso = "support_iso"  # "on"
    support_wb = "support_wb"  # "on"
    video_file_max_size = "video_file_max_size"  # "4GB"
    quick_view = "quick_view"  # QuickView
    sound_effect = "sound_effect"  # "stereo"
    sound_effect_support = "sound_effect_support"  # "off"
    language = "language"  # "CN"

    photo_file_type = "photo_file_type"  # 文件格式
    photo_file_type_settable = "photo_file_type_settable"  # "off"
    video_shutter = "video_shutter"  # "1/200s"
    video_shutter_support = "video_shutter_support"  # "off"


photo_setting = {
    Setting.photo_size: [
        "12MP (4000x3000 4:3) fov:w",
        "7MP (3008x2256 4:3) fov:w",
        "7MP (3008x2256 4:3) fov:m",
        "5MP (2560x1920 4:3) fov:m",
        "8MP (3840x2160 16:9) fov:w",
    ],  # 分辨率
    Setting.iq_photo_shutter: [
        "auto",
        "1/500s",
        "1/125s",
        "1/30s",
        "1/8s",
        "1/2s",
        "1s",
        "2s",
        "5s",
        "10s",
        "20s",
        "30s",
    ],  # 快门
    Setting.meter_mode: ["center", "average", "spot"],  # 测光模式
    Setting.iq_photo_wb: ["auto", "native", "3000k", "5500k", "6500k"],  # 白平衡
    Setting.photo_flat_color: ["yi", "flat"],  # 色彩模式
    Setting.iq_photo_iso_min: ["100", "200", "400"],  # 最小感光度
    Setting.iq_photo_iso: ["auto", "100", "200", "400", "800"],  # 最大感光度
    Setting.photo_sharpness: ["high", "medium", "low"],  # 锐度
    Setting.iq_photo_ev: [
        "-2.0",
        "-1.5",
        "-1.0",
        "-0.5",
        "0",
        "+0.5",
        "+1.0",
        "+1.5",
        "+2.0",
    ],  # 曝光补偿
    Setting.photo_stamp: ["off", "time", "date", "date/time"],  # 时间戳
    Setting.quick_view: ["Off", "0.5S", "1S", "2S", "3S", "5S"],  # QuickView
    Setting.photo_file_type: ["jpg", "raw+jpg"],  # 文件格式
}

mode_setting = {
    Setting.capture_mode: [
        "precise quality",  # 普通拍照
        "precise quality cont.",  # 延时拍照
        "burst quality",  # 连续拍照
        "precise self quality",  # 定时拍照
    ],
    Setting.rec_mode: [
        "record",  # 普通录像
        "record_timelapse",  # 延时录像
        "record_loop",  # 循环录像
        "record_photo",  # 拍照 + 录像
        "record_slow_motion",  # 慢动作
        # "live_streaming",  # 直播
    ],
}
