#!/usr/bin/env python3

import socket
# from gpiozero import Motor, OutputDevice
from time import sleep
from time import time
import RPi.GPIO as GPIO

# # Define and setup GPIO pins
# # Rigth foot
# motor1 = Motor(24, 27)
# motor1_enable = OutputDevice(5, initial_value=1)
# # Left foot
# motor2 = Motor(6, 22)
# motor2_enable = OutputDevice(17, initial_value=1)
# # Right tentacle
# motor3 = Motor(23, 16)
# motor3_enable = OutputDevice(12, initial_value=1)
# # Left tentacle
# motor4 = Motor(13, 18)
# motor4_enable = OutputDevice(25, initial_value=1) 


# Setup-server socket
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65443  # Port to listen on (non-privileged ports are > 1023)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()


time_old = time()
flag_wings = True

# Set the GPIO mode (pin numbers)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set variables for the GPIO motor pins
Motor1A = 6
Motor1B = 13
Motor2A = 20
Motor2B = 21
EnableA = 12
EnableB = 26
#pinTrigger = 17
#pinEcho = 18

# How many times to turn the pin on and off each second
Frequency = 20

# How long the pin stays on each cycle, as a percent 
DutyCycle = 20

# Setting the duty cycle to 0 means the motors will not turn
Stop = 0

# Set the GPIO Pin mode to be Output
GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(EnableA, GPIO.OUT)
GPIO.setup(EnableB, GPIO.OUT)

# Set the GPIO to software PWM at 'Frequency' Hertz
PWM_Motor1A = GPIO.PWM(Motor1A, Frequency)
PWM_Motor1B = GPIO.PWM(Motor1B, Frequency)
PWM_Motor2A = GPIO.PWM(Motor2A, Frequency)
PWM_Motor2B = GPIO.PWM(Motor2B, Frequency)

# Start the software PWM with a duty cycle of 0 (i.e. not moving)
PWM_Motor1A.start(Stop)
PWM_Motor1B.start(Stop)
PWM_Motor2A.start(Stop)
PWM_Motor2B.start(Stop)

def Enable(state):
    """ 
    When state is 0, enable pin is driven high, PWM output
    """
    GPIO.output(EnableA, state)
    GPIO.output(EnableB, state)

def StopMotors():
    """
    Turn all motors off
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(Stop)
    PWM_Motor2A.ChangeDutyCycle(Stop)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Forwards():
    """
    Turn both motors forwards
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Backwards():
    """
    Turn both motors backwards
    """
    PWM_Motor1A.ChangeDutyCycle(DutyCycle)
    PWM_Motor1B.ChangeDutyCycle(Stop)
    PWM_Motor2A.ChangeDutyCycle(Stop)
    PWM_Motor2B.ChangeDutyCycle(DutyCycle)

def Spin_Right():
    """
    Turn left
    """
    PWM_Motor1A.ChangeDutyCycle(DutyCycle)
    PWM_Motor1B.ChangeDutyCycle(Stop)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Spin_Left():
    """
    Turn Right
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle)
    PWM_Motor2A.ChangeDutyCycle(Stop)
    PWM_Motor2B.ChangeDutyCycle(DutyCycle)

def Turn_Right():
    """
    Turn left
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle/3)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Turn_Left():
    """
    Turn Right
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle/3)
    PWM_Motor2B.ChangeDutyCycle(Stop)


def pos_to_command(x, y):
    """
    Translates position of hand detected to command sent to robot
    """
    # Cap max and min x values 
    if x < 0.0:
        x = 0

    if x > 1.0:
        x = 1   

    # Map position to command      
    if x < 0.4:        # Turn left
        out = 'left'
         
    elif x > 0.6:        # Turn right 
        out = 'right'
        
    else:                # Go forwards
        if y >= 0.5:
            out = 'backward'
        else:
            out = 'forward'

    return out


while(1):

    # # Switch wing direction every 3s
    # time_new = time()
    # if time_new-time_old >= 3:
    #     flag_wings = not flag_wings
    #     time_old = time_new
    #     print('switched wing direction')

    # # Switch wings on/off
    # if flag_wings:
    #     print('wings up')
    #     motor3.forward()
    #     motor4.forward()
    # else:
    #     print('wings down')
    #     motor3.stop()
    #     motor4.stop()

    # print('looper')

    Enable(1)

    conn, addr = server_socket.accept()
    with conn:
        print(f"Connected by {addr}")



        while True:

            # time_new = time()
            # if time_new-time_old >= 2:
            #     flag_wings = not flag_wings
            #     time_old = time_new
            #     print('switched wing direction')
            #     #sleep(2)

            # # # Switch wings on/off
            #     if flag_wings:
            #         print('wings up')
            #         motor3.forward()
            #         motor4.forward()
            #     else:
            #         print('wings down')
            #         motor3.stop()
            #         motor4.stop()

            # Spin_Left()
            # sleep(3)
            # Spin_Right()
            # sleep(3)
            # # Turn_Left()
            # # sleep(3)
            # # Turn_Right()
            # # sleep(3)

            # StopMotors()
            # Enable(0)
            # GPIO.cleanup()




            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode()
            print(msg)

            # if msg != 'no command' and msg != 'stop':
            if msg not in ['no command', 'stop', 'forward', 'backward', 'right', 'left']:

                coordinates = msg.split(',')

                # Convert string to floating point data 
                coordinates = [float(i) for i in coordinates]

                # Grouped coordintes 2D (x,y) or 3D (x,y,z) for each hand detected
                n_dimensions = 2 # x,y,z coordinates recieved 
                hands = [coordinates[i:i+n_dimensions] for i in range(0, len(coordinates), n_dimensions)]


                # print(coordinates)

                # If 2 hands detected:
                if len(hands) > 1:

                    # If x coordinate of both hands are on the same side of the screen, ignore one hand
                    print("2 hands detected. Change n_hands to '1' in client code...")
                    print("Exiting program...")
                    sys.exit(1)


                # For each hand 
                for i in hands:

                    x_position = i[0]
                    y_position = i[1]
                    print(x_position) 

                    msg = pos_to_command(x_position, y_position)
                    print('msg', msg)



            if msg == 'stop':
                StopMotors()


            elif msg == 'left':
                Spin_Left()


            elif msg == 'right':
                Spin_Right()

                

            elif msg == 'forward':
                Forwards()


            elif msg == 'backward':
                Backwards()


            #conn.sendall(data)
    
    # except:
    #     print('no comms')


# except KeyboardInterrupt:
#         pass

