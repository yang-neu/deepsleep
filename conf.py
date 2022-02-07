# encoding=utf8
# !/usr/bin/env python3

class Conf:
    # conf:: HX711
    hx711_dout_pin = 21
    hx711_pd_sck_pin = 20

    # conf:: DHT11
    dht11_pin = 18

    # conf:: BEM280
    bem280_i2c_address = 0x76
    bem280_bus_number = 0

    # conf:: ADS1115
    ads1x15_i2c_address = 0x48
    ads1x15_bus_number = 1
    # 选择1的增益来读取0到4.096V的电压 或者选择一个不同的增益来改变所读取的电压范围
    # 2/3 = +/-6.144V
    # 1   = +/-4.096V
    # 2   = +/-2.048V
    # 4   = +/-1.024V
    # 8   = +/-0.512V
    # 16  = +/-0.256V
    ads1x15_gain = 1

    # conf:: SOUND
    # 每次收集声音的时间长度(秒)
    second = 1

    # conf:: SIM7600 4G模块
    # PWR P22 (对应BCM的P6)
    power_key = 6
    # FLIGHTMODE P7 (对应BCM的P4)，当拉高时进入飞行模式
    flightmode = 4
    # 接口 波特率
    gps_port = "/dev/ttyS0"
    baudrate = 115200

    # conf:: EMQ服务器 mqtt
    host = "mqtt.hivespeak.net"
    port = 1883
    keepalive = 600
    username = "admin"
    password = "LTAIzYlMeQ9o7thS"
    # 服务质量
    qos = 2
    pub_qos = 1
    # 订阅地址
    topic_subscribe = "beehiveData/%s/get_raw"
    topic_publish = "beehiveData/send_raw"
    topic = "beehiveData"
    # 主动推送到 topic 的时间间隔(秒)
    interval = 3600

    # 接收MAC地址主题
    mac_topic_publish = "scalesMac"
    led_topic_subscribe = "beehive/%s/LED"
    ota_topic_subscribe = "beehive/%s/OTA"

    # 遗嘱主题
    will_topic_publish = "beehiveData/lwt"

    # 版本主题
    version_topic_publish = "beehiveData/version"
    version_file = "/home/pi/hive-pi/version"

    # 保活主题
    survival_topic_subscribe = 'confirm/%s/scalesContact'
    survival_topic_publish = 'scales_survival'

    cache_message_file = '/home/pi/hive-pi/message/mqtt_message.txt'
    cache_message_max_lines = 24

    # conf:: 日志
    # 文件名称
    log_file_name = "/home/pi/hive-pi/log_mqtt"
    # 文件保存最大数(单位MB)
    log_file_size = 10

    # 无硬件 或硬件失灵时 默认返回的数值
    # 正式发布时 请将下面数值更改成 = ""
    in_humi = ""
    in_temp = ""
    ex_temp = ""
    ex_humi = ""
    ex_bar = ""
    weight = ""
    sound = ""
    #没有GPS模块时，用下面的数据调试
    gps = "2232.643279,N,11404.697531,E,300618,085520,0,96.0,0,0,0,0"
    #power = ""
    #battery = ""
    # 没有ADS115模块时，用下面的数据调试 插电
    power = "0"
    battery = "2"

    # 风机自动模式 0 手动 1 自动
    fan_auto = 1
    # 开启风扇的温度
    high_temp = 40
    # 关闭风扇的温度
    low_temp = 35
    # 风扇对应的管脚
    fan_pin = 16
    # 配置文件
    fan_conf_file = "/home/pi/hive-pi/fan.conf"
    # 风扇检测间隔时间
    fan_loop_interval = 600
    # 风扇指令
    fan_type_id = "11"

    led_pin = 12
    led_state = 2
    led_count = 5
    led_interval = 200
    led_conf_file = "/home/pi/hive-pi/led.conf"

    led_loop_interval = 10

    get_data_loop_count = 5

    default_timeout = 10

    CODE_OK = 0
    CODE_NG = -1

    fault_topic_format = "beehiveData/fault"

    internal_fault = 1  # 内部传感器异常
    external_fault = 2  # 外部传感器异常
    weight_fault = 3  # 重力传感器异常
    gps_fault = 4  # GPS传感器异常
    battery_fault = 5  # 太阳能异常
    sound_fault = 6  # 麦克风异常

    max_resend_times = 2
