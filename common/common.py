'''
==============================================================================
 PiCycle Common Module
==============================================================================

Description: This library provides functions that are common to 
  both app.py and control.py

==============================================================================
'''

'''
==============================================================================
 Imported Modules
==============================================================================
'''
import time
import datetime
import os
import io
import json
import math
import redis
# import uuid
# import random
import logging
from collections.abc import Mapping
from ratelimitingfilter import RateLimitingFilter

# *****************************************
# Constants and Globals 
# *****************************************
'''
==============================================================================
 Constants and Globals
==============================================================================
'''
# BACKUP_PATH = './backups/'  # Path to backups of settings.json, pelletdb.json

# Set of default colors for charts.  Contains list of tuples (primary color, secondary color). 
# COLOR_LIST = [
# 	('rgb(0, 64, 255, 1)', 'rgb(0, 128, 255, 1)'),  # Blue
# 	('rgb(0, 200, 64, 1)', 'rgb(0, 232, 126, 1)'),  # Green
# 	('rgb(132, 0, 0, 1)', 'rgb(200, 0, 0, 1)'),  # Red 
# 	('rgb(126, 0, 126, 1)', 'rgb(126, 64, 125, 1)'),  # Purple
# 	('rgb(255, 210, 0, 1)', 'rgb(255, 255, 0, 1)'),  # Yellow
# 	('rgb(255, 126, 0, 1)', 'rgb(255, 126, 64, 1)')	# Orange
# ]

# Setup Command / Status database connection Global 
cmdsts = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)


'''
==============================================================================
 Functions
==============================================================================
'''
def create_logger(name, filename='./logs/picycle.log', messageformat='%(asctime)s | %(levelname)s | %(message)s', level=logging.INFO):
	'''Create or Get Existing Logger'''
	logger = logging.getLogger(name)
	''' 
		If the logger does not exist, create one. Else return the logger. 
		Note: If the a log-level change is needed, the developer should directly set the log level on the logger, instead of using 
		this function.  
	'''
	if not logger.hasHandlers():
		logger.setLevel(level)
		formatter = logging.Formatter(fmt=messageformat, datefmt='%Y-%m-%d %H:%M:%S')
		# datefmt='%Y-%m-%d %H:%M:%S'
		# Add a rate limit filter for the voltage error logging 
		config = {'match': ['An error occurred reading the voltage from one of the ports.']}
		ratelimit = RateLimitingFilter(rate=1, per=60, burst=5, **config)  # Allow 1 per 60s (with periodic burst of 5)
		handler = logging.FileHandler(filename)		
		handler.setFormatter(formatter)
		handler.addFilter(ratelimit)  # Add the rate limit filter
		logger.addHandler(handler)
	return logger

# def default_settings():
# 	settings = {}

	# updater_info = read_updater_manifest()
	# settings['versions'] = updater_info['metadata']['versions']

	# settings['probe_settings'] = {}
	# settings['probe_settings']['probe_profiles'] = _default_probe_profiles()
	# settings['probe_settings']['probe_map'] = default_probe_map(settings['probe_settings']['probe_profiles'])

	# settings['globals'] = {
	# 	'grill_name' : '',
	# 	'debug_mode' : False,
	# 	'page_theme' : 'light',
	# 	'triggerlevel' : 'LOW',
	# 	'buttonslevel' : 'HIGH',
	# 	'disp_rotation' : 0,
	# 	'dc_fan': False,
	# 	'standalone': True,
	# 	'units' : 'F',
	# 	'augerrate' : 0.3,  		# (grams per second) default auger load rate is 10 grams / 30 seconds
	# 	'first_time_setup' : True,  # Set to True on first setup, to run wizard on load 
	# 	'ext_data' : False,  # Set to True to allow tracking of extended data.  More data will be stored in the history database and can be reviewed in the CSV.
	# 	'global_control_panel' : False,  # Set to True to display control panel on most pages (except Updater, Wizard, Cookfile and some other pages)
	# 	'boot_to_monitor' : False,  # Set to True to boot directly into monitor mode
	# 	'prime_ignition' : False,  # Set to True to enable the igniter in prime & startup mode
	# 	'updated_message' : False,   # Set to True to display a pop-up message after the system has been updated 
	# 	'venv' : False,  # Set to True if running in virtual environment (needed for Raspberry Pi OS Bookworm)
	# 	'real_hw' : True  # Set to True if running on real hardware (i.e. Raspberry Pi), False if running in a test environment 
	# }

	# if os.path.exists('bin'):
	# 	settings['globals']['venv'] = True 

	# settings['outpins'] = {
	# 	'power' : 4,
	# 	'auger' : 14,
	# 	'fan' : 15,
	# 	'igniter' : 18,
	# 	'dc_fan' : 26,
	# 	'pwm' : 13
	# }

	# settings['inpins'] = { 'selector' : 17 }

	# settings['dev_pins'] = {	# Device Pin Assignment
	# 	'input': {
	# 		'up_clk': 16,		# Up Button or CLK for encoder
	# 		'enter_sw' : 21,	# Enter Button or SW for encoder
	# 		'down_dt' : 20		# Down Button or DT for encoder
	# 	},
	# 	'display': {
	# 		'led' : 5,			# ILI9341: LED	- ST7789: BL
	# 		'dc' : 24,			# ILI9341: DC	- ST7789: DC
	# 		'rst' : 25			# ILI9341: RST	- ST7789: RST
	# 	},
	# 	'distance': {
	# 		'trig': 23,			# For hcsr04
	# 		'echo' : 27			# For hcsr04
	# 	},
	# }

	# settings['cycle_data'] = {
	# 	'HoldCycleTime' : 25,
	# 	'SmokeOnCycleTime' : 15,  # Smoke/Startup Auger On Time.
	# 	'SmokeOffCycleTime' : 45,  # Smoke/Startup Auger Off Time.  Starting value for PMode (10s is added for each PMode setting)
	# 	'PMode' : 2,  			# http://tipsforbbq.com/Definition/Traeger-P-Setting
	# 	'u_min' : 0.1,
	# 	'u_max' : 0.9,
	# 	'LidOpenDetectEnabled' : False,  #  Enable Lid Open Detection
	# 	'LidOpenThreshold' : 15,	 #  Percentage drop in temperature from the hold temp, to trigger lid open event
	# 	'LidOpenPauseTime' : 60  #  Number of seconds to pause when a lid open event is detected 
	# }

	# settings['controller'] = {
	# 	'selected' : 'pid'
	# }

	# settings['controller']['config'] = _default_controller_config()

	# settings['display'] = {
	# 	'selected' : 'none'
	# }
	# settings['display']['config'] = _default_display_config()

	# settings['keep_warm'] = {
	# 	'temp' : 165,
	# 	's_plus' : False
	# }

	# settings['smoke_plus'] = {
	# 	'enabled' : False, 		# Sets default Enable/Disable (True = Enabled, False = Disabled)
	# 	'min_temp' : 160, 		# Minimum temperature to cycle fan on/off
	# 	'max_temp' : 220, 		# Maximum temperature to cycle fan on/off
	# 	'on_time' : 5, 			# Number of seconds the fan will remain ON
	# 	'off_time' : 5, 		# Number of seconds the fan will remain OFF
	# 	'duty_cycle' : 75, 		# Duty cycle that will be used during fan ramping. 20-100%
	# 	'fan_ramp' : False 		# If enabled fan will ramp up to speed instead of just turning on
	# }

	# settings['pwm'] = {
	# 	'pwm_control': False,
	# 	'update_time' : 10,
	# 	'frequency' : 25000,	# PWM Fan Frequency. Intel 4-wire PWM spec specifies 25 kHz
	# 	'min_duty_cycle' : 20, 	# This is the minimum duty cycle that can be set. Some fans stall below a certain speed
	# 	'max_duty_cycle' : 100, # This is the maximum duty cycle that can be set. Can limit fans that are overpowered
	# 	'temp_range_list' : [3, 7, 10, 15],  # Temp Bands for Each Profile
	# 	'profiles' : [
	# 		{
	# 			'duty_cycle' : 20 		# Duty Cycle to set fan
	# 		},
	# 		{
	# 			'duty_cycle' : 35
	# 		},
	# 		{
	# 			'duty_cycle' : 50
	# 		},
	# 		{
	# 			'duty_cycle' : 75
	# 		},
	# 		{
	# 			'duty_cycle' : 100
	# 		}
	# 	]
	# }

	# settings['safety'] = {
	# 	'minstartuptemp' : 75, 	# User Defined. Minimum temperature allowed for startup.
	# 	'maxstartuptemp' : 100, # User Defined. Take this value if the startup temp is higher than maxstartuptemp
	# 	'maxtemp' : 550, 		# User Defined. If temp exceeds value in any mode, shut off. (including monitor mode)
	# 	'reigniteretries' : 1, 	# Number of tries to reignite grill if it has gone below the safe temp (0 to disable)
	# 	'startup_check' : True	# True = Enabled
	# }

	# settings['pelletlevel'] = {
	# 	'warning_enabled' : True,
	# 	'warning_level' : 25,	# Percent to begin low pellet warning notifications
	# 	'warning_time' : 20,	# Number of minutes to check for low pellets and send notification
	# 	'empty' : 22, 			# Number of centimeters from the sensor that indicates empty
	# 	'full' : 4  			# Number of centimeters from the sensor that indicates full
	# }

	# settings['modules'] = {
	# 	'grillplat' : 'prototype',
	# 	'display' : 'none',
	# 	'dist' : 'none'
	# }

	# settings['lastupdated'] = {
	# 	'time' : math.trunc(time.time())
	# }

	# settings['startup'] = {
	# 	'duration' : 240,  # Default startup time (seconds)
	# 	'prime_on_startup' : 0,  # Prime Amount (grams) [0 = disabled]
	# 	'startup_exit_temp' : 0,  # Exit startup at this temperature threshold. [0 = disabled]
	# 	'start_to_mode' : {
	# 		'after_startup_mode' : 'Smoke',  # Transition to this mode after startup completes
	# 		'primary_setpoint' : 165  # If Hold, set the setpoint
	# 	},
	# 	'smartstart' : {
	# 		'enabled' : False,   # Disable Smart Start by default on new installations
	# 		'exit_temp' : 120,  # Exit temperature - exits smart start if this temperature is achieved 
	# 		'temp_range_list' : [60, 80, 90],  # Min Temps for Each Profile
	# 		'profiles' : [
	# 			{
	# 				'startuptime' : 360,  
	# 				'augerontime' : 15,
	# 				'p_mode' : 0
	# 			},
	# 			{
	# 				'startuptime' : 360,  
	# 				'augerontime' : 15,
	# 				'p_mode' : 1
	# 			},
	# 			{
	# 				'startuptime' : 240,  
	# 				'augerontime' : 15,
	# 				'p_mode' : 3
	# 			},
	# 			{
	# 				'startuptime' : 240,  
	# 				'augerontime' : 15,
	# 				'p_mode' : 5
	# 			}
	# 		]
	# 	}
	# }

	# settings['shutdown'] = {
	# 	'shutdown_duration' : 240,  # Default Shutdown time (seconds)
	# 	'auto_power_off' : False  # Power off the system after shutdown (False = disabled)
	# }

	# settings['dashboard'] = {
	# 	'current' : 'Default', 
	# 	'dashboards' : {
	# 		'Default' : {	
	# 			'name' : 'Default',
	# 			'friendly_name' : 'Default Dashboard', 
	# 			'html_name' : 'dash_default.html',
	# 			'custom' : {
	# 				'hidden_cards' : []
	# 			},
	# 			'config' : {}
	# 		},
	# 		'Basic' : {	
	# 			'name' : 'Basic',
	# 			'friendly_name' : 'Basic Dashboard', 
	# 			'html_name' : 'dash_basic.html',
	# 			'custom' : {
	# 				'hidden_cards' : []
	# 			},
	# 			'config' : {}
	# 		}
	# 	}
	# }

	# settings['notify_services'] = default_notify_services()

	# settings['history_page'] = {
	# 	'minutes' : 15, 				# Sets default number of minutes to show in history
	# 	'clearhistoryonstart' : True, 	# Clear history when StartUp Mode selected
	# 	'autorefresh' : 'on', 			# Sets history graph to auto refresh ('live' graph)
	# 	'datapoints' : 60, 				# Number of data points to show on the history chart
	# 	'probe_config' : {}				# Empty probe config
	# }
	# settings['history_page']['probe_config'] = default_probe_config(settings)

	# settings['recipe'] = {}
	# settings['recipe']['probe_map'] = _default_recipe_probe_map(settings)

	#return settings

