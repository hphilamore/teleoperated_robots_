#!/usr/bin/env python3
# https://realpython.com/python-sockets/
# https://www.explainingcomputers.com/rasp_pi_robotics.html

"""
#----------------------------------------------------------

Tracks hand position in image from web-cam. 

Chooses a command based on hand position.

Sends command to raspberry pi robot over wifi. 

#----------------------------------------------------------
"""


import cv2
import mediapipe
import socket
import time

from mss import mss
import sys
from subprocess import Popen, PIPE
import numpy as np

import curses

#-------------------------------------------------------------------------------
""" SETUP """

HOST = "192.168.60.223"  # The raspberry pi's hostname or IP address
PORT = 65441            # The port used by the server

# Take video stream from 'camera' or 'window' or 'keys'
input_mode = 'camera' #'window' ###'keys'#'camera' ##'camera'##'camera'  

# Window name is using window
win_name = 'zoom.us'                      
#win_name = 'Microsoft Teams'
win_name = 'zoom.us:Zoom Meeting'          # Find zoom meeting window 
#win_name = 'zoom.us:zoom floating video'  # Find zoom meeting window during share screen ('pin' caller in zoom)
#win_name = 'Vysor'                        # Find vysor window for robot POV 
#win_name = 'Vysor:SM'                     # Find vysor window for robot POV 
#win_name = 'Vysor:ART'                    # Find vysor window for robot POV 
win_name = 'Photo Booth:Photo Booth' 
# win_name = 'GoPro Webcam:'  


# Choose OC as macOS or windowsOS 
OS = 'macOS' #'windowsOS'

# Set as True if the image to run hand tracking on is full screeen 
grab_full_screen_image = False

# Output video appears full screen if True
make_output_window_fullscreen = True

# Send command to raspberry pi
send_command = False

# Number of hands to track (wings track 2 hands, turtle robots track one hand)
n_hands = 2

# A flag to indicate when no hand is deteced so that a timer can be set to 
# check of the hand is really gone or if detection has failed momentarily 
flag_no_hand = False 
flag_timeout = 2

# Detail of hands tracked when True, otherwise whole body frame 
track_hands_only = False


#-------------------------------------------------------------------------------

if OS == 'windowsOS': 
    from screeninfo import get_monitors # windows only
 
# Setup media pipe solutions 
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
mp_drawing = mediapipe.solutions.drawing_utils
mp_pose = mediapipe.solutions.pose

# Setup web cam ready for video capture 
capture = cv2.VideoCapture(0)

def window_coordinates():
    process = Popen(['./windowlist', 'windowlist.m'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    window_positions = stdout.decode().split('\n')

    for w in window_positions:
        # Find window 
        if win_name in w:                        
            # Separate window info 
            w = w.split(':')                     
            # Separate window coordinates
            coordinates = w[-1].split(',')       
            # Convert coordinates to integer
            coordinates = [int(float(i)) for i in coordinates] 
            break
    else:
        print("No window with specified name")
        print("Exiting program...")
        sys.exit(1)  

    return coordinates

def track_hands(frame, pose, flag_no_hand, flag_timeout):
    results = pose.process(frame)

    # Check for hands
    if results.multi_hand_landmarks != None:

        # Draw hands
        for handLandmarks in results.multi_hand_landmarks:
            # Draw landmarks onto frame 
            drawingModule.draw_landmarks(frame, 
                                         handLandmarks, 
                                         handsModule.HAND_CONNECTIONS)

        hand_coordinates = []

        # Find each hand up to max number of hands 
        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
            print(f'HAND NUMBER: {hand_no+1}')
            print('-----------------------')

            x_ = []
            y_ = []
            z_ = []

            for i in range(20):
                x_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].x)
                y_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].y)
                z_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].z)
                    
            # Find mean value of x and z coordinate of nodes 
            x = sum(x_)/len(x_)                
            y = sum(y_)/len(y_)                
            z = sum(z_)/len(z_)

            print(x, y, z)

            # Add the mean values to the list of coordinates to send to raspberry pi
            hand_coordinates.append(str(round(x, 2)))
            hand_coordinates.append(str(round(y, 2)))

        # Choose a command to send to the raspberry pi robot 
        # command = pos_to_command(x, y, z)
        command = ','.join(hand_coordinates)
        print(command)

    else:
            print('no hand')
            if not flag_no_hand:     # If there was a hand in previous frame
                flag_no_hand = True  # Raise the flag 
                start = time.time()  # Start the timer
                command = 'no command'

            else:
                end = time.time()
                if end-start >= flag_timeout:
                    flag_no_hand = False  # Lower the flag 
                    print('stop')
                    command = 'stop'  

    return command

