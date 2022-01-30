import machine
import time

from machine import Pin

# esp-cam
# led = Pin(33, Pin.OUT) 
# Aideepen ESP32S
led = Pin(2, Pin.OUT) 

def led_fast(cnt):

    for i in range(cnt):

        led.on()
        print('LED ON')
        time.sleep(0.5)
        led.off()
        print('LED OFF')
        time.sleep(0.5)

def led_slow(cnt):

    for i in range(cnt):

        led.on()
        print('LED ON')
        time.sleep(1)
        led.off()
        print('LED OFF')
        time.sleep(1)

def main():
    res = machine.reset_cause()

    if res == machine.PWRON_RESET:
        # 1：正常电源开机
        print('woke from a power on')
        led_fast(3)
    elif res == machine.DEEPSLEEP_RESET:
        # woke from a deep sleep
        print('woke from a deep sleep')
        led_slow(3)
    else:
        print('woke from a other reason')
        led_fast(5)

    # put the device to sleep for 20 seconds
    machine.deepsleep(20000)

if __name__ == '__main__':
	main()

