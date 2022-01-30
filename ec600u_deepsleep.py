from machine import Pin
from machine import RTC
from misc import Power
import utime
#import pm

# EC600S/N模组
#LED = Pin(Pin.GPIO24, Pin.OUT, Pin.PULL_DISABLE, 0)
# EC600U
# LED = Pin(Pin.GPIO14, Pin.OUT, Pin.PULL_DISABLE, 0)
#P60
LED = Pin(Pin.GPIO4, Pin.OUT, Pin.PULL_DISABLE, 0)
# BC25
# LED = Pin(Pin.GPIO5, Pin.OUT, Pin.PULL_DISABLE, 0)
"""
P60对应EC600S/EC600N模组的GPIO13、对应EC600U模组的GPIO4
P56对应EC600S/EC600N模组的GPIO28、对应EC600U模组的GPIO16
P61对应EC600S/EC600N模组的GPIO14、对应EC600U模组的GPIO1
"""


def led_fast(cnt):

	for i in range(cnt):

		LED.write(1)
		print('LED ON')
		utime.sleep(0.5)    
		LED.write(0)
		print('LED OFF')
		utime.sleep(0.5)

def led_slow(cnt):

	for i in range(cnt):

		LED.write(1)
		print('LED ON')
		utime.sleep(1)    
		LED.write(0)
		print('LED OFF')
		utime.sleep(1)   

def rtc_cb():
	while(1):
		print('rt call back')
		utime.sleep(1)

		
def main():
	res = Power. powerOnReason()
	rtc = RTC()
	rtc.register_callback(rtc_cb)
	
	if res == 1:
		# 1：正常电源开机
		led_fast(3)
	elif res == 4:
		# 4：RTC定时开机
		led_slow(3)
	else:
		led_fast(5)
		
	print("powerOnReason = %d" % res)

	# 设置RTC到期时间
	while(1):
		data_e=rtc.datetime()
		data_l=list(data_e)
		
		# Second
		n = 20
		if data_l[6] < (59 - n):
			data_l[6] +=n
			data_e=tuple(data_l)
			ret = rtc.set_alarm(data_e)
			if ret == 0:
				print('rtc set ok')
			else:
				print('rtc set ng')

			ret = rtc.enable_alarm(1)
			if ret == 0:
				print('rtc alarm ok')
				print('powerDown...')
				Power.powerDown()
			else:
				print('rtc alarm ng')
				
				
				
			break
		else:
			print("second = %d" % data_l[6])
			utime.sleep(10)


if __name__ == '__main__':
	main()