def track_body(frame, pose, flag_no_hand, flag_timeout):
    # Process the frame with MediaPipe Pose
    results = pose.process(frame)

    # # Draw the pose landmarks on the frame
    # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Extract and print the XYZ coordinates of shoulders, elbows, knees, wrists, and hands
    if results.pose_landmarks:
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            if idx in [
                       # mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                       # mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                       # mp_pose.PoseLandmark.LEFT_ELBOW.value,
                       # mp_pose.PoseLandmark.RIGHT_ELBOW.value,
                       mp_pose.PoseLandmark.LEFT_WRIST.value,
                       mp_pose.PoseLandmark.RIGHT_WRIST.value,
                       # mp_pose.PoseLandmark.LEFT_KNEE.value,
                       # mp_pose.PoseLandmark.RIGHT_KNEE.value
                       ]:
                x = landmark.x
                y = landmark.y
                z = landmark.z
                print(f"Person {idx // 33 + 1}")
                print(f"Point {mp_pose.PoseLandmark(idx).name}: X={x}, Y={y}, Z={z}")
    return 10



def frame_from_window(window_coordinates):
    with mss() as sct:

        # try:
            # Use coordinates of window
            # with mss() as sct:
        window = {"top": window_coordinates[1], 
              "left": window_coordinates[0], 
              "width": window_coordinates[3], 
              "height": window_coordinates[2]
               }

        # Grab current image    
        frame = np.array(sct.grab(window))

        # If full screen image grab required
        if grab_full_screen_image: 
            frame = np.array(ImageGrab.grab()) 

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        return frame

        # except:
        #     print("No window with specified name")
        #     print("Exiting program...")
        #     sys.exit(1)

def frame_from_camera(capture):
    ret, frame = capture.read()
    # Grab current image    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 1)
    return frame


def show_tracked_wireframe(frame, OS):
    if OS == 'windowsOS': 
        if make_output_window_fullscreen:

            # To make output window full screen:
            for monitor in get_monitors():
                screen_h = monitor.height
                screen_w = monitor.width
            
            frame_h, frame_w, _ = frame.shape

            scaleWidth = float(screen_w)/float(frame_w)
            scaleHeight = float(screen_h)/float(frame_h)

            if scaleHeight>scaleWidth:
                imgScale = scaleWidth
            else:
                imgScale = scaleHeight

            newX,newY = frame_w*imgScale, frame_h*imgScale

            cv2.namedWindow('image',cv2.WINDOW_NORMAL)      # Implicitly create the window
            cv2.resizeWindow('image', int(newX),int(newY))  # Resize the window


    try:
        cv2.imshow('image', frame)                 # Show the window 
        
    except:
        pass


def send_command_to_server(HOST, PORT):
    # Send command to server socket on raspberry pi
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address
        s.connect((HOST, PORT))
        s.sendall(command.encode())




if input_mode == 'keys':

    screen = curses.initscr()
    curses.noecho() 
    curses.cbreak()
    screen.keypad(True)

    command = 'stop'

    try:

        while(True):
            char = screen.getch()

            # if char == curses.KEY_UP:
            #     print("up")
            #     command = 'forward'
            if char == ord('q'):
                break
            elif char == curses.KEY_UP:
                print("up")
                command = 'forward'
            elif char == curses.KEY_DOWN:
                print("down")
                command = 'backward'
            elif char == curses.KEY_RIGHT:
                print("right")
                command = 'right'
            elif char == curses.KEY_LEFT:
                print("left")
                command = 'left'
            elif char == ord('s'): #10:
                print("stop")
                command = 'stop' 

            # Send command to server socket on raspberry pi
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address
                s.connect((HOST, PORT))
                s.sendall(command.encode())
                # data = s.recv(1024)

    except KeyboardInterrupt:
        #Close down curses properly, inc turn echo back on!
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()
        sys.exit(1)


elif input_mode == 'window':
    # Set up window for image capture
    window_coordinates = window_coordinates()
     

elif input_mode == 'camera':
    """ Setup web cam ready for video capture """
    capture = cv2.VideoCapture(0)
 

while(True):

    if track_hands_only:
        model = handsModule.Hands(static_image_mode=False, 
                                  min_detection_confidence=0.7, 
                                  min_tracking_confidence=0.7, 
                                  max_num_hands=n_hands)
    else:
        model = mp_pose.Pose(min_detection_confidence=0.5, 
                             min_tracking_confidence=0.5)

    with model as pose:

        # Input taken from window
        if input_mode == 'window':
            frame = frame_from_window(window_coordinates)    

        elif input_mode == 'camera':
            frame = frame_from_camera(capture)


        # Look for hands 
        if track_hands_only:
            command = track_hands(frame, pose, flag_no_hand, flag_timeout) 
        else:
            command = track_body(frame, pose, flag_no_hand, flag_timeout)

        # Visualise output
        show_tracked_wireframe(frame, OS) 
 
        if cv2.waitKey(1) == 27:
            break

        if send_command:
            send_command_to_server(HOST, PORT)