# def _default_display_config():
# 	display_metadata = read_generic_json('./wizard/wizard_manifest.json')
# 	display_metadata = display_metadata['modules']['display']

# 	config = {}
# 	for display in display_metadata:
# 		config[display] = {}
# 		for option in display_metadata[display]['config']:
# 			config[display][option['option_name']] = option['default']

# 	return config

def default_control():
	settings = read_settings()
	control = {}
	control['settings_update'] = False
	control['updated'] = True
	control['mode'] = 'Stop'
	control['status'] = ''
	control['next_mode'] = 'Stop'
	control['curr_speed'] = 0.0
	control['avg_speed'] = 0.0
	control['distance'] = 0.0
	control['mode'] = 'Stop'
	control['next_mode'] = 'Stop'
	control['status'] = ''
	control['errors'] = []
	control['system'] = {}

	return(control)

# """
# List of Tuples ('metric_key', default_value)
#  - This structure will be used to build the default metrics structure, and to export the data easily
#  - To add a metric, simply add a tuple to this list.  
# """
# metrics_items = [ 
# 	('id', 0),
# 	('starttime', 0),
# 	('starttime_c', 0),  		# Converted Start Time
# 	('endtime', 0),
# 	('endtime_c', 0),  			# Converted End Time
# 	('timeinmode', 0),  		# Calculated Time in Mode
# 	('mode', ''),  
# 	('augerontime', 0), 
# 	('augerontime_c', 0), 		# Converted Auger On Time
# 	('estusage_m', ''),  		# Estimated pellet usage in metric (grams)
# 	('estusage_i', ''),  		# Estimated pellet usage in pounds (and ounces)
# 	('fanontime', 0),
# 	('fanontime_c', 0),  		# Converted Fan On Time
# 	('smokeplus', True), 
# 	('primary_setpoint', 0),
# 	('smart_start_profile', 0), # Smart Start Profile Selected
# 	('startup_temp', 0), # Smart Start Start Up Temp
# 	('p_mode', 0), # P_mode selected
# 	('auger_cycle_time', 0),  # Auger Cycle Time
# 	('pellet_level_start', 0),  # Pellet Level at the begining of this mode
# 	('pellet_level_end', 0),  # Pellet Level at the end of this mode
# 	('pellet_brand_type', '')  # Pellet Brand and Wood Type 
# ]

# def default_metrics():
# 	metrics = {}

# 	for index in range(0, len(metrics_items)):
# 		metrics[metrics_items[index][0]] = metrics_items[index][1]

# 	return(metrics)

def read_control(flush=False):
	"""
	Read Control from Redis DB

	:param flush: True to clean control. False otherwise
	:return: control
	"""
	global cmdsts

	try:
		if flush:
			# Remove all control structures in Redis DB (not history or current)
			cmdsts.delete('control:general')
			#cmdsts.delete('control:command')
			# The following set's no persistence so that we don't get writes to the disk / SDCard 
			cmdsts.config_set('appendonly', 'no')
			cmdsts.config_set('save', '')

			control = default_control()
			write_control(control, direct_write=True, origin='common')
		else: 
			control = json.loads(cmdsts.get('control:general'))
	except:
		control = default_control()

	return(control)

def write_control(control, direct_write=False, origin='unknown'):
	"""
	Write Control to Redis DB

	:param control: Control Dictionary
	:param direct_write:  If set to true, write directly to the control data.  Else, write the control data to a command queue.  Defaults to false.  
	"""
	global cmdsts

	if direct_write: 
		cmdsts.set('control:general', json.dumps(control))
	else: 
		# Add changes to control write queue 
		control['origin'] = origin 
		cmdsts.rpush('control:write', json.dumps(control))

def execute_control_writes():
	"""
	Execute Control Writes in Queue from Redis DB

	:param None

	:return status : 'OK', 'ERROR' 
	"""
	global cmdsts 

	status = 'OK'
	while cmdsts.llen('control:write') > 0:
		control = read_control()
		command = json.loads(cmdsts.lpop('control:write'))
		command.pop('origin')
		control = deep_update(control, command)
		write_control(control, direct_write=True, origin='writer')
	return status

def read_errors(flush=False):
	"""
	Read Errors from Redis DB

	:param flush: True to clear errors. False otherwise
	:return: errors
	"""
	global cmdsts

	try:
		if flush:
			# Remove all error structures in Redis DB
			cmdsts.delete('errors')

			errors = []
			write_errors(errors)
		else: 
			errors = json.loads(cmdsts.get('errors'))
	except:
		errors = ['Unable to reach Redis database.  You may need to reinstall PiCycle or enable redis-server.']

	return(errors)

def write_errors(errors):
	"""
	Write Errors to Redis DB

	:param errors: Errors
	"""
	global cmdsts

	cmdsts.set('errors', json.dumps(errors))

