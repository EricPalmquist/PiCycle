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
# *****************************************

# *****************************************
# Imported Libraries
# *****************************************

import datetime
import math
from common import create_logger

class BikeSpeed:

    def __init__(self, pulse_gpio=0, radius=1.0 ):
        
        """ Initialize a bike speed calculator

        This code will run first when we instantiate a new BikeSpeed class.  May consider running in
        a seperate thread later...

		Arguments:
		pulse_gpio: gpio pin to read from
        radius: radius of the wheel in inches
		
        """
        #print('initializing')

        try:
            # Initialize class attributes, note that because they are attributes of "self" they are
            # available to all functions in this class

            self.total_rev_count = 0
            self.start_time = datetime.datetime.now()
            self.prev_time = self.start_time
            self.curr_time_delta = 0
            
            # Factor for converting revelutions to miles
            self.dist_factor = self._rev_to_mi(radius)

        except:
            pass #TODO error logging here
        
        finally:
            pass

    def _rev_to_mi(self, radius):
        """ calculte conversion factor from rev to miles"""

        circ_inches = math.pi * radius**2
        circ_feet = circ_inches / 12.0
        circ_mi = circ_feet / 5280.0

        return circ_mi

    def avg_speed(self):
        """ Return the average speed """

        return 10.0
    
    def curr_speed(self):
        """ Return the current speed """

        return 11.0
    
    def distance(self):
        """ Return the total distance traveled """
        time_delta = (datetime.datetime.now() - self.start_time).total_seconds()
        hours = time_delta / (3600.0) 
        mi = self.avg_speed() * hours
        return mi

    