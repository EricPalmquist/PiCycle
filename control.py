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
#log_level = logging.DEBUG if settings['globals']['debug_mode'] else logging.ERROR
log_level = logging.DEBUG if settings['globals']['debug_mode'] else logging.DEBUG
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
Set up Display Module
'''
try: 
	display_name = settings['display']['selected']
	DisplayModule = importlib.import_module(f'display.{display_name}')
	display_config = settings['display'][display_name]

except:
	controlLogger.exception(f'Error occurred loading the display module ({display_name}). Trace dump: ')
	DisplayModule = importlib.import_module('display.none')
	error_event = f'An error occurred loading the [{settings["modules"]["display"]}] display module.  The ' \
		f'"display_none" module has been loaded instead.  This sometimes means that the hardware is ' \
		f'not connected properly, or the module is not configured.  Please run the configuration wizard ' \
		f'again from the admin panel to fix this issue.'
	#errors.append(error_event)
	#write_errors(errors)
	eventLogger.error(error_event)
	print(error_event)
	#if settings['globals']['debug_mode']:
	#	raise

try:
	display_device = DisplayModule.Display(dev_pins=settings['gpio_assignments'], config=display_config)
	print('display_device created')
except:
	controlLogger.exception(f'Error occurred configuring the display module ({display_name}). Trace dump: ')
	from display.none import Display  # Simulated Library for controlling the grill platform
	display_device = Display(dev_pins=settings['gpio_assignments'], config={})
	error_event = f'An error occurred configuring the [{display_name}] display object.  The ' \
		f'"display_none" module has been loaded instead.  This sometimes means that the hardware is ' \
		f'not connected properly, or the module is not configured.  Please run the configuration wizard ' \
		f'again from the admin panel to fix this issue.'
	#errors.append(error_event)
	#write_errors(errors)
	eventLogger.error(error_event)
	print(error_event)
	#if settings['globals']['debug_mode']:
	#	raise
'''
*****************************************
 	Function Definitions
*****************************************
'''

def _start_ride_cycle():
	"""
	Ride Cycle Function runs when actively riding

	"""

	controlLogger.info(f'Starting a ride.')

	# Setup Cycle Parameters
	settings = read_settings()
	pulse_gpio = settings['gpio_assignments']['wheel']['pulses']
	radius = settings['globals']['wheel_rad_inches']
	return SpeedModule.BikeSpeed(pulse_gpio, radius)

	# ============ Main Work Cycle ============
	# while True:

	# 	time.sleep(5)

	# 	current['curr_speed'] = speed_input.curr_speed()
	# 	current['avg_speed'] = speed_input.avg_speed()
	# 	current['distance'] = speed_input.distance()
	# 	current['mode'] = 'Riding'

	# 	write_current(current)
		
	# 	print_speed = "{:4.1f}".format(speed_input.avg_speed())
	# 	print_dist  = "{:4.1f}".format(speed_input.distance())
	# 	display_text = f'speed = {print_speed}\ndist  = {print_dist}'
	# 	print(display_text)

		#display.display_text(display_text)

		#controlLogger.debug(f'Current Speed={speed_input.curr_speed()} mph, Average Speed={speed_input.avg_speed()}, Dist={speed_input.distance()}')
		#print(f'Current Speed={speed_input.curr_speed()} mph, Average Speed={speed_input.avg_speed()}, Dist={speed_input.distance()}')

def _main_loop():
	''' This loop will dispatch logic based on state '''

	# Startup in standby mode
	# Note that our modes will be Stop, Error, Riding
	control = read_control()
	control['mode'] = 'Stop'
	control['updated'] = True
	write_control(control, direct_write=True, origin='control')

	last_display_update = 0

	# Loop forever, processing based on the control state
	while True:

		# Check if there were updates to any of the settings that were flagged
		if control['settings_update']:
			control['settings_update'] = False
			write_control(control, direct_write=True, origin='control')
			#settings = read_settings()
		
		# Ensure all buffered control write requests have been processed and then read the data
  		# from redis  Note that "control" has all of our realtime values and mode info
		execute_control_writes()
		control = read_control()

		# Check to see if the WebUI or the local display published an update to our mode.
		if control['updated']:
			eventLogger.debug(f'Control Settings Updated.  New mode is: {control["mode"]}')
			control['updated'] = False  # Reset Control Updated to False
			write_control(control, direct_write=True, origin='control')  # Commit change in 'updated' status to the file

			if control['mode'] == 'Stop':
				#TODO what to do when done - save ride?  Have a nice display...
				#TODO clear the control and status structures so the web UI doesn't continue showing the last values
				
				# Kill our speed_input reader object.  Should we choose to ride again a new one will be created
				if 'speed_input' in dir():
					print('killing')
					speed_input.stop_riding()

			elif control['mode'] == 'Error':
				#TODO handle this, but I don't think we yet have anything that declares an error
				pass
			
			elif control['mode'] == 'Riding':
				# Start a new ride!
				speed_input = _start_ride_cycle()
		
		elif control['mode'] == 'Riding':

			eventLogger.debug('in riding mode')
			# Update the display and other redis data periodically
			if (time.time() - last_display_update) > 0.5:
				current['curr_speed'] = speed_input.curr_speed()
				current['avg_speed'] = speed_input.avg_speed()
				current['distance'] = speed_input.distance()
				write_current(current)

				# Send Data to Display
				display_device.display_status(current)

		# rest for 2 seconds
		time.sleep(2)


# Start running the main loop, which will run forever

_main_loop()