def read_warnings():
	"""
	Read Warnings from Redis DB and then burn them

	:return: warnings
	"""
	global cmdsts

	try:
		if not(cmdsts.exists('warnings')):
			warnings = []
		else:
			# Read list of warnings 
			warnings = cmdsts.lrange('warnings', 0, -1)
			# Remove all warnings in Redis DB
			cmdsts.delete('warnings')
	except:
		warnings = ['Unable to reach Redis database.  You may need to reinstall PiCycle or enable redis-server.']
		#write_log(warnings[0])

	return warnings

def write_warning(warning):
	"""
	Write a warning to Redis DB

	:param warnings: Warnings List 
	"""
	global cmdsts

	try:
		cmdsts.rpush('warnings', warning)
	except:
		event = 'Unable to reach Redis database.  You may need to reinstall PiCycle or enable redis-server.'
		#write_log(event)

# def read_metrics(all=False):
# 	"""
# 	Read Metrics from Redis DB

# 	:param all: True to read entire list. False for top of list.
# 	"""
# 	global cmdsts

# 	if not(cmdsts.exists('metrics:general')):
# 		write_metrics(flush=True)
# 		return([])
	
# 	if all: 
# 		# Read entire list of Metrics
# 		llength = cmdsts.llen('metrics:general')
# 		metrics = cmdsts.lrange('metrics:general', 0, -1)
# 		metrics_list = []
# 		for index in range(0, llength):
# 			metrics_list.append(json.loads(metrics[index]))
# 		return(metrics_list)
	
# 	# Read current Metrics Record (i.e. top of the list)
# 	return(json.loads(cmdsts.lindex('metrics:general', -1)))

# def write_metrics(metrics=default_metrics(), flush=False, new_metric=False):
# 	"""
# 	Write metrics to Redis DB

# 	:param metrics: Metrics Data
# 	:param flush: True to clear metrics. False otherwise
# 	:param new_metric:
# 	"""
# 	global cmdsts

# 	if(flush or not(cmdsts.exists('metrics:general'))):
# 		# Remove all metrics structures in Redis DB
# 		cmdsts.delete('metrics:general')

# 		# The following set's no persistence so that we don't get writes to the disk / SDCard 
# 		cmdsts.config_set('appendonly', 'no')
# 		cmdsts.config_set('save', '')
# 		if not flush:
# 			new_metric=True
# 		else:
# 			return

# 	if new_metric:
# 		metrics['starttime'] = time.time() * 1000
# 		metrics['id'] = generate_uuid()
# 		cmdsts.rpush('metrics:general', json.dumps(metrics))
# 	else: 
# 		cmdsts.rpop('metrics:general')
# 		cmdsts.rpush('metrics:general', json.dumps(metrics))

def read_settings(filename='settings.json', init=False, retry_count=0):
	"""
	Read Settings from file

	:param filename: Filename to use (default settings.json)
	"""

	try:
		json_data_file = os.fdopen(os.open(filename, os.O_RDONLY))
		json_data_string = json_data_file.read()
		settings = json.loads(json_data_string)
		json_data_file.close()

	except(IOError, OSError):
		""" Settings file not found, create a new default settings file """
		#settings = default_settings()
		#write_settings(settings)
		return(settings)
	except(ValueError):
		# A ValueError Exception occurs when multiple accesses collide, this code attempts a retry.
		event = 'ERROR: Value Error Exception - JSONDecodeError reading settings.json'
		#write_log(event)
		json_data_file.close()
		# Retry Reading Settings
		if retry_count < 5: 
			settings = read_settings(filename=filename, retry_count=retry_count+1)
		else:
			pass
			#""" Undefined settings file load error, indicates corruption """
			# settings_default = default_settings()
			# settings = restore_settings(settings_default)
			# init = True
			# write_settings(settings)
 
	#if init:
		# Get latest settings format
		#settings_default = default_settings()

		# Overlay the read values over the top of the default settings
		#  This ensures that any NEW fields are captured.  
		#update_settings = False # set flag in case an update needs to be written back

		# Prevent the wizard from popping up on existing installations
		# if 'first_time_setup' not in settings['globals'].keys():
		# 	settings['globals']['first_time_setup'] = False
		# 	update_settings = True

		# If default version is different from what is currently saved, update version in saved settings
		# if 'versions' not in settings.keys():
		# 	''' Upgrading from extremely old version '''
		# 	settings['versions'] = settings_default['versions']
		# 	update_settings = True
		# elif semantic_ver_is_lower(settings['versions']['server'], settings_default['versions']['server']):
		# 	''' Upgrade Path '''
		# 	backup_settings()  # Backup Old Settings Before Performing Upgrade
		# 	warning = f'Upgrading your settings from {settings["versions"]["server"]} to {settings_default["versions"]["server"]}.'
		# 	write_warning(warning)
		# 	write_log(warning)
		# 	prev_ver = semantic_ver_to_list(settings['versions']['server'])
		# 	settings = upgrade_settings(prev_ver, settings, settings_default)
		# 	settings['versions'] = settings_default['versions']
		# 	update_settings = True
		# elif semantic_ver_is_lower(settings_default['versions']['server'], settings['versions']['server']):
		# 	''' Downgrade Path '''			
		# 	backup_settings()  # Backup Old Settings Before Performing Downgrade 
		# 	settings = downgrade_settings(settings, settings_default)
		# 	update_settings = True
		# elif (settings_default['versions']['server'] == settings['versions']['server']) and (settings['versions']['build'] < settings_default['versions']['build']):
		# 	''' Minor Upgrade Path '''
		# 	prev_ver = semantic_ver_to_list(settings['versions']['server'])
		# 	settings = upgrade_settings(prev_ver, settings, settings_default)
		# 	settings['versions'] = settings_default['versions']
		# 	update_settings = True

		# if settings['versions'].get('build', None) != settings_default['versions']['build']:
		# 	settings['versions']['build'] = settings_default['versions']['build']
		# 	update_settings = True 

		# # Overlay the original settings on top of the default settings
		# settings = deep_update(settings_default, settings)
		update_settings = True
		# settings['history_page']['probe_config'] = default_probe_config(settings)  # Fix issue with probe_configs resetting to defaults

		# if update_settings or filename != 'settings.json': # If any of the keys were added, then write back the changes
		# 	write_settings(settings)

	return(settings)

def write_settings(settings):
	"""
	Write all settings to JSON file

	:param settings: Settings

	"""
	settings['globals']['lastupdated'] = math.trunc(time.time())

	json_data_string = json.dumps(settings, indent=2, sort_keys=True)
	with open("settings.json", 'w') as settings_file:
		settings_file.write(json_data_string)

# def backup_settings():
# 	# Copy current settings file to a backup copy in /[BACKUP_PATH]/PiCycle_[DATE]_[TIME].json 
# 	time_now = datetime.datetime.now()
# 	time_str = time_now.strftime('%m-%d-%y_%H%M%S') # Truncate the microseconds
# 	backup_file = BACKUP_PATH + 'PiCycle_' + time_str + '.json'
# 	os.system(f'cp settings.json {backup_file}')
# 	# Save a path to the backup copy in the updater_manifest.json
# 	backup_manifest = read_generic_json('./backups/manifest.json')
# 	if backup_manifest == {}:
# 		backup_manifest = {
# 			'server_settings' : {}
# 		}
# 		write_generic_json(backup_manifest, './backups/manifest.json')

# 	settings = read_generic_json('settings.json')
# 	server_version = settings['versions']['server']
# 	backup_manifest['server_settings'][server_version] = backup_file
# 	write_generic_json(backup_manifest, 'backups/manifest.json')
# 	warning = f'Backed up your current settings to "{backup_file}" and setting these as the recovery settings for server version: {server_version}.'
# 	write_warning(warning)
# 	write_log(warning)
# 	return backup_file 

# def restore_settings(settings_default):
# 	''' Look for backup file to restore from '''
# 	backup_manifest = read_generic_json('./backups/manifest.json')
# 	if backup_manifest == {}:
# 		backup_manifest = {
# 			'server_settings' : {},
# 			'pelletdb' : {
# 				'current' : ''
# 			}
# 		}
# 		write_generic_json(backup_manifest, './backups/manifest.json')
# 	server_version = settings_default['versions']['server']
# 	backup_settings_file = backup_manifest['server_settings'].get(server_version, None)
# 	if backup_settings_file is not None:
# 		warning = f'Something failed when reading the "settings.json" file.  Restoring settings from the following backup settings file: {backup_settings_file}.'
# 		settings = read_settings(filename=backup_settings_file)
# 	else: 
# 		warning = f'Something failed when reading the "settings.json" file.  Resetting settings to defaults, since no backup settings files were found.'
# 		settings = settings_default
# 	write_warning(warning)
# 	write_log(warning)
# 	return settings

