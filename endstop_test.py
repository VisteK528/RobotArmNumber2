import RPi.GPIO as GPIO
import time
from robot import EndStop


GPIO.setmode(GPIO.BCM)

stop = EndStop(SIGNAL_PIN=23, type='up')

"""endstop_pins = [(12, "First"), (6, "Second"), (23, "Third"), (24, "Fourth"), (25, "Fifth")]
endstops = []

for pin in endstop_pins:
    endstops.append(EndStop(SIGNAL_PIN=pin[0]), pin[1])
    
for endstop in endstops:
    while True:
        if endstop[0].check_sensor"""



while True:
    time.sleep(0.1)
    print(stop.check_sensor())

"""DIG = 23
GPIO.setup(DIG, GPIO.OUT)



while True:
    channel = GPIO.input(DIG)
    print(channel)
    time.sleep(0.01)"""





