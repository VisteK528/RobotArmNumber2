from robot import Joint, EndStop
from tmc2209_driver import TMC2209, DM556Driver
import RPi.GPIO as GPIO
import time

host = '192.168.0.108'
port = 5560

"""def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created.")
    try:
        s.bind((host, port))
    except socket.error as msg:
        print(msg)
    print("Socket bind complete.")
    return s

def setupConnection(s):
    s.listen(1)  # Allows one connection at a time.
    conn, address = s.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    return conn

s = setupServer()
conn = setupConnection(s)"""

GPIO.setmode(GPIO.BCM)
# Waist
# Shoulder 20:124 -> 200 steps per revolution, ~9925.55 steps per one shoulder revolution
waist = TMC2209(en=26, dir=13, step=19, resolution=0.9, gear_teeth=20)
waist_endstop = EndStop(SIGNAL_PIN=12, type='up')
waist_joint = Joint(driver=waist, sensor=waist_endstop, min_pos=-1, max_pos=358, gear_teeth=125, homing_direction='ANTICLOCKWISE')

#driver = DriverSerialControl(port="/dev/ttyACM0", baudrate=115200, resolution=1.8, gear_teeth=20)
shoulder = DM556Driver(DIR=15, PUL=14, driver_resolution=46.6667, motor_resolution=1.8, gear_teeth=20)
shoulder_endstop = EndStop(SIGNAL_PIN=6, type='up')
shoulder_joint = Joint(shoulder, shoulder_endstop, gear_teeth=149, min_pos=0, max_pos=181, homing_direction='CLOCKWISE')


elbow = TMC2209(en=4, dir=27, step=17, resolution=0.9, gear_teeth=20)
elbow_endstop = EndStop(SIGNAL_PIN=23)
elbow_joint = Joint(driver=elbow, sensor=elbow_endstop, gear_teeth=62, min_pos=0, max_pos=70, homing_direction='ANTICLOCKWISE')

elbow_roll = TMC2209(en=21, dir=16, step=20, resolution=1.8, gear_teeth=1)
elbow_roll.set_max_speed(4000)
elbow_roll_endstop = EndStop(SIGNAL_PIN=24)
elbow_roll_joint = Joint(driver=elbow_roll, sensor=elbow_roll_endstop, min_pos=0, max_pos=270, gear_teeth=1, homing_direction='CLOCKWISE')

elbow_pitch = TMC2209(en=10, dir=9, step=11, resolution=1.8, gear_teeth=20)
elbow_pitch.set_max_speed(4000)
elbow_pitch_endstop = EndStop(SIGNAL_PIN=25)
elbow_pitch_joint = Joint(driver=elbow_pitch, sensor=elbow_pitch_endstop, min_pos=0, max_pos=250, gear_teeth=40, homing_direction="ANTICLOCKWISE")

waist_joint.home()
waist_joint.set_angle(90)
print('Waist homed')


shoulder_joint.home(multipicator=1)
print("Shoulder homed")

"""
elbow_joint.home()
elbow_roll_joint.home()
elbow_pitch_joint.home()
elbow_pitch_joint.set_angle(150)"""



print('Homed')
"""while True:
    data = conn.recv(1024).decode()  # receive data
    selected_j, j1, j2, j3, j4, j5, j6 = data.split(';')
    print(selected_j)
    if int(selected_j) == 1:
        print('WAIST')
        waist_joint.set_angle(float(j1))
        conn.send(str.encode('Done'))
    elif int(selected_j) == 2:
        print('SHOULDER')
        shoulder_joint.set_angle(float(j2))
        conn.send(str.encode('Done'))
    else:
        conn.send(str.encode('Done'))

    time.sleep(0.001)"""

while True:
    motor = input('Podaj silnik: ')
    angle = input('Podaj kąt: ')
    if str(angle) == 'HOME':
        if motor == "WAIST":
            waist_joint.home()
        elif motor == "SHOULDER":
            shoulder_joint.home()
        elif motor == "ELBOW":
            elbow_joint.home()
        elif motor == "ROLL":
            elbow_roll_joint.home(offset=17)
        elif motor == "PITCH":
            elbow_pitch_joint.home()
    else:
        if motor == "WAIST":
            waist_joint.set_angle(float(angle))
        elif motor == "SHOULDER":
            shoulder_joint.set_angle(float(angle))
        elif motor == "ELBOW":
            elbow_joint.set_angle(float(angle))
        elif motor == "ROLL":
            elbow_roll_joint.set_angle(float(angle))
        elif motor == "PITCH":
            elbow_pitch_joint.set_angle(float(angle))
    time.sleep(2)



shoulder_length = 20.75                #207,48 mmm
elbow_length = (165.9 + 13.5)/10

algorithm = Algorithm(SHOULDER_LENGTH=shoulder_length, ELBOW_LENGTH=elbow_length,
                        WAIST_OFFSET=-90, SHOULDER_OFFSET=-190, ELBOW_OFFSET=-63, z_axis_offset=11.5)

"""while True:
    x, y, z = input("Podaj koordynaty: ").split()
    x, y, z = float(x), float(y), float(z)
    try:
        waist_degrees, shoulder_degrees, elbow_degrees = algorithm.calculate_angles_with_offsets(x, y, z)

        print("Waist degrees: ", waist_degrees)
        waist_joint.set_angle(waist_degrees)
        time.sleep(0.1)
        t = th.Thread(target=shoulder.set_angle, args=(shoulder_degrees,))
        t2 = th.Thread(target=elbow_joint.set_angle, args=(elbow_degrees,))


        t.start()
        t2.start()
        t.join()
        t2.join()
    except:
        pass"""

"""for i in range(5):
    for i in range(200):
        waist_degrees, shoulder_degrees, elbow_degrees = algorithm.calculate_angles_with_offsets(28, 0, 5 + i/10)

        t3 = th.Thread(target=waist_joint.set_angle, args=(waist_degrees,))
        t = th.Thread(target=shoulder.set_angle, args=(shoulder_degrees,))
        t2 = th.Thread(target=elbow_joint.set_angle, args=(elbow_degrees,))

        t3.start()
        t.start()
        t2.start()
        t.join()
        t2.join()
        t3.join()

        time.sleep(0.001)

    for i in range(200):
        waist_degrees, shoulder_degrees, elbow_degrees = algorithm.calculate_angles_with_offsets(30, 0, 25 - i/10)

        t3 = th.Thread(target=waist_joint.set_angle, args=(waist_degrees,))
        t = th.Thread(target=shoulder.set_angle, args=(shoulder_degrees,))
        t2 = th.Thread(target=elbow_joint.set_angle, args=(elbow_degrees,))

        t3.start()
        t.start()
        t2.start()
        t.join()
        t2.join()
        t3.join()

        time.sleep(0.001)"""