# def upgrade_settings(prev_ver, settings, settings_default):
# 	''' Check if upgrading from v1.4.x or earlier '''
# 	if prev_ver[0] <=1 and prev_ver[1] <= 4:
# 		settings['versions'] = settings_default['versions']
# 		settings['globals']['first_time_setup'] = True  # Force configuration for probes
# 		settings['startup']['start_to_mode']['primary_setpoint'] = settings['start_to_mode']['grill1_setpoint']
# 		settings['start_to_mode'].pop('grill1_setpoint')
# 		settings['dashboard'] = settings_default['dashboard']
# 		# Move Notification Settings
# 		settings['notify_services'] = {}
# 		for key in settings_default['notify_services'].keys():
# 			settings['notify_services'][key] = settings[key]
# 		settings['probe_settings'].pop('probe_options')
# 		settings['probe_settings'].pop('probe_sources')
# 		settings['probe_settings'].pop('probes_enabled')
# 		settings['modules'].pop('adc')
# 		# Add ID to probe_profiles
# 		for profile in settings['probe_settings']['probe_profiles']:
# 			if 'id' not in settings['probe_settings']['probe_profiles'][profile].keys():
# 				settings['probe_settings']['probe_profiles'][profile]['id'] = profile
# 	if prev_ver[0] <=1 and prev_ver[1] <= 5:
# 		# if moving from v1.5 to v1.6, force a first-time setup to drive changes to the probe device setup
# 		settings['globals']['first_time_setup'] = True
# 		settings['cycle_data'].pop('SmokeCycleTime') # Remove old SmokeCycleTime
# 		settings['cycle_data']['SmokeOnCycleTime'] = 15  # Name change for SmokeCycleTime variable 
# 		settings['cycle_data']['SmokeOffCycleTime'] = 45  # Added SmokeOffCycleTime variable 
# 	''' Check if upgrading from v1.6.x or v1.7.0 build 7 '''
# 	if (prev_ver[0] <=1 and prev_ver[1] <= 6) or (prev_ver[0] ==1 and prev_ver[1] == 7 and settings['versions'].get('build', 0) <= 7):
# 		settings['dashboard'] = settings_default['dashboard']
# 	''' Check if upgrading from v1.7.0 build 45 '''
# 	if (prev_ver[0] <=1 and prev_ver[1] <= 6) or (prev_ver[0] ==1 and prev_ver[1] == 7 and settings['versions'].get('build', 0) <= 45):
# 		# Move startup defaults to new 'startup' section of settings 
# 		settings['startup'] = settings_default['startup']
# 		settings['startup']['duration'] = settings['globals'].get('startup_timer', settings_default['startup']['duration'])
# 		settings['globals'].pop('startup_timer', None)
# 		settings['startup']['startup_exit_temp'] = settings['globals'].get('startup_exit_temp', settings_default['startup']['startup_exit_temp'])
# 		settings['globals'].pop('startup_exit_temp', None)
# 		settings['startup']['start_to_mode'] = settings.get('start_to_mode', settings_default['startup']['start_to_mode'])
# 		settings.pop('start_to_mode', None)
# 		settings['startup']['smartstart'] = settings.get('smartstart', settings_default['startup']['smartstart'])
# 		settings.pop('smartstart', None)
# 		settings['shutdown'] = settings_default['shutdown']
# 		settings['shutdown']['shutdown_duration'] = settings['globals'].get('shutdown_timer', settings_default['shutdown']['shutdown_duration'])
# 		settings['globals'].pop('shutdown_timer', None)
# 		settings['shutdown']['auto_power_off'] = settings['globals'].get('auto_power_off', settings_default['shutdown']['auto_power_off'])
# 		settings['globals'].pop('auto_power_off', None)

# 	''' Import any new probe profiles '''
# 	for profile in list(settings_default['probe_settings']['probe_profiles'].keys()):
# 		if profile not in list(settings['probe_settings']['probe_profiles'].keys()):
# 			settings['probe_settings']['probe_profiles'][profile] = settings_default['probe_settings']['probe_profiles'][profile]

# 	settings['globals']['updated_message'] = True  # Display updated message after reset/reboot
# 	return(settings)

# def downgrade_settings(settings, settings_default):
# 	''' Look for backup file for the downgrade '''
# 	backup_manifest = read_generic_json('./backups/manifest.json')
# 	if backup_manifest == {}:
# 		backup_manifest = {
# 			'server_settings' : {},
# 			'pelletdb' : {
# 				'current' : ''
# 			}
# 		}
# 		write_generic_json(backup_manifest, './backups/manifest.json')
# 	server_version = settings_default['versions']['server']
# 	backup_settings_file = backup_manifest['server_settings'].get(server_version, None)
# 	if backup_settings_file is not None:
# 		warning = f'Downgrade server version detected. [{settings["versions"]["server"]} -> {settings_default["versions"]["server"]}] Restoring settings from the following backup settings file: {backup_settings_file}.'
# 		settings = read_settings(filename=backup_settings_file)
# 	else: 
# 		warning = f'Downgrade server version detected. [{settings["versions"]["server"]} -> {settings_default["versions"]["server"]}] Resetting settings to defaults, since no backup settings files were found.'
# 		settings = settings_default
# 	write_warning(warning)
# 	write_log(warning)
# 	return(settings)

# def read_events(legacy=True):
# 	"""
# 	Read event.log and populate an array of events.

# 	if legacy=true:
# 	:return: (event_list, num_events)

# 	if legacy=false:
# 	:return: (event_list, num_events)
# 	"""
# 	# Read all lines of events.log into a list(array)
# 	try:
# 		with open('/tmp/events.log') as event_file:
# 			event_lines = event_file.readlines()
# 			event_file.close()
# 	# If file not found error, then create events.log file
# 	except(IOError, OSError):
# 		event_file = open('/tmp/events.log', "w")
# 		event_file.close()
# 		event_lines = []

# 	# Initialize event_list list
# 	event_list = []

# 	# Get number of events
# 	num_events = len(event_lines)

# 	if legacy:
# 		for x in range(num_events):
# 			event_list.insert(0, event_lines[x].split(" ",2))

# 		# Error handling if number of events is less than 10, fill array with empty
# 		if num_events < 10:
# 			for line in range((10-num_events)):
# 				event_list.append(["--------","--:--:--","---"])
# 			num_events = 10
# 	else:
# 		for x in range(num_events):
# 			event_list.append(event_lines[x].split(" ",2))
# 		return event_list

# 	return(event_list, num_events)

# def read_log_file(filepath):
# 	# Read all lines of events.log into a list(array)
# 	try:
# 		with open(filepath) as log_file:
# 			log_file_lines = log_file.readlines()
# 			log_file.close()
# 	# If file not found error, then create events.log file
# 	except(IOError, OSError):
# 		event = f'Unable to open log file: {filepath}'
# 		write_log(event)
# 		return []

# 	return log_file_lines 

# def add_line_numbers(event_list):
# 	event_lines = []
# 	for index, line in enumerate(event_list):
# 		event_lines.append([index, line])
# 	return event_lines 

# def write_log(event):
# 	"""
# 	Write event to event.log

# 	:param event: String event
# 	"""
# 	log_level = logging.INFO
# 	eventLogger = create_logger('events', filename='/tmp/events.log', messageformat='%(asctime)s [%(levelname)s] %(message)s', level=log_level)
# 	eventLogger.info(event)

# def write_event(settings, event):
# 	"""
# 	Send event to log and console if debug mode enabled or only to log if
# 	string does not begin with *

# 	:param settings: Settings
# 	:param event: String event
# 	"""
# 	if settings['globals']['debug_mode']:
# 		print(event)
# 		write_log(event)
# 	elif not event.startswith('*'):
# 		write_log(event)

# def read_history(num_items=0, flushhistory=False):
# 	"""
# 	Read history from Redis DB and populate a list of data

# 	:param num_items: Items from end of the history (set to 0 for all items)
# 	:param flushhistory: True=flush history & current, False=normal history read
# 	:return: List of history dictionaries (each list item is timestamped 'T')
# 	"""
# 	global cmdsts
	
# 	datalist = []  # Initialize data list

# 	# If a flushhistory is requested, then flush the control:history key (and data)
# 	if flushhistory:
# 		if cmdsts.exists('control:history'):
# 			cmdsts.delete('control:history')  # deletes the history
# 			read_current(zero_out=True)  # zero-out current data
# 			write_metrics(flush=True)
# 	else:
# 		if cmdsts.exists('control:history'):
# 			list_length = cmdsts.llen('control:history') 

# 			if((num_items > 0) and (list_length < num_items)) or (num_items == 0):
# 				list_start = 0
# 			else: 
# 				list_start = list_length - num_items

# 			data = cmdsts.lrange('control:history', list_start, -1)
			
# 			''' Unpack data to list of dictionaries '''
# 			for index in range(len(data)):
# 				datalist.append(json.loads(data[index]))
			
# 	return(datalist)

