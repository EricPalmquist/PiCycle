#!/usr/bin/env python3

# *****************************************
# PiCycle Hall Sensor Interface Library
# *****************************************
#
# Description: This library supports getting the hall sensor pulses and calculating
# speed and distance
#
# Install Dependencies (installed by default on rPI)
#
#    sudo pip install RPi.GPIO
#
# *****************************************

# *****************************************
# Imported Libraries
# *****************************************

import RPi.GPIO as GPIO
import time
import datetime
import math
from common import create_logger
import traceback

class BikeSpeed:

    def __init__(self, pulse_gpio=18, radius=1.0 ):
        
        """ Initialize a bike speed calculator

        This code will run first when we instantiate a new BikeSpeed class.  May consider running in
        a seperate thread later...

		Arguments:
		pulse_gpio: gpio pin to read from
        radius: radius of the wheel in inches
		
        """
        print('BikeSpeed initializing!')

        try:
            # Initialize class attributes, note that because they are attributes of "self" they are
            # available to all functions in this class

            self.total_rev_count = 0
            self.start_time = datetime.datetime.now()
            self.prev_time = self.start_time
            self.curr_time_delta_sec = 0.0
            
            # Factor for converting revelutions to miles.  1 rev = this many miles
            circ_inches = math.pi * radius**2
            circ_feet = circ_inches / 12.0
            self.dist_factor = circ_feet / 5280.0

            # Set up the rPI input pin for reading pulses on our input pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pulse_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Set up a callback to _pulse_detected to occur automatically when there is a
            # new pulse.  Note there is also a debounce option that might be useful
            GPIO.add_event_detect(pulse_gpio, edge=GPIO.RISING, callback=self._pulse_detected)

            print('BikeSpeed initialized!')

        except Exception as e:
            traceback.print_exc()
 
    def stop_riding(self):
        
        """ Cleanup bike speed calculator when we are done riding
        """

        try:
            self.total_rev_count = 0
            self.curr_time_delta = 0

            GPIO.cleanup()
            print('BikeSpeed cleaned up!')
        except:
            pass

    def _pulse_detected(self, channel):

        # This gets called automatically every time a new pulse comes in.
        self.total_rev_count += 1
        current_time = datetime.datetime.now()
        self.curr_time_delta_sec = (current_time - self.prev_time).total_seconds()
        self.prev_time = current_time

    def _calc_speed(self, pulse_delta, time_delta):
        """ Return the current given change in pulses and time """

        # We might want to do some form of averaging here if the speed is too
        # bouncy
        if time_delta > 0.0:
            rev_per_sec = pulse_delta / time_delta
            rev_per_min = rev_per_sec * 60.0
            rev_per_hour = rev_per_min * 60.0
            mph = rev_per_hour * self.dist_factor
        else:
            mph = 0

        return mph

   
    def avg_speed(self):
        """ Return the average speed """

        pulse_delta = self.total_rev_count
        time_delta = (datetime.datetime.now() - self.start_time).total_seconds()

        return self._calc_speed(pulse_delta, time_delta)
    
    def curr_speed(self):
        """ Return the current speed """

        # force the speed back to zero if no new pulsed have come in for a
        # while.  It might be better to have a speperate thread do it ...
        if (datetime.datetime.now() - self.prev_time).total_seconds() > 5.0:
            speed = 0.0
        else:
            speed = self._calc_speed(1, self.curr_time_delta_sec)
        
        return speed
    
    def distance(self):
        """ Return the total distance traveled """

        return self.total_rev_count * self.dist_factor

    