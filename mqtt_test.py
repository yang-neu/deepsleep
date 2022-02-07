# Complete project details at https://RandomNerdTutorials.com

import time
#from umqttsimple import MQTTClient
from umqtt.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

import ujson
#导入配置文件
from conf import Conf

ssid = 'PROAPIS'
password = 'Kamimutsuna!109'
mqtt_server = 'broker.hivemq.com'
#mqtt_server = 'mqtt.hivespeak.net'
#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'hello'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
if station.isconnected() == False:
   station.connect(ssid, password)

while station.isconnected() == False:
  print('Connecting...')
  print(station.ifconfig())
  time.sleep(2)

print(station.isconnected())
print('Connection successful')
time.sleep(5)
print(station.ifconfig())



def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = b'Hello #%d' % counter
      #client.publish(topic_pub, msg)
      now = time.localtime()
      nows = f"%d-%02d-%02d %02d:%02d:%02d.000"%(now[0],now[1],now[2],now[3],now[4],now[5])
      scale_id = 'b827ebc76670'
      payload = {"scales_id": scale_id, "at": nows}
      msg = {'scales_id': 'b827ebc76670', 'at': '2022-02-07 21:56:53.678'}
      print(ujson.dumps(payload))
      client.publish(Conf.mac_topic_publish,ujson.dumps(payload)) 
      last_message = time.time()
      counter += 1
  except OSError as e:
    restart_and_reconnect()