# def unpack_history(datalist):
# 	temp_dict = {}  # Create temporary dictionary to store all of the history data lists
# 	temp_struct = datalist[0]  # Load the initial history data into a temporary dictionary  
# 	for key in temp_struct.keys():  # Iterate each of the keys
# 		if key in ['P', 'F', 'NT', 'EXD', 'AUX']:
# 			temp_dict[key] = {}
# 			for subkey in temp_struct[key]:
# 				temp_dict[key][subkey] = []
# 		else: 
# 			temp_dict[key] = []  # Create an empty list for any other keys ('T', 'PSP')

# 	for index in range(len(datalist)):
# 		temp_struct = datalist[index]
# 		for key, value in temp_struct.items():
# 			if key in ['P', 'F', 'NT', 'EXD', 'AUX']:
# 				for subkey, subvalue in temp_struct[key].items():
# 					temp_dict[key][subkey].append(subvalue)
# 			else: 
# 				temp_dict[key].append(value)  # Append list for any other keys ('T', 'PSP')
# 	return temp_dict

# def write_history(in_data, maxsizelines=28800, ext_data=False):
# 	"""
# 	Write History to Redis DB

# 	:param in_data: History data to be written to the database 
# 	:param maxsizelines: Maximum Line Size (Default 28800)
# 	:param ext_data: Extended data to be written to the databse 
# 	"""
	
# 	global cmdsts

# 	# Create data structure for current temperature data and timestamp
# 	datastruct = {}
# 	datastruct['T'] = int(time.time() * 1000)
# 	datastruct['P'] = in_data['probe_history']['primary']  # Contains primary probe temperature [key:value]
# 	datastruct['F'] = in_data['probe_history']['food']  # Contains food probe temperature(s) [key:value pairs]
# 	datastruct['PSP'] = in_data['primary_setpoint']  # Setpoint for the primary probe (non-notify setpoint) [value]
# 	datastruct['NT'] = in_data['notify_targets']  # Notification Target Temps for all probes
# 	datastruct['AUX'] = in_data['probe_history']['aux']  # Contains auxilliary probe temperature history [key:value]

# 	if ext_data:
# 		datastruct['EXD'] = in_data['ext_data']

# 	# Push data string to the list in the last position
# 	cmdsts.rpush('control:history', json.dumps(datastruct))

# 	# Check if the list has exceeded maxsizelines, and pop the first item from the list if it has
# 	if cmdsts.llen('control:history') > maxsizelines:
# 		cmdsts.lpop('control:history')


def write_current(in_data):
	"""
	Write current and populate a dictionary of data

	:param in_data: dictionary containing current ride info
	"""
	global cmdsts

	current = {}
	current['curr_speed'] = in_data['curr_speed']
	current['avg_speed'] = in_data['avg_speed']
	current['distance'] = in_data['distance']
	current['mode'] = in_data['mode']
	current['timestamp'] = int(time.time() * 1000) 

	cmdsts.set('control:current', json.dumps(current))

def read_current(zero_out=False):
	"""
	Read current and populate a list of data

	:param zero_out: True to zero out current. False otherwise
	:return: Current probe temps structure
	"""
	global cmdsts

	if zero_out:
		settings = read_settings()
		current = {
			'curr_speed' : 0, 
			'avg_speed' : 0,
			'distance' : 0,
			'mode' : 0,
			'timestamp' : 0
		}

		cmdsts.set('control:current', json.dumps(current))

	if not cmdsts.exists('control:current'):
		current = {}
	else:
		current = json.loads(cmdsts.get('control:current'))
	
	return(current)

# def prepare_csv(data=[], filename=''):
# 	# Create filename if no name specified
# 	if(filename == ''):
# 		now = datetime.datetime.now()
# 		filename = now.strftime('%Y%m%d-%H%M') + '-PiCycle-Export'
# 	else:
# 		filename = filename.replace('.json', '')
# 		filename = filename.replace('./history/', '')
# 		filename += '-Pifire-Export'
	
# 	exportfilename = '/tmp/' + filename + ".csv"
	
# 	# Open CSV File for editing
# 	csvfile = open(exportfilename, "w")

# 	if(data == []):
# 		data = read_history()

# 	exd_data = True if 'EXD' in data[0].keys() else False 

# 	# Set Standard Labels 
# 	labels = 'Time, '
# 	primary_key = list(data[0]['P'].keys())[0]
# 	labels += f'{primary_key} Temp, {primary_key} Set Point, {primary_key} Notify Target' 
# 	for key in data[0]['F']:
# 		labels += f', {key} Temp, {key} Notify Target'
# 	for key in data[0]['AUX']:
# 		labels += f', {key} Temp'
# 	if exd_data: 
# 		for key in data[0]['EXD']:
# 			labels += f', {key}'

# 	# End the labels line
# 	labels += '\n'

# 	# Get the length of the data (number of captured events)
# 	list_length = len(data)

# 	if(list_length > 0):
# 		writeline = labels
# 		csvfile.write(writeline)

# 		for index in range(0, list_length):
# 			converted_dt = datetime.datetime.fromtimestamp(int(data[index]['T']) / 1000)
# 			timestr = converted_dt.strftime('%Y-%m-%d %H:%M:%S')
# 			writeline = f"{timestr}, {data[index]['P'][primary_key]}, {data[index]['PSP']}, {data[index]['NT'][primary_key]}"
# 			for key in data[index]['F']:
# 				writeline += f", {data[index]['F'][key]}, {data[index]['NT'][key]}"
# 			for key in data[index]['AUX']:
# 				writeline += f", {data[index]['AUX'][key]}"
# 			# Add any additional data if keys exist
# 			if exd_data: 
# 				for key in data[index]['EXD']:
# 					writeline += f", {data[index]['EXD'][key]}"
# 			# Write line to file
# 			csvfile.write(writeline + '\n')
# 	else:
# 		writeline = 'No Data\n'
# 		csvfile.write(writeline)

# 	csvfile.close()

# 	return(exportfilename)

def is_real_hardware(settings=None):
	"""
	Check if running on real hardware as opposed to a prototype/test environment.

	:return: True if running on real hardware (i.e. Raspberry Pi), else False. 
	"""
	if settings == None:
		settings = read_settings()

	return True if settings['globals']['real_hw'] else False 

def restart_scripts():
	"""
	Restart the Control and WebApp Scripts
	"""
	if is_real_hardware():
		os.system("sleep 3 && sudo service supervisor restart &")

def reboot_system():
	"""
	Reboot the system
	"""
	if is_real_hardware():
		os.system("sleep 3 && sudo reboot &")

def shutdown_system():
	"""
	Shutdown the system
	"""
	if is_real_hardware():
		os.system("sleep 3 && sudo shutdown -h now &")

# def read_updater_manifest(filename='updater/updater_manifest.json'):
# 	"""
# 	Read Updater Manifest Data from file

# 	:param filename: updater_manifest.json filename
# 	:return: Dependencies
# 	"""
# 	try:
# 		json_data_file = os.fdopen(os.open(filename, os.O_RDONLY))
# 		json_data_string = json_data_file.read()
# 		dependencies = json.loads(json_data_string)
# 		json_data_file.close()
# 	except(IOError, OSError):
# 		event = 'ERROR: Could not read from updater manifest.'
# 		write_log(event)
# 		dependencies = {
# 			"dependencies" : {}
# 		}
# 		return(dependencies)
# 	except(ValueError):
# 		# A ValueError Exception occurs when multiple accesses collide, this code attempts a retry.
# 		event = 'ERROR: Value Error Exception - JSONDecodeError reading updater_manifest.json'
# 		write_log(event)
# 		json_data_file.close()
# 		# Retry Reading Settings
# 		dependencies = read_updater_manifest(filename=filename)

# 	return(dependencies)

# def get_updater_install_status():
# 	"""
# 	Read Updater Install Status from Redis DB

# 	:return: Wizard Updater (Percent, Status, Output)
# 	"""
# 	global cmdsts
# 	percent = cmdsts.get('updater:percent')
# 	status = cmdsts.get('updater:status')
# 	output = cmdsts.get('updater:output')
# 	return(percent, status, output)

# def set_updater_install_status(percent, status, output):
# 	"""
# 	Write Updater Install Status to Redis DB

# 	:param percent: Percent Complete
# 	:param status: Current Status
# 	:param output: Output
# 	"""
# 	global cmdsts
# 	cmdsts.set('updater:percent', percent)
# 	cmdsts.set('updater:status', status)
# 	cmdsts.set('updater:output', output)

