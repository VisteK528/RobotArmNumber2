from robot import Joint, EndStop
from tmc2209_driver import TMC2209
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
# Waist
# Shoulder 20:124 -> 200 steps per revolution, ~9925.55 steps per one shoulder revolution
shoulder = TMC2209(en=21, dir=16, step=20)
waist = TMC2209(en=26, dir=13, step=19)
shoulder_endstop = EndStop(SIGNAL_PIN=6)

shoulder_joint = Joint(driver=shoulder, sensor=shoulder_endstop)

shoulder_joint.home()