#!/usr/bin/env python3

# *****************************************
# Base class object for recording speed and distance
# *****************************************
#
# Description: This is a base clase which should be inherited from
#
# *****************************************

# *****************************************
# Imported Libraries
# *****************************************

import time
import math
from common import create_logger

class SpeedBase:

    def __init__(self, radius=1.0):
        
        """ Initialize a bike speed calculator

		Arguments:
		pulse_gpio: gpio pin to read from
        radius: radius of the wheel in inches
		
        """
        # Initialize class attributes, note that because they are attributes of "self" they are
        # available to all functions in this class

        self.total_rev_count = 0
        self.start_time = time.time()
        self.prev_time = self.start_time
        self.curr_time_delta_sec = 0.0

        # Factor for converting revelutions to miles.  1 rev = this many miles
        circ_inches = math.pi * radius**2
        circ_feet = circ_inches / 12.0
        self.dist_factor = circ_feet / 5280.0

    def stop_riding(self):       
        pass

    def avg_speed(self):
        """ Return the average speed """
        pass

    def curr_speed(self):
        """ Return the current speed """
        pass

    def distance(self):
        """ Return the total distance traveled """
        pass
    