# def process_metrics(metrics_data, augerrate=0.3):
# 	# Process Additional Metrics Information for Display
# 	for index in range(0, len(metrics_data)):
# 		# Convert Start Time
# 		starttime = metrics_data[index]['starttime']
# 		metrics_data[index]['starttime_c'] = epoch_to_time(starttime/1000)
# 		# Convert End Time
# 		if(metrics_data[index]['endtime'] == 0):
# 			endtime = 0
# 		else: 
# 			endtime = epoch_to_time(metrics_data[index]['endtime']/1000)
# 		metrics_data[index]['endtime_c'] = endtime
# 		# Time in Mode
# 		if(metrics_data[index]['mode'] == 'Stop'):
# 			timeinmode = 'NA'
# 		elif(metrics_data[index]['endtime'] == 0):
# 			timeinmode = 'Active'
# 		else:
# 			seconds = int((metrics_data[index]['endtime']/1000) - (metrics_data[index]['starttime']/1000))
# 			if seconds > 60:
# 				timeinmode = f'{int(seconds/60)} m {seconds % 60} s'
# 			else:
# 				timeinmode = f'{seconds} s'
# 		metrics_data[index]['timeinmode'] = timeinmode 
# 		# Convert Auger On Time
# 		metrics_data[index]['augerontime_c'] = str(int(metrics_data[index]['augerontime'])) + ' s'
# 		# Estimated Pellet Usage
# 		grams = int(metrics_data[index]['augerontime'] * augerrate)
# 		pounds = round(grams * 0.00220462, 2)
# 		ounces = round(grams * 0.03527392, 2)
# 		metrics_data[index]['estusage_m'] = f'{grams} grams'
# 		metrics_data[index]['estusage_i'] = f'{pounds} pounds ({ounces} ounces)'

# 	return(metrics_data)

def epoch_to_time(epoch):
	end_time =  datetime.datetime.fromtimestamp(epoch)
	return end_time.strftime("%H:%M:%S")

# def semantic_ver_to_list(version_string):
# 	# Count number of '.' in string
# 	decimal_count = version_string.count('.')
# 	ver_list = version_string.split('.')

# 	if decimal_count == 0:
# 		ver_list = [0, 0, 0]
# 	elif decimal_count < 2:
# 		ver_list.append('0')

# 	ver_list = list(map(int, ver_list))

# 	return(ver_list)

# def semantic_ver_is_lower(version_A, version_B):
# 	version_A = semantic_ver_to_list(version_A)
# 	version_B = semantic_ver_to_list(version_B)
	
# 	if version_A [0] < version_B[0]:
# 		return True
# 	elif version_A [0] > version_B[0]:
# 		return False
# 	else:
# 		if version_A [1] < version_B[1]:
# 			return True
# 		elif version_A [1] > version_B[1]:
# 			return False
# 		else:
# 			if version_A [2] < version_B[2]:
# 				return True
# 			elif version_A [2] > version_B[2]:
# 				return False
# 	return False

def seconds_to_string(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)

	if h > 0:
		time_string = f'{h}h {m}m {s}s'
	elif m > 0:
		time_string = f'{m}m {s}s'
	else: 
		time_string = f'{s}s'

	return time_string

def read_generic_json(filename):
	try:
		json_file = os.fdopen(os.open(filename, os.O_RDONLY))
		json_data = json_file.read()
		dictionary = json.loads(json_data)
		json_file.close()
	except: 
		dictionary = {}
		event = f'An error occurred loading {filename}'
		#write_log(event)

	return dictionary

def write_generic_json(dictionary, filename):
	try: 
		json_data_string = json.dumps(dictionary, indent=2, sort_keys=True)
		with open(filename, 'w') as json_file:
			json_file.write(json_data_string)
	except:
		event = f'Error writing generic json file ({filename})'
		#write_log(event)

# def write_status(status):
# 	"""
# 	Write Status to Redis DB

# 	:param status: Status Dictionary
# 	"""
# 	global cmdsts

# 	cmdsts.set('control:status', json.dumps(status))

# def read_status(init=False):
# 	"""
# 	Read Status dictionary from Redis DB
# 	"""
# 	global cmdsts

# 	if init:
# 		status = {
# 		  	"s_plus": False,
#   			"hopper_level": 100,
# 			"units": "F",
# 			"mode": "Stop",
# 			"recipe": False,
# 			"startup_timestamp" : 0,
# 			"start_time": 0,
# 			"start_duration": 0,
# 			"shutdown_duration": 0,
# 			"prime_duration": 0,
# 			"prime_amount": 0,
# 			"lid_open_detected": False,
# 			"lid_open_endtime": 0,
# 			"p_mode": 0,
# 			"recipe_paused": False,
# 			"outpins": {
# 				"auger": False,
# 				"fan": False,
# 				"igniter": False,
# 				"power": False
# 			}
# 		}
# 		write_status(status)
# 	else:
# 		status = json.loads(cmdsts.get('control:status'))

# 	return status

# def get_probe_info(probe_info):
# 	''' Create a structure with probe information for the display to use. '''
# 	probe_structure = {
# 		'primary' : {},
# 		'food' : []
# 	}
# 	for probe in probe_info:
# 		if probe['type'] == 'Primary':
# 			probe_structure['primary']['name'] = probe['name']
# 			probe_structure['primary']['label'] = probe['label']
# 		elif probe['type'] == 'Food':
# 			food_probe = {
# 				'name' : probe['name'],
# 				'label' : probe['label']
# 			}
# 			probe_structure['food'].append(food_probe)

# 	return probe_structure 

# # Borrowed from: https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
# # Attributed to Alex Martelli and Alex Telon 
def deep_update(dictionary, updates):
	for key, value in updates.items():
		if isinstance(value, Mapping):
			dictionary[key] = deep_update(dictionary.get(key, {}), value)
		else:
			dictionary[key] = value

	return dictionary

MODE_MAP = {
	'stop' : 'Stop',
	'error' : 'Error',
	'riding' : 'Riding'
}

# MODE_MAP = {
# 	'startup' : 'Startup',
# 	'smoke' : 'Smoke',
# 	'shutdown' : 'Shutdown',
# 	'stop' : 'Stop',
# 	'reignite' : 'Reignite',
# 	'monitor' : 'Monitor',
# 	'error' : 'Error',
# 	'prime' : 'Prime',
# 	'hold' : 'Hold',
# 	'manual' : 'Manual'
# }


# Borrowed from: https://pythonhow.com/how/check-if-a-string-is-a-float/ 
# Attributed to Python How
# Slightly modified to check if string is None
def is_float(string):
	if string is not None:
		if string.replace(".", "").isnumeric():
			return True
	return False

# def process_command(action=None, arglist=[], origin='unknown', direct_write=False):
# 	'''
# 	Process incoming command from API or elsewhere
# 	'''
# 	data = {} 
# 	data['result'] = 'OK'
# 	data['message'] = 'Command was accepted successfully.'
# 	data['data'] = {}

# 	control = read_control()
# 	settings = read_settings() 
	
# 	''' Populate any empty args with None just in case '''
# 	num_args = len(arglist)
# 	max_args = 4  # Needs updating if API adds deeper number of arguments 

# 	for _ in range(max_args - num_args):
# 		arglist.append(None)

# 	if action == 'get':
# 		''' GET Commands '''

# 		if arglist[0] == 'temp':
# 			'''
# 			Get Temperature 
# 			/api/get/temp/{probe label}


# 			Returns: 
# 			{ 
# 				'temp' : <probe temperature> 
# 				'result' : 'OK'
# 			}
# 			'''
# 			current_temps = read_current()

# 			if arglist[1] in current_temps['P'].keys():
# 				data['data']['temp'] = current_temps['P'][arglist[1]]
# 			elif arglist[1] in current_temps['F'].keys():
# 				data['data']['temp'] = current_temps['F'][arglist[1]]
# 			elif arglist[1] in current_temps['AUX'].keys():
# 				data['data']['temp'] = current_temps['AUX'][arglist[1]]
# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Probe {arglist[1]} not found or not specified.'

# 		elif arglist[0] == 'current':
# 			'''
# 			Get Current Temp Data Structure 
# 			/api/get/current

# 			Returns (Example): 
# 			{
# 				"AUX": {},
# 				"F": {
# 					"Probe1": 204,
# 					"Probe2": 206
# 				},
# 				"NT": {
# 					"Grill": 0,
# 					"Probe1": 0,
# 					"Probe2": 0
# 				},
# 				"P": {
# 					"Grill": 518
# 				},
# 				"PSP": 0,
# 				"TS": 1707345482984
# 			}
# 			'''
# 			current_temps = read_current()

# 			data['data'] = current_temps

# 		elif arglist[0] == 'mode':
# 			'''
# 			Get Current Mode 
# 			/api/get/mode

# 			Returns: 
# 			{ 
# 				'mode' : <Current Mode> 
# 			}
# 			'''
# 			data['data']['mode'] = control['mode']

# 		elif arglist[0] == 'hopper':
# 			'''
# 			Get Hopper Level 
# 			/api/get/hopper

