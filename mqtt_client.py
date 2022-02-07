#!usr/bin/env python3
#-*- coding:utf-8 _*-
import json
import os
import threading
import time
from datetime import datetime

import paho.mqtt.client as mqtt

import clog
from clog import logger
from conf import Conf
from data import get_scale_id
from tool.git_version import get_branch, get_version


class MQTTClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if MQTTClient._instance is None:
            MQTTClient._instance = MQTTClient()
        return MQTTClient._instance

    def __init__(self):
        self.connected = False
        self._on_message = None
        self.scale_id = get_scale_id()
        self.cli = mqtt.Client(self.scale_id, clean_session=False)
        self.cli.username_pw_set(username=Conf.username, password=Conf.password)
        self.cli.on_connect = self.on_connect
        self.cli.on_publish = self.on_publish
        self.cli.on_disconnect = self.on_disconnect
        self.cli.on_message = self.on_message
        self.mid = None
        self.lock = threading.RLock()
        self.messages = []

    def loop(self, on_message):
        path, _ = os.path.split(Conf.cache_message_file)
        if not os.path.exists(path):
            os.mkdir(path)
        self.load_message()
        self._on_message = on_message
        # 遗嘱消息
        self.cli.will_set(Conf.will_topic_publish, json.dumps(self.scale_id), Conf.pub_qos)
        self.cli.connect_async(Conf.host, keepalive=Conf.keepalive)
        while True:
            try:
                self.cli.loop_forever()
            except Exception as ex:
                logger.error(ex)
                time.sleep(60)

    def publish(self, topic, payload, cache=False, retain=False, times=0):
        mid = -1
        current_times = times if times is not None else 0
        if self.cli.is_connected():
            try:
                self.lock.acquire()
                info = self.cli.publish(topic, payload, qos=Conf.pub_qos, retain=retain)
                mid = info.mid
                current_times = current_times + 1
            except Exception as ex:
                logger.error(ex)
                logger.error("publish message except!")
            finally:
                if cache:
                    logger.info("cache topic:%s payload:%s!" % (topic, payload))
                    self.cache_message(topic, payload, mid, retain, current_times)
                self.lock.release()
        elif cache:
            self.cache_message(topic, payload, mid, retain, current_times)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        MQTTClient.get_instance()._on_connect(rc)

    def _on_connect(self, rc):
        logger.info("on_connect")
        if rc == 0:
            self.connected = True
            # 链接成功
            status = "成功" if str(rc) == "0" else "失败"
            logger.info("链接主机 => %s" % status)
            # 订阅地址
            # pub mac
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            payload = {"scales_id": self.scale_id, "at": now}
            logger.info("推送消息 => %s" % Conf.mac_topic_publish)
            logger.info("消息内容 => %s" % payload)
            self.publish(Conf.mac_topic_publish, json.dumps(payload), False)
            # pub version
            self.notify_version()
            topic_subscribe = Conf.topic_subscribe % self.scale_id
            logger.info("订阅消息 => %s" % topic_subscribe)
            self.cli.subscribe(topic=topic_subscribe, qos=Conf.qos)
            led_topic_subscribe = Conf.led_topic_subscribe % self.scale_id
            logger.info("订阅消息 => %s" % led_topic_subscribe)
            self.cli.subscribe(topic=led_topic_subscribe, qos=Conf.qos)
            ota_topic_subscribe = Conf.ota_topic_subscribe % self.scale_id
            logger.info("订阅消息 => %s" % ota_topic_subscribe)
            self.cli.subscribe(topic=ota_topic_subscribe, qos=Conf.qos)
            survival_topic_subscribe = Conf.survival_topic_subscribe % self.scale_id
            logger.info("订阅消息 => %s" % survival_topic_subscribe)
            self.cli.subscribe(topic=survival_topic_subscribe, qos=Conf.qos)
            self.pub_remain_message()
        else:
            logger.error("connect error for result: {}".format(rc))

    @staticmethod
    def on_disconnect(client, userdata, rc):
        logger.error("on_disconnect")
        MQTTClient.get_instance()._on_disconnect()

    def _on_disconnect(self):
        logger.error("on_disconnect")
        self.connected = False

    @staticmethod
    def on_publish(client, userdata, packet):
        MQTTClient.get_instance()._on_publish(packet)

    def _on_publish(self, packet):
        logger.info("publish ok {}".format(packet))
        self.remove_message(packet)

    @staticmethod
    def on_message(client, userdata, msg):
        try:
            payload = msg.payload.decode()
            logger.info("接收消息 => %s" % msg.topic)
            logger.info("消息内容 => %s" % payload)
            if MQTTClient.get_instance()._on_message is not None:
                MQTTClient.get_instance()._on_message(msg.topic, payload)
        except Exception as ex:
            logger.error(ex)

    def pub_remain_message(self):
        logger.info("开始发送失败的消息")
        messages = []
        messages.extend(self.messages)
        self.messages.clear()
        self.flush_message()
        for message in messages:
            self.publish(message["topic"], message["payload"], True, message["retain"], message['times'])

    def cache_message(self, topic, message, mid=-1, retain=False, times=1):
        if times >= Conf.max_resend_times:
            return
        logger.debug("缓存消息 {}".format(mid))
        self.lock.acquire()
        self.messages.append({"topic": topic, "payload": message, "mid": mid, "retain": retain, 'times': times})
        if len(self.messages) > Conf.cache_message_max_lines:
            self.messages.pop(0)
        self.flush_message()
        self.lock.release()

    def remove_message(self, mid):
        self.lock.acquire()
        for message in self.messages:
            if message['mid'] == mid:
                self.messages.remove(message)
                break
        self.flush_message()
        self.lock.release()

    def flush_message(self):
        try:
            self.lock.acquire()
            if len(self.messages) > 0:
                with open(Conf.cache_message_file, 'w', encoding='utf8') as fp:
                    for message in self.messages:
                        fp.write(json.dumps(message) + '\n')
            else:
                if os.path.exists(Conf.cache_message_file):
                    os.remove(Conf.cache_message_file)
        except Exception as ex:
            logger.error(ex)
        finally:
            self.lock.release()

    def load_message(self):
        try:
            if os.path.exists(Conf.cache_message_file):
                with open(Conf.cache_message_file, 'r', encoding='utf8') as fp:
                    for line in fp.readlines():
                        info = json.loads(line.strip())
                        self.messages.append({"topic": info.get("topic"), "payload": info.get("payload"), "mid": -1,
                                              "retain": info.get("retain"), 'times': info.get("times")})
        except Exception as ex:
            logger.error(ex)

    def notify_version(self):
        if os.path.exists(Conf.version_file):
            try:
                info = {'scales_id': self.scale_id,
                        'at': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        'branch': get_branch(),
                        'version': get_version()}
                payload = json.dumps(info)
                logger.info("推送消息 => %s" % Conf.version_topic_publish)
                logger.info("消息内容 => %s" % payload)
                self.publish(Conf.version_topic_publish, payload)
                os.remove(Conf.version_file)
            except:
                clog.print_exception()
