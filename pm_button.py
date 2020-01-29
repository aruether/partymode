#!/usr/bin/env python

import RPi.GPIO as gpio
import os
import time
import subprocess
import sys
import signal
import threading


# Control box IO
key_channel = 22
button_channel = 7
armed_indicator_channel =  18
activated_indicator_channel = 29 

# Motor IO
motor1_channel = 31
motor2_channel = 35
top_limit_channel = 33

# Set up GPIO
gpio.setmode(gpio.BOARD)
gpio.setup(button_channel, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(key_channel, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(armed_indicator_channel, gpio.OUT)
gpio.setup(activated_indicator_channel, gpio.OUT)
gpio.setup(motor1_channel, gpio.OUT)
gpio.setup(motor2_channel, gpio.OUT)
gpio.setup(top_limit_channel, gpio.IN, pull_up_down=gpio.PUD_UP)

# Handle keyboard break
def signal_handler(signal, frame):
    print "Cleaning up"
    gpio.cleanup()
    sys.exit(0)

# Stop light display
def stop_party():
    global lights
    print "Stop the party!"
    lights = False
    gpio.output(activated_indicator_channel, gpio.LOW)
    ret = subprocess.check_output(["stop_music_and_lights"], stderr=subprocess.STDOUT)
    print ret

    raise_platform()

    return


# Check on the state of the key
def check_event(channel):
    print "Event triggered on channel " + str(channel)

    if channel==key_channel:
        check_key()
    elif channel==button_channel:
        check_button()
    elif channel==top_limit_channel:
        # If the platform is being raised, stop the motors. 
        # Only check when the platform is being raised, because debounce problems
        # can trigger limit switch output when turning off
        print "Top limit switch activated"
        if platform_rising(): 
            stop_motors()
    return


def platform_rising():
    # Return true if the platform is being raised
    return (gpio.input(motor1_channel) and not gpio.input(motor2_channel))


def check_key():

    global lights
    global armed

    # Give key extra time to settle
    time.sleep(0.2)

    armed = gpio.input(key_channel)

    if armed:
        print "Armed"
        gpio.output(armed_indicator_channel, gpio.HIGH)
    else:
        print "Disarmed"
        gpio.output(armed_indicator_channel, gpio.LOW)
    	if lights:
        	stop_party()

    return


def check_button():

    global lights
    global armed

    # Short debounce
    time.sleep(0.1)

    # Check to see if button is pressed and system is armed
    if (not gpio.input(button_channel)) and armed:
        if not lights:
            start_party()
        else:
            stop_party()

    # Give some time for debouncing
    time.sleep(0.2)

    return



def start_party():
    global lights
    print "Starting the party"
    gpio.output(activated_indicator_channel, gpio.HIGH)
    lights = True
    lower_platform()

    # https://stackoverflow.com/a/2581943
    # Runs the musicshowpi call in a subprocess.Popen, and then raises the platform when the subprocess completes.
    def runInThread():
        global lights
        print "Starting a thread to lightshowpi"
        command = "sudo python  /home/pi/lightshowpi/py/synchronized_lights.py".split()
        proc =  subprocess.Popen(command, stdin=subprocess.PIPE)
        proc.wait()
        lights = False
        gpio.output(activated_indicator_channel, gpio.LOW)
        raise_platform()
        return

    thread = threading.Thread(target=runInThread)
    thread.start()
    # returns immediately after the thread starts
    return thread


# Lower platform using motors
def lower_platform():
    print "Lowering platform"
    gpio.output(motor1_channel, gpio.LOW)
    gpio.output(motor2_channel, gpio.HIGH)
    threading.Timer(15, stop_motors).start()

def stop_motors():
    print "Stopping motors"
    gpio.output(motor1_channel, gpio.LOW)
    gpio.output(motor2_channel, gpio.LOW)

def raise_platform():
    # Raise the platform
    print "Raising platform"
    # Make sure top limit switch isn't already activated
    # Interrupt will handle end turning off lift motor 
    if gpio.input(top_limit_channel):
        gpio.output(motor1_channel, gpio.HIGH)
        gpio.output(motor2_channel, gpio.LOW)   

# Setup to handle keyboard interrupts (control-C)
signal.signal(signal.SIGINT, signal_handler)

# Initial state
lights = False
armed = gpio.input(key_channel)
gpio.output(armed_indicator_channel, gpio.input(armed_indicator_channel))
gpio.output(activated_indicator_channel, gpio.LOW)

stop_motors()

gpio.add_event_detect(key_channel, gpio.BOTH, callback=check_event, bouncetime=400)
gpio.add_event_detect(button_channel, gpio.RISING, callback=check_event, bouncetime=300)
gpio.add_event_detect(top_limit_channel, gpio.FALLING, callback=check_event, bouncetime=100)

print "Make sure platform is raised at the start"
raise_platform()

while True:
    # trying not to waste cycles on the pi

    # print "motor 1: " + str(gpio.input(motor1_channel))
    # print "motor 2: " + str(gpio.input(motor2_channel)) + "\n"
    time.sleep(2)
