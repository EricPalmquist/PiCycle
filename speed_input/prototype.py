#!/usr/bin/env python3

# *****************************************
# PiCycle Hall Sensor Interface Library
# *****************************************
#
# Description: This library simulates a speed
#
# *****************************************

# *****************************************
# Imported Libraries
# *****************************************

import time
from speed_input.speed_input_base import SpeedBase
import random

class BikeSpeed(SpeedBase):

    BASE_SPEED = 10.0
    RANDOM_RANGE = 2.0

    def __init__(self, pulse_gpio=0, radius=1.0 ):
        super().__init__(radius)
        
        self._speed = 0
        self._distance = 0
        self._avg_speed = 0
        self._last_time = self.start_time
        self._riding = True

    def avg_speed(self):
        """ Return the average speed """

        return 10.0
    
    def curr_speed(self):
        """ Return the current speed """

        if self._riding:
            # Every time this is requested, calculate a semi-random speed by adding a random
            # change between -0.05 and +0.05 mph
            speed_delta = random.random() * 0.1 - 0.05
            self._speed += speed_delta

            # prevent numbers from going too crazy
            self._speed = max(self.BASE_SPEED - self.RANDOM_RANGE, self._speed )
            self._speed = min(self.BASE_SPEED + self.RANDOM_RANGE, self._speed )
        else:
            self._speed = 0

        # get current time in seconds
        current_time = time.time()

        # update out distance
        self._distance += self._speed * (current_time - self._last_time ) / 3600.0

        self._last_time = current_time

        return self._speed
    
    def distance(self):
        """ Return the total distance traveled """
        return self._distance

    def stop_riding(self):       
        self._riding = False

    def avg_speed(self):
        """ Return the average speed """
        time_delta_hrs = (time.time() - self.start_time) / 3600.0
        s = self._distance / time_delta_hrs
        return s


    