# 			Returns: 
# 			{ 
# 				'hopper' : <level> 
# 			}
# 			'''
# 			control['hopper_check'] = True 
# 			write_control(control, direct_write=direct_write, origin=origin)
# 			time.sleep(3)
# 			pelletdb = read_pellet_db()
# 			data['data']['hopper'] = pelletdb['current']['hopper_level']
		
# 		elif arglist[0] == 'timer':
# 			'''
# 			Get Timer Data
# 			/api/get/timer

# 			Returns:
# 			{ 
# 				'start' : control['timer']['start'], 
# 				'paused' : control['timer']['paused'],
# 				'end' : control['timer']['end'], 
# 				'shutdown' : control['notify_data'][]['shutdown'],
# 				'keep_warm' : control['notify_data'][]['keep_warm'],
# 			}
# 			'''
# 			data['data']['start'] = control['timer']['start']
# 			data['data']['paused'] = control['timer']['paused']
# 			data['data']['end'] = control['timer']['end']
# 			''' Get index of timer object '''
# 			for index, notify_obj in enumerate(control['notify_data']):
# 				if notify_obj['type'] == 'timer':
# 					break 
# 			data['data']['shutdown'] = control['notify_data'][index]['shutdown']
# 			data['data']['keep_warm'] = control['notify_data'][index]['keep_warm']

# 		elif arglist[0] == 'notify':
# 			'''
# 			Get Notify Data
# 			/api/get/notify

# 			Returns:
# 				[
# 					{
# 					"eta": null,
# 					"keep_warm": false,
# 					"label": "Grill",
# 					"name": "GrillMain",
# 					"req": false,
# 					"shutdown": false,
# 					"target": 0,
# 					"type": "probe"
# 					},
# 					...
# 					{
# 					"keep_warm": false,
# 					"label": "Hopper",
# 					"last_check": 0,
# 					"req": true,
# 					"shutdown": false,
# 					"type": "hopper"
# 					}
# 				]
# 			'''
# 			data['data'] = control['notify_data']

# 		elif arglist[0] == 'status':
# 			'''
# 			Get Status Information for Key Items
# 			/api/get/status

# 			Returns (Example):
# 			{
# 				"display_mode": "Stop",
# 				"lid_open_detected": false,
# 				"lid_open_endtime": 0,
# 				"mode": "Stop",
# 				"name": "Development",
# 				"outpins": {
# 					"auger": false,
# 					"fan": false,
# 					"igniter": false,
# 					"power": false
# 				},
# 				"p_mode": 0,
# 				"prime_amount": 0,
# 				"prime_duration": 0,
# 				"s_plus": false,
# 				"shutdown_duration": 10,
# 				"start_duration": 30,
# 				"start_time": 0,
# 				"startup_timestamp": 0,
# 				"status": "",
# 				"ui_hash": 5734093427135650890,
# 				"units": "F"
# 			}
# 			'''
# 			status = read_status()

# 			data['data']['mode'] = control['mode']
# 			data['data']['display_mode'] = status['mode']
# 			data['data']['status'] = control['status']
# 			data['data']['s_plus'] = control['s_plus']
# 			data['data']['units'] = settings['globals']['units']
# 			data['data']['name'] = settings['globals']['grill_name']
# 			data['data']['start_time'] = status['start_time']
# 			data['data']['start_duration'] = status['start_duration']
# 			data['data']['shutdown_duration'] = status['shutdown_duration']
# 			data['data']['prime_duration'] = status['prime_duration']
# 			data['data']['prime_amount'] = status['prime_amount']
# 			data['data']['lid_open_detected'] = status['lid_open_detected']
# 			data['data']['lid_open_endtime'] = status['lid_open_endtime']
# 			data['data']['p_mode'] = status['p_mode']
# 			data['data']['outpins'] = status['outpins']
# 			data['data']['startup_timestamp'] = status['startup_timestamp']
# 			data['data']['ui_hash'] = hash(json.dumps(settings['probe_settings']['probe_map']['probe_info']))

# 		else:
# 			data['result'] = 'ERROR'
# 			data['message'] = f'Get API Argument: [{arglist[0]}] not recognized.'
	
# 	elif action == 'set':
# 		''' SET Commands '''

# 		if arglist[0] == 'psp':
# 			'''
# 			Primary Setpoint 
# 			/api/set/psp/{integer/float temperature}
# 			'''
# 			if is_float(arglist[1]):
# 				control['mode'] = 'Hold'
# 				if settings['globals']['units'] == 'F':
# 					control['primary_setpoint'] = int(float(arglist[1]))
# 				else:
# 					control['primary_setpoint'] = float(arglist[1])
# 				control['updated'] = True
# 				write_control(control, direct_write=direct_write, origin=origin)
# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Primary set point should be an integer or float in degrees {settings["globals"]["units"]}'

# 		elif arglist[0] == 'mode':
# 			'''
# 			Mode
# 			/api/set/mode/{mode} where mode = 'startup', 'smoke', 'shutdown', 'stop', 'reignite', 'monitor', 'error'
# 			/api/set/mode/prime/{prime amount in grams}[/{next mode}]
# 			/api/set/mode/hold/{integer/float temperature}
# 			'''
# 			if arglist[1] in ['startup', 'smoke', 'shutdown', 'stop', 'reignite', 'monitor', 'error', 'manual']:
# 				control['mode'] = MODE_MAP[arglist[1]]
# 				control['updated'] = True
# 				write_control(control, direct_write=direct_write, origin=origin)
# 			elif arglist[1] == 'prime':
# 				try:
# 					if arglist[2] is not None: 
# 						if arglist[2].isdigit():
# 							control['mode'] = MODE_MAP[arglist[1]]
# 							control['prime_amount'] = int(arglist[2])
# 							control['updated'] = True
# 							if arglist[3] in ['startup', 'monitor']:
# 								control['next_mode'] = MODE_MAP[arglist[3]]
# 							else:
# 								control['next_mode'] = 'Stop'
# 							write_control(control, direct_write=direct_write, origin=origin)
# 						else:
# 							data['result'] = 'ERROR'
# 							data['message'] = f'Prime amount should be an integer in grams.'
# 					else:
# 						data['result'] = 'ERROR'
# 						data['message'] = f'Prime amount not specified.'
# 				except:
# 					data['result'] = 'ERROR'
# 					data['message'] = f'Set Mode {arglist[1]} with {arglist[2]} caused an exception.'
# 			elif arglist[1] == 'hold':
# 				if arglist[2] is not None: 
# 					if is_float(arglist[2]):
# 						control['mode'] = MODE_MAP[arglist[1]]
# 						if settings['globals']['units'] == 'F':
# 							control['primary_setpoint'] = int(float(arglist[2]))
# 						else:
# 							control['primary_setpoint'] = float(arglist[2])
# 						control['updated'] = True
# 						write_control(control, direct_write=direct_write, origin=origin)
# 					else:
# 						data['result'] = 'ERROR'
# 						data['message'] = f'Set Mode {arglist[1]} with {arglist[2]} failed [not a number].'
# 				else:
# 					data['result'] = 'ERROR'
# 					data['message'] = f'Set Mode {arglist[1]} with {arglist[2]} failed [no hold temp specified].'
# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Get API Argument: {arglist[2]} not recognized.'
		
# 		elif arglist[0] == 'pmode':
# 			'''
# 			PMode
# 			/api/set/pmode/{pmode value} where pmode value is between 0-9 
# 			'''
# 			if arglist[1] is not None: 
# 				if arglist[1].isdigit():
# 					if int(arglist[1]) >= 0 and int(arglist[1]) < 10:
# 						settings['cycle_data']['PMode'] = int(arglist[1])
# 						write_settings(settings)
# 						control['settings_update'] = True 
# 						write_control(control, direct_write=False, origin=origin)
# 					else:
# 						data['result'] = 'ERROR'
# 						data['message'] = f'Set PMode out of range(0-9): {arglist[1]}'
# 				else:
# 					data['result'] = 'ERROR'
# 					data['message'] = f'Set PMode invalid value.'
# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Set PMode invalid arguments.'
		
# 		elif arglist[0] == 'splus':
# 			'''
# 			Smoke Plus 
# 			/api/set/splus/{true/false}
# 			'''
# 			if arglist[1] == 'true':
# 				control['s_plus'] = True
# 			else:
# 				control['s_plus'] = False 
# 			write_control(control, direct_write=direct_write, origin=origin)
		
# 		elif arglist[0] == 'notify':
# 			'''
# 			Notify Settings
# 			/api/set/notify/{object}/ where object = probe label, 'Timer', 'Hopper' 

# 			/api/set/notify/{object}/req/{true/false} 
# 			/api/set/notify/{object}/target/{value}  (not valid for Timer or Hopper)
# 			/api/set/notify/{object}/shutdown/{true/false}
# 			/api/set/notify/{object}/keep_warm/{true/false} 
# 			'''

