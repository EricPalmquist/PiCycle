#!/usr/bin/env python3

"""
==============================================================================
 PiCycle Main Control Process
==============================================================================

Description: This script will start at boot, initialize ....

 This script runs as a separate process from the Flask / Gunicorn
 implementation which handles the web interface.

==============================================================================
 Imported Modules
==============================================================================
"""
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
is_real_hardware = settings['globals']['real_hw']

# Setup logging
log_level = logging.DEBUG if settings['globals']['debug_mode'] else logging.ERROR
controlLogger = create_logger('control', filename='./logs/control.log',
							  messageformat='%(asctime)s [%(levelname)s] %(message)s', level=log_level)

# Flush Redis DB and create JSON structure
current = read_control(flush=True)
controlLogger.info('Flushing Redis DB and creating new current structure')

# Load the appropriate hardware interfaces

'''
Set up Speed input Module- user the prototype or real based on the settings file
'''
module = ''
if is_real_hardware:
	module = 'speed_input.hall_sensor'
else:
	module = 'speed_input.prototype'

SpeedModule = importlib.import_module(module)
controlLogger.info(f'Imported speed input module from {module}')

'''
Set up Display Module- user the prototype or real based on the settings file
'''
module = ''
if is_real_hardware:
	module = 'display.ili9341'
else:
	module = 'display.prototype'

DisplayModule = importlib.import_module(module)
controlLogger.info(f'Imported display module from {module}')

display_device = DisplayModule.Display(dev_pins=settings['gpio_assignments'])

'''
*****************************************
	Function Definitions
*****************************************
'''


def _main_loop():
	""" This loop will dispatch logic based on state """

	# Startup in standby mode
	# Note that our modes will be Stop, Error, Riding
	control = read_control()
	control['mode'] = 'Stop'
	control['updated'] = True
	write_control(control, direct_write=True, origin='control')

	# last_display_update = 0

	# Loop forever, processing based on the control state
	while True:

		# Check if there were updates to any of the settings that were flagged.  This is not currently
		# doing anything, but is a place were we could implement certain changes without having to completely
		# restart
		# if control['settings_update']:
		# 	control['settings_update'] = False
		# 	write_control(control, direct_write=True, origin='control')
		# 	settings = read_settings()

		# Ensure all buffered control write requests have been processed and then read the data
		# from redis  Note that "control" has all of our realtime values and mode info
		execute_control_writes()
		control = read_control()

		# Check to see if the WebUI or the local display published an update to our mode.
		if control['updated']:
			controlLogger.info(f'Changed to {control["mode"]} mode.')
			control['updated'] = False  # Reset Control Updated to False
			write_control(control, direct_write=True, origin='control')  # Commit change in 'updated' status to the file

			if control['mode'] == 'Stop':

				# Kill our speed_input reader object.  Should we choose to ride again a new one will be created
				if 'speed_input' in dir():
					speed_input.stop_riding()

			# TODO what to do when done - save ride?  Have a nice display...
			# TODO clear the control and status structures so the web UI doesn't continue showing the last values

			elif control['mode'] == 'Error':
				# TODO handle this, but I don't think we yet have anything that declares an error, so just go to stop mode.
				control['mode'] == 'Stop'
				control['updated'] == True
				write_control(control, direct_write=True, origin='control')

			elif control['mode'] == 'Riding':
				# Start a new ride!
				settings = read_settings()
				pulse_gpio = settings['gpio_assignments']['wheel']['pulses']
				radius = settings['globals']['wheel_rad_inches']
				speed_input = SpeedModule.BikeSpeed(pulse_gpio, radius)

		elif control['mode'] == 'Riding':

			# Update the display and other redis data periodically
			# if (time.time() - last_display_update) > 0.5:
			current['curr_speed'] = speed_input.curr_speed()
			current['avg_speed'] = speed_input.avg_speed()
			current['distance'] = speed_input.distance()
			write_current(current)

			# Send Data to Display
			display_device.display_status(current)

		# rest for 1 seconds
		time.sleep(1)


# Start running the main loop, which will run forever
_main_loop()
