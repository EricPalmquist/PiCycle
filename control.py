#!/usr/bin/env python3

'''
==============================================================================
 PiCycle Main Control Process 
==============================================================================

Description: This script will start at boot, initialize ....

 This script runs as a separate process from the Flask / Gunicorn
 implementation which handles the web interface.

==============================================================================
'''

'''
==============================================================================
 Imported Modules
==============================================================================
'''
import logging
import time
import importlib
from common import *  # Common Module for WebUI and Control Program

'''
==============================================================================
 Read and initialize Settings, Control, History, Metrics, and Error Data
==============================================================================
'''
# Read Settings
settings = read_settings()

# Setup logging
log_level = logging.DEBUG if settings['globals']['debug_mode'] else logging.ERROR
controlLogger = create_logger('control', filename='./logs/control.log', messageformat='%(asctime)s [%(levelname)s] %(message)s', level=log_level)
eventLogger = create_logger('events', filename='/tmp/events.log', messageformat='%(asctime)s [%(levelname)s] %(message)s', level=log_level)

# Flush Redis DB and create JSON structure
current = read_control(flush=True)
eventLogger.info('Flushing Redis DB and creating new current structure')

'''
Set up our speed reader class object - use the prototype or real based on settings file
'''
try: 
	if settings['globals']['real_hw']:
		module = "speed_input.hall_sensor"
	else:
		module = "speed_input.prototype"

	SpeedModule = importlib.import_module(f'{module}') 

	controlLogger.info(f'Loaded speed input module from {module}')
	print(f'Loaded speed input module from {module}')

except:
	controlLogger.exception(f'Error occurred loading speed input module "{module}". Trace dump: ')

'''
*****************************************
 	Function Definitions
*****************************************
'''

def _ride_cycle():
	"""
	Work Cycle Function runs when actively riding

	"""

	controlLogger.info(f'Starting a ride.')
	print(f'Starting a ride.')

	# Setup Cycle Parameters
	settings = read_settings()
	pulse_gpio = settings['gpio_assignments']['wheel']['pulses']
	radius = settings['globals']['wheel_rad_inches']
	speed_input = SpeedModule.BikeSpeed(pulse_gpio, radius)

	# ============ Main Work Cycle ============
	while True:

		time.sleep(5)

		current['curr_speed'] = speed_input.curr_speed()
		current['avg_speed'] = speed_input.avg_speed()
		current['distance'] = speed_input.distance()
		current['mode'] = 'Riding'

		write_current(current)
		
		#controlLogger.debug(f'Current Speed={speed_input.curr_speed()} mph, Average Speed={speed_input.avg_speed()}, Dist={speed_input.distance()}')
		print(f'Current Speed={speed_input.curr_speed()} mph, Average Speed={speed_input.avg_speed()}, Dist={speed_input.distance()}')

# Run the work cycle

_ride_cycle()