# 			if arglist[1] is not None:
# 				found = False
# 				for index, object in enumerate(control['notify_data']):
# 					if object['label'] == arglist[1]:
# 						print('FOUND')
# 						found = True
# 						if arglist[2] in ['req', 'shutdown', 'keep_warm']:
# 							if arglist[3] == 'true':
# 								control['notify_data'][index][arglist[2]] = True
# 							else: 
# 								control['notify_data'][index][arglist[2]] = False
# 						elif arglist[2] == 'target' and arglist[1] not in ['Timer', 'Hopper']:
# 							if is_float(arglist[3]):
# 								if settings['globals']['units'] == 'F':
# 									control['notify_data'][index]['target'] = int(float(arglist[3]))
# 								else:
# 									control['primary_setpoint'] = float(arglist[3])
# 							else:
# 								data['result'] = 'ERROR'
# 								data['message'] = f'Notify object target value invalid or missing.'
# 						else:
# 							data['result'] = 'ERROR'
# 							data['message'] = f'Notify object update failed.'
# 						break
# 				if not found:
# 					data['result'] = 'ERROR'
# 					data['message'] = f'Notify object label {arglist[1]} was not found.'
# 				else:
# 					write_control(control, direct_write=False, origin=origin)
# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Notify object label was not specified.'
				
# 		elif arglist[0] == 'pwm':
# 			'''
# 			PWM Control

# 			/api/set/pwm/{true/false} 
# 			'''
# 			if arglist[1] == 'true':
# 				control['pwm_control'] = True
# 			else:
# 				control['pwm_control'] = False 
# 			write_control(control, direct_write=direct_write, origin=origin) 

# 		elif arglist[0] == 'duty_cycle':
# 			'''
# 			Duty Cycle

# 			/api/set/duty_cycle/{0-100 percent} 
# 			'''
# 			if is_float(arglist[1]):
# 				duty_cycle = int(arglist[1])
# 				if duty_cycle >= 0 and duty_cycle <= 100:
# 					control['duty_cycle'] = duty_cycle
# 					write_control(control, direct_write=False, origin=origin)
# 				else:
# 					data['result'] = 'ERROR'
# 					data['message'] = f'Duty cycle must be an integer between 0-100.'
# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Duty cycle must be specified as an integer between 0-100 percent.'

# 		elif arglist[0] == 'tuning_mode':
# 			'''
# 			Tuning Mode Enable

# 			/api/set/tuning_mode/{true/false} 
# 			'''
# 			if arglist[1] == 'true':
# 				control['tuning_mode'] = True
# 			else:
# 				control['tuning_mode'] = False 
# 			write_control(control, direct_write=direct_write, origin=origin)

# 		elif arglist[0] == 'timer':
# 			'''
# 			Timer Control

# 			/api/set/timer/start/{seconds} 
# 			/api/set/timer/pause 
# 			/api/set/timer/stop
# 			/api/set/timer/shutdown/{true/false}
# 			/api/set/timer/keep_warm/{true/false}
# 			'''

# 			''' Get index of timer object '''
# 			for index, notify_obj in enumerate(control['notify_data']):
# 				if notify_obj['type'] == 'timer':
# 					break 
# 			''' Get timestamp '''
# 			now = time.time()

# 			if arglist[1] == 'start':
# 				control['notify_data'][index]['req'] = True
# 				# If starting new timer
# 				if control['timer']['paused'] == 0:
# 					control['timer']['start'] = now
# 					if is_float(arglist[2]):
# 						seconds = int(float(arglist[2]))
# 						control['timer']['end'] = now + seconds
# 					else:
# 						control['timer']['end'] = now + 60
# 					write_log('Timer started.  Ends at: ' + epoch_to_time(control['timer']['end']))
# 					write_control(control, direct_write=direct_write, origin='app')
# 				else:	# If Timer was paused, restart with new end time.
# 					control['timer']['end'] = (control['timer']['end'] - control['timer']['paused']) + now
# 					control['timer']['paused'] = 0
# 					write_log('Timer unpaused.  Ends at: ' + epoch_to_time(control['timer']['end']))
# 					write_control(control, direct_write=direct_write, origin='app')
# 			elif arglist[1] == 'pause':
# 				if control['timer']['start'] != 0:
# 					control['notify_data'][index]['req'] = False
# 					control['timer']['paused'] = now
# 					write_log('Timer paused.')
# 					write_control(control, direct_write=direct_write, origin='app')
# 				else:
# 					control['notify_data'][index]['req'] = False
# 					control['timer']['start'] = 0
# 					control['timer']['end'] = 0
# 					control['timer']['paused'] = 0
# 					control['notify_data'][index]['shutdown'] = False
# 					control['notify_data'][index]['keep_warm'] = False
# 					write_log('Timer cleared.')
# 					write_control(control, direct_write=direct_write, origin='app')
# 			elif arglist[1] == 'stop':
# 				control['notify_data'][index]['req'] = False
# 				control['timer']['start'] = 0
# 				control['timer']['end'] = 0
# 				control['timer']['paused'] = 0
# 				control['notify_data'][index]['shutdown'] = False
# 				control['notify_data'][index]['keep_warm'] = False
# 				write_log('Timer stopped.')
# 				write_control(control, direct_write=direct_write, origin='app')
# 			elif arglist[1] == 'shutdown':
# 				if arglist[2] == 'true':
# 					control['notify_data'][index]['shutdown'] = True
# 				else:
# 					control['notify_data'][index]['shutdown'] = False 
# 				write_control(control, direct_write=direct_write, origin=origin)
# 			elif arglist[1] == 'keep_warm':
# 				if arglist[2] == 'true':
# 					control['notify_data'][index]['keep_warm'] = True
# 				else:
# 					control['notify_data'][index]['keep_warm'] = False 
# 				write_control(control, direct_write=direct_write, origin=origin)
# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Timer command not recognized.'

# 		elif arglist[0] == 'manual':
# 			'''
# 			Manual Control
# 			Note: Must already be in Manual mode (see set/mode command)
# 			/api/set/manual/power/{true/false}
# 			/api/set/manual/igniter/{true/false}
# 			/api/set/manual/fan/{true/false}
# 			/api/set/manual/auger/{true/false}
# 			/api/set/manual/pwm/{speed}
# 			'''

# 			if control['mode'] == 'Manual':
# 				if arglist[1] == 'power':
# 					control['manual']['change'] = True
# 					if arglist[2] == 'true':
# 						control['manual']['power'] = True
# 					else:
# 						control['manual']['power'] = False 
# 				elif arglist[1] == 'igniter':
# 					control['manual']['change'] = True
# 					if arglist[2] == 'true':
# 						control['manual']['igniter'] = True
# 					else:
# 						control['manual']['igniter'] = False 
# 				elif arglist[1] == 'fan':
# 					control['manual']['change'] = True
# 					if arglist[2] == 'true':
# 						control['manual']['fan'] = True
# 					else:
# 						control['manual']['fan'] = False 
# 						control['manual']['pwm'] = 100
# 				elif arglist[1] == 'auger':
# 					control['manual']['change'] = True
# 					if arglist[2] == 'true':
# 						control['manual']['auger'] = True
# 					else:
# 						control['manual']['auger'] = False
# 				elif arglist[1] == 'pwm' and is_float(arglist[2]):
# 					control['manual']['change'] = True
# 					control['manual']['pwm'] = int(float(arglist[2]))
# 				else:
# 					data['result'] = 'ERROR'
# 					data['message'] = f'Manual command not recognized or contained an error.'
# 				if control['manual']['change']:
# 					write_control(control, direct_write=direct_write, origin=origin)

# 			else:
# 				data['result'] = 'ERROR'
# 				data['message'] = f'Before changing manual outputs, system must be put into Manual mode.'

# 		else:
# 			data['result'] = 'ERROR'
# 			data['message'] = f'Set API Argument: {arglist[0]} not recognized.'

# 	elif action == 'cmd':
# 		''' System CMD Commands '''

# 		if arglist[0] == 'restart':
# 			'''
# 			Restart Scripts 
# 			/api/cmd/restart
# 			'''
# 			restart_scripts()
		
# 		elif arglist[0] == 'reboot':
# 			'''
# 			Reboot System 
# 			/api/cmd/reboot
# 			'''
# 			reboot_system()
		
# 		elif arglist[0] == 'shutdown':
# 			'''
# 			Shutdown System 
# 			/api/cmd/shutdown
# 			'''
# 			shutdown_system()
		
# 		else:
# 			data['result'] = 'ERROR'
# 			data['message'] = f'CMD API Argument: {arglist[0]} not recognized.'
	
# 	else:
# 		data['result'] = 'ERROR'
# 		data['message'] = f'Action [{action}] not valid/recognized.'

# 	return data