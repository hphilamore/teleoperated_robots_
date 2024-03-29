A collection of programs consisting of a client program (to be run on computer) and server program (to be run on Raspberry pi robot). 

The repository has subfolder containing programs for 3 different server Raspberry pi robots: tentacle_robot, turtle_robot, VR_robot

The server robot is controlled by the client computer over a local wifi network. 

## Setting up the client computer
- Clone this git repository
- Create virtual environment __inside__ cloned repository: Run:[`python3 venv env`]
- Add virtual environment to .gitignore file. Run:[`nano .gitignore`] and add line [`/env`]
- Activate virtual environment: Run:[`source env/bin/activate`]
- Install requirements for open cv from either of these links
    - https://raspberrypi-guide.github.io/programming/install-opencv
    - https://stackoverflow.com/questions/53347759/importerror-libcblas-so-3-cannot-open-shared-object-file-no-such-file-or-dire)
- Install open cv, run:[`pip3 install opencv-python`]
- Install media-pipe, run:[`pip3 install mediapipe`]
- Install other requirements, run:[`pip3 install -r requirements.txt`]
- Test motion tracking is working by running demos/body_tracking_demo.py and demos/hand_tracking_demo.py

## Setting up the server Raspberry pi robot
### (tentacle_robot/ turtle_robot/ VR_robot)
- Install buster legacy lite OS 
- Add any additional wifi networks to etc/wpa_supplicant/wpa_supplicant.conf
- (Optional) Add static IP for wifi network. Add following snippet to /etc/dhcpcd.conf:
	`
	interface wlan0
	static ip_address=192.168.11.13 #(desired IP)
	static routers=192.168.11.1 #(router IP)
	`
- Open a terminal. Run:[`sudo raspi-config`]. 
- Enable all interfaces (serial, camera, remote GPIO)
- Within 'Serial Port' select 'Would you like a login shell to be accessible over serial?'-> No, 'Would you like the serial port hardware to be enabled?' -> Yes
- Choose 'Finish' and reboot if prompted
- Update Raspberry pi:[`sudo apt update`]
- Install git, run:[`sudo apt install git`]
- Install pip, run:[`sudo apt-get install python3-pip`]
- Install python3, run:[`sudo apt-get install python3-venv`]
- Clone this git repository.
- (Optional) Create virtual environment __inside__ cloned repository:
	- Create virtual environment e.g. run:[`python3 -m venv env`]
	- Add virtual environment to .gitignore file, run:[`nano .gitignore`] and add line e.g. [`/env`] 
	- Edit virtual environment to include system site packages (e.g. RPi.GPIO) by setting include-system-site-packages to true in env/pyvenv.cfg:
		`
		home = /Library/Frameworks/Python.framework/Versions/3.6/bin
		include-system-site-packages = false
		version = 3.6.4
		`
	- Activate virtual environment e.g. run:[`source env/bin/activate`]
- Install library to operate GPIO pins, run:[`pip3 install gpiozero rpi-gpio`]
- Install other requirements, run:[`pip3 install -r requirements.txt`]
- Test everything is working by going into the subfolder for the relevant robot (tentacle_robot/ turtle_robot/ VR_robot) and running the motor test prpgram)

# Remote controlling the server Raspberry pi robot using the client computer
## Raspberry pi robot
- Make a note of the robot's IP address on the Wifi network you will use for communication
- Make a note of the port number (variable `PORT`) in `telepresence-server.py` within the subfolder for the relevant robot (tentacle_robot/ turtle_robot/ VR_robot)
- Activate the virtual environment if you have set one up: Run:[`source env/bin/activate`]
- Run server program:[`python3 telepresence-server.py`]
- Alternatively, you can set up the server program to run autonmatically when the Raspberry pi boots, to avoid the need to use the terminal to launch the server program (instructions in Section _Setting up a program to run on boot on the raspberry pi on boot __, below).

## Client computer
- Set variable `HOST` in `telepresence-client.py` to noted Raspberry pi IP address
- Set variable `HOST` in `telepresence-client.py` to value noted from `telepresence-server.py`
- Optionally define variables at start of `telepresence-client.py` to customise application. For example there are options to control the robot using the keyboard or using motion tracking from a camera livefeed or desktop window 
- Activate virtual environment: Run:[`source env/bin/activate`]
- Run client program:[`python3 telepresence-client.py`]
- Alternatively, you can create a windows batch file that can be clicked to launch the client program, to avoid the need to use the terminal to launch the client program. Instructions here: https://techrando.com/2019/06/22/how-to-execute-python-scripts-on-your-computer-in-batch-mode/  

## Troubleshooting
<br>If you see this warning when using ssh:

	`
	@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
	@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	`

Enter this:
[`ssh-keygen -R <IP_address>`]


# Setting up a program to run on boot on the raspberry pi on boot 
(https://stackoverflow.com/questions/67487273/raspberry-pi-4b-running-python-script-using-serial-at-boot)

- Run: [`sudo crontab -e`]
- Add this at the bottom of file that opens:
	`@reboot sh /home/neon05/start.sh &`
	*(Replace neon05 with pi username)*

- Create start.sh script in directory with username i.e. the file path added to the file that was just closed:
  
	```
	#!/bin/sh
	# start.sh
	cd /home/neon05
	python3 blink__.py
	```
 
	*(The last line is the path to the script to run)*

- To check script runs, Run: [`sh /home/neon05/start.sh`]
- Re-boot pi to check runs on start-up. Run: [`sudo reboot`]
- ssh-ing into the Raspberry pi will now launch program automatically, removing the need to manually launch the program

## Killing a program that has run on boot 
(https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup/all)

- Check which processes are running. Run: [`sudo ps -ax | grep python3`]
- Find the process ID (PID) number for your program and run: [`sudo kill <PID>`]


# Listing all desktop windows
<br>**A program written in C (called from within a Python program) to list names of all windows  on computer desktop**
Either:
- call from within Python program
OR
- Compile with: [`clang windowlist.m -o windowlist -framework coregraphics -framework cocoa`]
- Run: [`./windowlist`]

