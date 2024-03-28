'''
==============================================================================
 PiCycle Web UI (Flask App) Process
==============================================================================

Description: This script will start at boot, and start up the web user
  interface.
 
  This script runs as a separate process from the control program
  implementation which handles interfacing and running I2C devices & GPIOs.

  This was created from a clone of the PiFire repository

==============================================================================
'''

'''
==============================================================================
 Imported Modules
==============================================================================
'''

from flask import Flask, request, abort, render_template, make_response, send_file, jsonify, redirect, render_template_string
from flask_mobility import Mobility
from flask_socketio import SocketIO
from flask_qrcode import QRcode
#from io import BytesIO
# from werkzeug.utils import secure_filename
# from collections.abc import Mapping
# import threading
# import zipfile
# import pathlib
# from threading import Thread
# from datetime import datetime
# from updater import *  # Library for doing project updates from GitHub
# from file_mgmt.common import fixup_assets, read_json_file_data, update_json_file_data, remove_assets
#from file_mgmt.cookfile import read_cookfile, upgrade_cookfile, prepare_chartdata
# from file_mgmt.media import add_asset, set_thumbnail, unpack_thumb
#from file_mgmt.recipes import read_recipefile, create_recipefile

#EP - Added this which piFire indirectly called from updater
from common import *


'''
==============================================================================
 Constants & Globals 
==============================================================================
'''

# BACKUP_PATH = './backups/'  # Path to backups of settings.json, pelletdb.json
# UPLOAD_FOLDER = BACKUP_PATH  # Point uploads to the backup path
# HISTORY_FOLDER = './history/'  # Path to historical cook files
# RECIPE_FOLDER = './recipes/'  # Path to recipe files 
LOGS_FOLDER = './logs/'  # Path to log files 
# ALLOWED_EXTENSIONS = {'json', 'picycle', 'pfrecipe', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'log'}
server_status = 'available'

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
QRcode(app)
Mobility(app)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['HISTORY_FOLDER'] = HISTORY_FOLDER
# app.config['RECIPE_FOLDER'] = RECIPE_FOLDER

'''
==============================================================================
 App Routes
==============================================================================
'''
@app.route('/')
def index():
	global settings
	return 'I want to ride my PiCycle I want to ride my bike...'
	
	# if settings['globals']['first_time_setup']:
	# 	return redirect('/wizard/welcome')
	# else: 
	# 	return redirect('/dash')

# @app.route('/dash')
# def dash():
# 	global settings
# 	control = read_control()
# 	errors = read_errors()
# 	warnings = read_warnings()

# 	current = settings['dashboard']['current']
# 	dash_template = settings['dashboard']['dashboards'][current].get('html_name', 'dash_default.html')
# 	dash_data = settings['dashboard']['dashboards'].get(current, {})

# 	return render_template(dash_template,
# 						   settings=settings,
# 						   control=control,
# 						   dash_data=dash_data,
# 						   errors=errors,
# 						   warnings=warnings,
# 						   page_theme=settings['globals']['page_theme'],
# 						   grill_name=settings['globals']['grill_name'])

# @app.route('/logs/<action>', methods=['POST','GET'])
# @app.route('/logs', methods=['POST','GET'])
# def logs_page(action=None):
# 	global settings
# 	control = read_control()
# 	# Get list of log files 
# 	if not os.path.exists(LOGS_FOLDER):
# 		os.mkdir(LOGS_FOLDER)
# 	log_file_list = os.listdir(LOGS_FOLDER)
# 	for file in log_file_list:
# 		if not _allowed_file(file):
# 			log_file_list.remove(file)

# 	if(request.method == 'POST') and ('form' in request.content_type):
# 		requestform = request.form 

# 		if 'download' in requestform:
# 			log_file_name = LOGS_FOLDER + requestform['selectLog']
# 			return send_file(log_file_name, as_attachment=True, max_age=0)
# 		elif 'eventslist' in requestform:
# 			log_file_name = requestform['logfile']
# 			event_list = read_log_file(LOGS_FOLDER + log_file_name)
# 			event_list = add_line_numbers(event_list)
# 			page = int(requestform['page'])
# 			reverse = True if requestform['reverse'] == 'true' else False
# 			itemsperpage = int(requestform['itemsperpage'])
# 			pgntd_data = _paginate_list(event_list, reversesortorder=reverse, itemsperpage=itemsperpage, page=page)
# 			return render_template('_log_list.html', pgntd_data = pgntd_data, log_file_name=log_file_name)
# 		else:
# 			return ('Error')

# 	return render_template('logs.html',
# 							settings=settings,
# 							control=control,
# 							log_file_list=log_file_list,
# 						   	page_theme=settings['globals']['page_theme'],
# 						   	grill_name=settings['globals']['grill_name'])

# @app.route('/settings/<action>', methods=['POST','GET'])
# @app.route('/settings', methods=['POST','GET'])
# def settings_page(action=None):

# 	global settings
# 	control = read_control()

# 	#controller = read_generic_json('./controller/controllers.json')

# 	event = {
# 		'type' : 'none',
# 		'text' : ''
# 	}

# 	if request.method == 'POST' and action == 'startup':
# 		response = request.form

# 		if _is_not_blank(response, 'shutdown_duration'):
# 			settings['shutdown']['shutdown_duration'] = int(response['shutdown_duration'])
# 		if _is_not_blank(response, 'startup_duration'):
# 			settings['startup']['duration'] = int(response['startup_duration'])
# 		if _is_checked(response, 'auto_power_off'):
# 			settings['shutdown']['auto_power_off'] = True
# 		else:
# 			settings['shutdown']['auto_power_off'] = False
# 		if _is_checked(response, 'smartstart_enable'):
# 			settings['startup']['smartstart']['enabled'] = True
# 		else:
# 			settings['startup']['smartstart']['enabled'] = False
# 		if _is_not_blank(response, 'smartstart_exit_temp'):
# 			settings['startup']['smartstart']['exit_temp'] = int(response['smartstart_exit_temp'])
# 		if _is_not_blank(response, 'startup_exit_temp'):
# 			settings['startup']['startup_exit_temp'] = int(response['startup_exit_temp'])
# 		if _is_not_blank(response, 'prime_on_startup'):
# 			prime_amount = int(response['prime_on_startup'])
# 			if prime_amount < 0 or prime_amount > 200:
# 				prime_amount = 0  # Validate input, set to disabled if exceeding limits.  
# 			settings['startup']['prime_on_startup'] = int(response['prime_on_startup'])

# 		settings['startup']['start_to_mode']['after_startup_mode'] = response['after_startup_mode']
# 		settings['startup']['start_to_mode']['primary_setpoint'] = int(response['startup_mode_setpoint'])
		
# 		event['type'] = 'updated'
# 		event['text'] = 'Successfully updated startup/shutdown settings.'

# 		control['settings_update'] = True

# 		write_settings(settings)
# 		write_control(control, origin='app')

# 	if request.method == 'POST' and action == 'history':
# 		response = request.form

# 		if _is_not_blank(response, 'historymins'):
# 			settings['history_page']['minutes'] = int(response['historymins'])
# 		if _is_checked(response, 'clearhistorystartup'):
# 			settings['history_page']['clearhistoryonstart'] = True
# 		else:
# 			settings['history_page']['clearhistoryonstart'] = False
# 		if _is_checked(response, 'historyautorefresh'):
# 			settings['history_page']['autorefresh'] = 'on'
# 		else:
# 			settings['history_page']['autorefresh'] = 'off'
# 		if _is_not_blank(response, 'datapoints'):
# 			settings['history_page']['datapoints'] = int(response['datapoints'])

# 		# This check should be the last in this group
# 		if control['mode'] != 'Stop' and _is_checked(response, 'ext_data') != settings['globals']['ext_data']:
# 			event['type'] = 'error'
# 			event['text'] = 'This setting cannot be changed in any active mode.  Stop the grill and try again.'
# 		else: 
# 			if _is_checked(response, 'ext_data'):
# 				settings['globals']['ext_data'] = True
# 			else:
# 				settings['globals']['ext_data'] = False 

# 			event['type'] = 'updated'
# 			event['text'] = 'Successfully updated history settings.'

# 		# Edit Graph Color Config
# 		for item in response:
# 			if 'clr_temp_' in item: 
# 				probe_label = item.replace('clr_temp_', '')
# 				settings['history_page']['probe_config'][probe_label]['line_color'] = response[item]
# 			if 'clrbg_temp_' in item: 
# 				probe_label = item.replace('clrbg_temp_', '')
# 				settings['history_page']['probe_config'][probe_label]['bg_color'] = response[item]
# 			if 'clr_setpoint_' in item: 
# 				probe_label = item.replace('clr_setpoint_', '')
# 				settings['history_page']['probe_config'][probe_label]['line_color_setpoint'] = response[item]
# 			if 'clrbg_setpoint_' in item: 
# 				probe_label = item.replace('clrbg_setpoint_', '')
# 				settings['history_page']['probe_config'][probe_label]['bg_color_setpoint'] = response[item]
# 			if 'clr_target_' in item: 
# 				probe_label = item.replace('clr_target_', '')
# 				settings['history_page']['probe_config'][probe_label]['line_color_target'] = response[item]
# 			if 'clrbg_target_' in item: 
# 				probe_label = item.replace('clrbg_target_', '')
# 				settings['history_page']['probe_config'][probe_label]['bg_color_target'] = response[item]

# 		write_settings(settings)

# 	if request.method == 'POST' and action == 'pagesettings':
# 		response = request.form

# 		if _is_checked(response, 'darkmode'):
# 			settings['globals']['page_theme'] = 'dark'
# 		else:
# 			settings['globals']['page_theme'] = 'light'

# 		if _is_checked(response, 'global_control_panel'):
# 			settings['globals']['global_control_panel'] = True
# 		else:
# 			settings['globals']['global_control_panel'] = False

# 		event['type'] = 'updated'
# 		event['text'] = 'Successfully updated page settings.'

# 		write_settings(settings)

# 	if request.method == 'POST' and action == 'grillname':
# 		response = request.form

# 		if 'grill_name' in response:
# 			settings['globals']['grill_name'] = response['grill_name']
# 			event['type'] = 'updated'
# 			event['text'] = 'Successfully updated grill name.'

# 		write_settings(settings)

# 	if request.method == 'POST' and action == 'units':
# 		response = request.form

# 		if 'units' in response:
# 			if response['units'] == 'C' and settings['globals']['units'] == 'F':
# 				settings = convert_settings_units('C', settings)
# 				write_settings(settings)
# 				event['type'] = 'updated'
# 				event['text'] = 'Successfully updated units to Celsius.'
# 				control = {}
# 				control['updated'] = True
# 				control['units_change'] = True
# 				write_control(control, origin='app')
# 			elif response['units'] == 'F' and settings['globals']['units'] == 'C':
# 				settings = convert_settings_units('F', settings)
# 				write_settings(settings)
# 				event['type'] = 'updated'
# 				event['text'] = 'Successfully updated units to Fahrenheit.'
# 				control = {}
# 				control['updated'] = True
# 				control['units_change'] = True
# 				write_control(control, origin='app')

# @app.route('/admin/<action>', methods=['POST','GET'])
# @app.route('/admin', methods=['POST','GET'])
# def admin_page(action=None):
# 	global server_status
# 	global settings
# 	control = read_control()
# 	notify = ''

# 	if not os.path.exists(BACKUP_PATH):
# 		os.mkdir(BACKUP_PATH)
# 	files = os.listdir(BACKUP_PATH)
# 	for file in files:
# 		if not _allowed_file(file):
# 			files.remove(file)

# 	if action == 'reboot':
# 		event = "Admin: Reboot"
# 		write_log(event)
# 		server_status = 'rebooting'
# 		reboot_system()
# 		return render_template('shutdown.html', action=action, page_theme=settings['globals']['page_theme'],
# 							   grill_name=settings['globals']['grill_name'])

# 	elif action == 'shutdown':
# 		event = "Admin: Shutdown"
# 		write_log(event)
# 		server_status = 'shutdown'
# 		shutdown_system()
# 		return render_template('shutdown.html', action=action, page_theme=settings['globals']['page_theme'],
# 							   grill_name=settings['globals']['grill_name'])

# 	elif action == 'restart':
# 		event = "Admin: Restart Server"
# 		write_log(event)
# 		server_status = 'restarting'
# 		restart_scripts()
# 		return render_template('shutdown.html', action=action, page_theme=settings['globals']['page_theme'],
# 							   grill_name=settings['globals']['grill_name'])

# 	if request.method == 'POST' and action == 'setting':
# 		response = request.form

# 		if 'debugenabled' in response:
# 			control['settings_update'] = True
# 			if response['debugenabled'] == 'disabled':
# 				write_log('Debug Mode Disabled.')
# 				settings['globals']['debug_mode'] = False
# 				write_settings(settings)
# 				write_control(control, origin='app')
# 			else:
# 				settings['globals']['debug_mode'] = True
# 				write_settings(settings)
# 				write_control(control, origin='app')
# 				write_log('Debug Mode Enabled.')

# 		if 'clearhistory' in response:
# 			if response['clearhistory'] == 'true':
# 				write_log('Clearing History Log.')
# 				read_history(0, flushhistory=True)

# 		if 'clearevents' in response:
# 			if response['clearevents'] == 'true':
# 				write_log('Clearing Events Log.')
# 				os.system('rm /tmp/events.log')

# 		if 'factorydefaults' in response:
# 			if response['factorydefaults'] == 'true':
# 				write_log('Resetting Settings, Control and History to factory defaults.')
# 				read_history(0, flushhistory=True)
# 				read_control(flush=True)
# 				os.system('rm settings.json')
# 				os.system('rm pelletdb.json')
# 				settings = default_settings()
# 				control = default_control()
# 				write_settings(settings)
# 				write_control(control, origin='app')
# 				server_status = 'restarting'
# 				restart_scripts()
# 				return render_template('shutdown.html', action='restart', page_theme=settings['globals']['page_theme'],
# 									   grill_name=settings['globals']['grill_name'])

# 		if 'download_logs' in response:
# 			zip_file = _zip_files_logs('logs')
# 			return send_file(zip_file, as_attachment=True, max_age=0)
		
# 		if 'backupsettings' in response:
# 			backup_file = backup_settings()
# 			return send_file(backup_file, as_attachment=True, max_age=0)

# 		if 'restoresettings' in response:
# 			# Assume we have request.files and local file in response
# 			remote_file = request.files['uploadfile']
# 			local_file = request.form['localfile']
			
# 			if local_file != 'none':
# 				new_settings = read_settings(filename=BACKUP_PATH+local_file)
# 				write_settings(new_settings)
# 				server_status = 'restarting'
# 				restart_scripts()
# 				return render_template('shutdown.html', action='restart', page_theme=settings['globals']['page_theme'],
# 									   grill_name=settings['globals']['grill_name'])
# 			elif remote_file.filename != '':
# 				# If the user does not select a file, the browser submits an
# 				# empty file without a filename.
# 				if remote_file and _allowed_file(remote_file.filename):
# 					filename = secure_filename(remote_file.filename)
# 					remote_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# 					notify = "success"
# 					new_settings = read_settings(filename=BACKUP_PATH+filename)
# 					write_settings(new_settings)
# 					server_status = 'restarting'
# 					restart_scripts()
# 					return render_template('shutdown.html', action='restart', page_theme=settings['globals']['page_theme'],
# 									   		grill_name=settings['globals']['grill_name'])
# 				else:
# 					notify = "error"
# 			else:
# 				notify = "error"

	
# 	if request.method == 'POST' and action == 'boot':
# 		response = request.form

# 		if 'boot_to_monitor' in response:
# 			settings['globals']['boot_to_monitor'] = True 
# 		else:
# 			settings['globals']['boot_to_monitor'] = False 
		
# 		write_settings(settings)

# 	uptime = os.popen('uptime').readline()

# 	cpu_info = os.popen('cat /proc/cpuinfo').readlines()

# 	ifconfig = os.popen('ifconfig').readlines()

# 	if is_real_hardware():
# 		temp = _check_cpu_temp()
# 	else:
# 		temp = '---'

# 	debug_mode = settings['globals']['debug_mode']

# 	url = request.url_root

# 	return render_template('admin.html', settings=settings, notify=notify, uptime=uptime, cpuinfo=cpu_info, temp=temp,
# 						   ifconfig=ifconfig, debug_mode=debug_mode, qr_content=url,
# 						   control=control,
# 						   page_theme=settings['globals']['page_theme'],
# 						   grill_name=settings['globals']['grill_name'], files=files)

# @app.route('/api', methods=['POST','GET'])
# @app.route('/api/<action>', methods=['POST','GET'])
# @app.route('/api/<action>/<arg0>', methods=['POST','GET'])
# @app.route('/api/<action>/<arg0>/<arg1>', methods=['POST','GET'])
# @app.route('/api/<action>/<arg0>/<arg1>/<arg2>', methods=['POST','GET'])
# @app.route('/api/<action>/<arg0>/<arg1>/<arg2>/<arg3>', methods=['POST','GET'])
# def api_page(action=None, arg0=None, arg1=None, arg2=None, arg3=None):
# 	global settings
# 	global server_status

# 	if action in ['get', 'set', 'cmd']:
# 		#print(f'action={action}\narg0={arg0}\narg1={arg1}\narg2={arg2}\narg3={arg3}')
# 		arglist = []
# 		arglist.extend([arg0, arg1, arg2, arg3])

# 		data = process_command(action=action, arglist=arglist, origin='api')
# 		return jsonify(data), 201
	
# 	elif request.method == 'GET':
# 		if action == 'settings':
# 			return jsonify({'settings':settings}), 201
# 		elif action == 'server':
# 			return jsonify({'server_status' : server_status}), 201
# 		elif action == 'control':
# 			control=read_control()
# 			return jsonify({'control':control}), 201
# 		elif action == 'current':
# 			''' Only fetch data from RedisDB or locally available, to improve performance '''
# 			current_temps = read_current()
# 			control = read_control()
# 			display = read_status()  # Get status of display items

# 			''' Create string of probes that can be hashed to ensure UI integrity '''
# 			probe_string = ''
# 			for group in current_temps:
# 				if group in ['P', 'F']:
# 					for probe in current_temps[group]:
# 						probe_string += probe
# 			probe_string += settings['globals']['units']

# 			notify_data = control['notify_data']

# 			status = {}
# 			status['mode'] = control['mode']
# 			status['display_mode'] = display['mode']
# 			status['status'] = control['status']
# 			status['s_plus'] = control['s_plus']
# 			status['units'] = settings['globals']['units']
# 			status['name'] = settings['globals']['grill_name']
# 			status['start_time'] = display['start_time']
# 			status['start_duration'] = display['start_duration']
# 			status['shutdown_duration'] = display['shutdown_duration']
# 			status['prime_duration'] = display['prime_duration']
# 			status['prime_amount'] = display['prime_amount']
# 			status['lid_open_detected'] = display['lid_open_detected']
# 			status['lid_open_endtime'] = display['lid_open_endtime']
# 			status['p_mode'] = display['p_mode']
# 			status['outpins'] = display['outpins']
# 			status['startup_timestamp'] = display['startup_timestamp']
# 			status['ui_hash'] = create_ui_hash()
# 			return jsonify({'current':current_temps, 'notify_data':notify_data, 'status':status}), 201
# 		else:
# 			return jsonify({'Error':'Received GET request, without valid action'}), 404
	
# 	elif request.method == 'POST':
# 		if not request.json:
# 			event = "Local API Call Failed"
# 			write_log(event)
# 			abort(400)
# 		else:
# 			request_json = request.json
# 			if(action == 'settings'):
# 				settings = deep_update(settings, request.json)
# 				'''
# 				for key in settings.keys():
# 					if key in request_json.keys():
# 						settings[key].update(request_json.get(key, {}))
# 				'''
# 				write_settings(settings)
# 				return jsonify({'settings':'success'}), 201
# 			elif(action == 'control'):
# 				'''
# 					Updating of control input data is now done in common.py > execute_commands() 
# 				'''
# 				write_control(request.json, origin='app')
# 				return jsonify({'control':'success'}), 201
# 			else:
# 				return jsonify({'Error':'Received POST request no valid action.'}), 404
# 	else:
# 		return jsonify({'Error':'Received undefined/unsupported request.'}), 404

# '''
# Wizard Route for PiCycle Setup
# '''
# @app.route('/wizard/<action>', methods=['POST','GET'])
# @app.route('/wizard', methods=['GET', 'POST'])
# def wizard(action=None):
# 	global settings
# 	control = read_control()

# 	wizardData = read_wizard()
# 	errors = []

# 	if settings['globals']['venv']:
# 		python_exec = 'bin/python'
# 	else:
# 		python_exec = 'python'

# 	if request.method == 'GET':
# 		if action=='installstatus':
# 			percent, status, output = get_wizard_install_status()
# 			return jsonify({'percent' : percent, 'status' : status, 'output' : output}) 
# 	elif request.method == 'POST':
# 		r = request.form
# 		if action=='cancel':
# 			settings['globals']['first_time_setup'] = False
# 			write_settings(settings)
# 			return redirect('/')
# 		if action=='finish':
# 			if control['mode'] == 'Stop':
# 				wizardInstallInfo = prepare_wizard_data(r)
# 				store_wizard_install_info(wizardInstallInfo)
# 				set_wizard_install_status(0, 'Starting Install...', '')
# 				os.system(f'{python_exec} wizard.py &')	# Kickoff Installation
# 				return render_template('wizard-finish.html', page_theme=settings['globals']['page_theme'],
# 									grill_name=settings['globals']['grill_name'], wizardData=wizardData)
	
# 	''' Create Temporary Probe Device/Port Structure for Setup, Use Existing unless First Time Setup '''
# 	if settings['globals']['first_time_setup']: 
# 		wizardInstallInfo = wizardInstallInfoDefaults(wizardData)
# 	else:
# 		wizardInstallInfo = wizardInstallInfoExisting(wizardData, settings)

# 	store_wizard_install_info(wizardInstallInfo)

# 	if control['mode'] != 'Stop':
# 		errors.append('PiCycle configuration wizard cannot be run while the system is active.  Please stop the current cook before continuing.')

# 	return render_template('wizard.html', settings=settings, page_theme=settings['globals']['page_theme'],
# 						   grill_name=settings['globals']['grill_name'], wizardData=wizardData, wizardInstallInfo=wizardInstallInfo, control=control, errors=errors)

# def get_settings_dependencies_values(settings, moduleData):
# 	moduleSettings = {}
# 	for setting, data in moduleData['settings_dependencies'].items():
# 		setting_location = data['settings']
# 		setting_value = settings
# 		for setting_name in setting_location:
# 			setting_value = setting_value[setting_name]
# 		moduleSettings[setting] = setting_value 
# 	print(moduleSettings)
# 	return moduleSettings 

# def wizardInstallInfoDefaults(wizardData):
	
# 	wizardInstallInfo = {
# 		'modules' : {
# 			'grillplatform' : {
# 				'module_selected' : [],
# 				'settings' : {}
# 			}, 
# 			'display' : {
# 				'module_selected' : [],
# 				'settings' : {}
# 			}, 
# 			'distance' : {
# 				'module_selected' : [],
# 				'settings' : {}
# 			}, 
# 			'probes' : {
# 				'module_selected' : [],
# 				'settings' : {
# 					'units' : 'F'
# 				}
# 			}
# 		},
# 		'probe_map' : wizardData['boards']['PiCyclev2x']['probe_map']
# 	}
# 	''' Populate Modules Info with Defaults from Wizard Data including Settings '''
# 	for component in ['grillplatform', 'display', 'distance']:
# 		for module in wizardData['modules'][component]:
# 			if wizardData['modules'][component][module]['default']:
# 				''' Populate Module Filename'''
# 				wizardInstallInfo['modules'][component]['module_selected'].append(wizardData['modules'][component][module]['filename'])
# 				for setting in wizardData['modules'][component][module]['settings_dependencies']: 
# 					''' Populate all settings with default value '''
# 					wizardInstallInfo['modules'][component]['settings'][setting] = list(wizardData['modules'][component][module]['settings_dependencies'][setting]['options'].keys())[0]

# 	''' Populate Probes Module List with all configured probe devices '''
# 	for device in wizardInstallInfo['probe_map']['probe_devices']:
# 		wizardInstallInfo['modules']['probes']['module_selected'].append(device['module'])

# 	return wizardInstallInfo

# def wizardInstallInfoExisting(wizardData, settings):
# 	wizardInstallInfo = {
# 		'modules' : {
# 			'grillplatform' : {
# 				'module_selected' : [settings['modules']['grillplat']],
# 				'settings' : {}
# 			}, 
# 			'display' : {
# 				'module_selected' : [settings['modules']['display']],
# 				'settings' : {}
# 			}, 
# 			'distance' : {
# 				'module_selected' : [settings['modules']['dist']],
# 				'settings' : {}
# 			}, 
# 			'probes' : {
# 				'module_selected' : [],
# 				'settings' : {
# 					'units' : settings['globals']['units']
# 				}
# 			}
# 		}, 
# 		'probe_map' : settings['probe_settings']['probe_map']
# 	} 
# 	''' Populate Probes Module List with all configured probe devices '''
# 	for device in wizardInstallInfo['probe_map']['probe_devices']:
# 		wizardInstallInfo['modules']['probes']['module_selected'].append(device['module'])
	
# 	''' Populate Modules Info with current Settings '''
# 	for module in ['grillplatform', 'display', 'distance']:
# 		selected = wizardInstallInfo['modules'][module]['module_selected'][0]
# 		for setting in wizardData['modules'][module][selected]['settings_dependencies']:
# 			settingsLocation = wizardData['modules'][module][selected]['settings_dependencies'][setting]['settings']
# 			settingsValue = settings.copy() 
# 			for index in range(0, len(settingsLocation)):
# 				settingsValue = settingsValue[settingsLocation[index]]
# 			wizardInstallInfo['modules'][module]['settings'][setting] = str(settingsValue)

# 	return wizardInstallInfo

# def prepare_wizard_data(form_data):
# 	wizardData = read_wizard()
	
# 	wizardInstallInfo = load_wizard_install_info()

# 	wizardInstallInfo['modules'] = {
# 		'grillplatform' : {
# 			'module_selected' : [form_data['grillplatformSelect']],
# 			'settings' : {}
# 		}, 
# 		'display' : {
# 			'module_selected' : [form_data['displaySelect']],
# 			'settings' : {}
# 		}, 
# 		'distance' : {
# 			'module_selected' : [form_data['distanceSelect']],
# 			'settings' : {}
# 		}, 
# 		'probes' : {
# 			'module_selected' : [],
# 			'settings' : {
# 				'units' : form_data['probes_units']
# 			}
# 		}
# 	}

# 	for device in wizardInstallInfo['probe_map']['probe_devices']:
# 		wizardInstallInfo['modules']['probes']['module_selected'].append(device['module'])

# 	for module in ['grillplatform', 'display', 'distance']:
# 		module_ = module + '_'
# 		moduleSelect = module + 'Select'
# 		selected = form_data[moduleSelect]
# 		for setting in wizardData['modules'][module][selected]['settings_dependencies']:
# 			settingName = module_ + setting
# 			if(settingName in form_data):
# 				wizardInstallInfo['modules'][module]['settings'][setting] = form_data[settingName]

# 	return(wizardInstallInfo)

# '''
# Manifest Route for Web Application Integration
# '''
# @app.route('/manifest')
# def manifest():
# 	res = make_response(render_template('manifest.json'), 200)
# 	res.headers["Content-Type"] = "text/cache-manifest"
# 	return res

# '''
# Updater Function Routes
# '''
# @app.route('/checkupdate', methods=['GET'])
# def check_update(action=None):
# 	global settings
# 	update_data = {}
# 	update_data['version'] = settings['versions']['server']

# 	avail_updates_struct = get_available_updates()

# 	if avail_updates_struct['success']:
# 		commits_behind = avail_updates_struct['commits_behind']
# 	else:
# 		event = avail_updates_struct['message']
# 		write_log(event)
# 		return jsonify({'result' : 'failure', 'message' : avail_updates_struct['message'] })

# 	return jsonify({'result' : 'success', 'current' : update_data['version'], 'behind' : commits_behind})

# @app.route('/update/<action>', methods=['POST','GET'])
# @app.route('/update', methods=['POST','GET'])
# def update_page(action=None):
# 	global settings

# 	# Create Alert Structure for Alert Notification
# 	alert = {
# 		'type' : '',
# 		'text' : ''
# 	}

# 	if settings['globals']['venv']:
# 		python_exec = 'bin/python'
# 	else:
# 		python_exec = 'python'

# 	if request.method == 'GET':
# 		if action is None:
# 			update_data = get_update_data(settings)
# 			return render_template('updater.html', alert=alert, settings=settings,
# 								   page_theme=settings['globals']['page_theme'],
# 								   grill_name=settings['globals']['grill_name'],
# 								   update_data=update_data)
# 		elif action=='updatestatus':
# 			percent, status, output = get_updater_install_status()
# 			return jsonify({'percent' : percent, 'status' : status, 'output' : output})
		
# 		elif action=='post-message':
# 			try:
# 				with open('./updater/post-update-message.html','r') as file:
# 					post_update_message_html = " ".join(line.rstrip() for line in file)
# 			except:
# 				post_update_message_html = 'An error has occurred fetching the post-update message.' 
# 			return render_template_string(post_update_message_html)

# 	if request.method == 'POST':
# 		r = request.form
# 		update_data = get_update_data(settings)

# 		if 'update_remote_branches' in r:
# 			if is_real_hardware():
# 				os.system(f'{python_exec} %s %s &' % ('updater.py', '-r'))	 # Update branches from remote 
# 				time.sleep(5)  # Artificial delay to avoid race condition
# 			return redirect('/update')

# 		if 'change_branch' in r:
# 			if update_data['branch_target'] in r['branch_target']:
# 				alert = {
# 					'type' : 'success',
# 					'text' : f'Current branch {update_data["branch_target"]} already set to {r["branch_target"]}'
# 				}
# 				return render_template('updater.html', alert=alert, settings=settings,
# 									   page_theme=settings['globals']['page_theme'], update_data=update_data,
# 									   grill_name=settings['globals']['grill_name'])
# 			else:
# 				set_updater_install_status(0, 'Starting Branch Change...', '')
# 				os.system(f'{python_exec} updater.py -b {r["branch_target"]} &')	# Kickoff Branch Change
# 				return render_template('updater-status.html', page_theme=settings['globals']['page_theme'],
# 									   grill_name=settings['globals']['grill_name'])

# 		if 'do_update' in r:
# 			control = read_control()
# 			if control['mode'] == 'Stop':
# 				set_updater_install_status(0, 'Starting Update...', '')
# 				os.system(f'{python_exec} updater.py -u {update_data["branch_target"]} &') # Kickoff Update
# 				return render_template('updater-status.html', page_theme=settings['globals']['page_theme'],
# 									grill_name=settings['globals']['grill_name'])
# 			else:
# 				alert = {
# 					'type' : 'error',
# 					'text' : f'PiCycle System Update cannot be completed when the system is active.  Please shutdown/stop your smoker before retrying.'
# 				}
# 				update_data = get_update_data(settings)
# 				return render_template('updater.html', alert=alert, settings=settings,
# 									page_theme=settings['globals']['page_theme'],
# 									grill_name=settings['globals']['grill_name'],
# 									update_data=update_data)


# 		if 'show_log' in r:
# 			if r['show_log'].isnumeric():
# 				action='log'
# 				result, error_msg = get_log(num_commits=int(r['show_log']))
# 				if error_msg == '':
# 					output_html = f'*** Getting latest updates from origin/{update_data["branch_target"]} ***<br><br>' 
# 					output_html += result
# 				else: 
# 					output_html = f'*** Getting latest updates from origin/{update_data["branch_target"]} ERROR Occurred ***<br><br>' 
# 					output_html += error_msg
# 			else:
# 				output_html = '*** Error, Number of Commits Not Defined! ***<br><br>'
			
# 			return render_template('updater_out.html', settings=settings, page_theme=settings['globals']['page_theme'],
# 								   action=action, output_html=output_html, grill_name=settings['globals']['grill_name'])

# '''
# End Updater Section
# '''

# ''' 
# Metrics Routes
# '''
# @app.route('/metrics/<action>', methods=['POST','GET'])
# @app.route('/metrics', methods=['POST','GET'])
# def metrics_page(action=None):
# 	global settings
# 	control = read_control()

# 	metrics_data = process_metrics(read_metrics(all=True))

# 	if (request.method == 'GET') and (action == 'export'):
# 		filename = datetime.datetime.now().strftime('%Y%m%d-%H%M') + '-PiCycle-Metrics-Export'
# 		csvfilename = _prepare_metrics_csv(metrics_data, filename)
# 		return send_file(csvfilename, as_attachment=True, max_age=0)

# 	return render_template('metrics.html', settings=settings, control=control, page_theme=settings['globals']['page_theme'], 
# 							grill_name=settings['globals']['grill_name'], metrics_data=metrics_data)

# '''
# ==============================================================================
#  Supporting Functions
# ==============================================================================
# '''

# def _create_safe_name(name): 
# 	return("".join([x for x in name if x.isalnum()]))

# def _is_not_blank(response, setting):
# 	return setting in response and setting != ''

# def _is_checked(response, setting):
# 	return setting in response and response[setting] == 'on'

# def _allowed_file(filename):
# 	return '.' in filename and \
# 		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def _check_cpu_temp():
# 	temp = os.popen('vcgencmd measure_temp').readline()
# 	return temp.replace("temp=","")

# def create_ui_hash():
# 	global settings 
# 	return hash(json.dumps(settings['probe_settings']['probe_map']['probe_info']))

# def _prepare_annotations(displayed_starttime, metrics_data=[]):
# 	if(metrics_data == []):
# 		metrics_data = read_metrics(all=True)
# 	annotation_json = {}
# 	# Process Additional Metrics Information for Display
# 	for index in range(0, len(metrics_data)):
# 		# Check if metric falls in the displayed time window
# 		if metrics_data[index]['starttime'] > displayed_starttime:
# 			# Convert Start Time
# 			# starttime = epoch_to_time(metrics_data[index]['starttime']/1000)
# 			mode = metrics_data[index]['mode']
# 			color = 'blue'
# 			if mode == 'Startup':
# 				color = 'green'
# 			elif mode == 'Stop':
# 				color = 'red'
# 			elif mode == 'Shutdown':
# 				color = 'black'
# 			elif mode == 'Reignite':
# 				color = 'orange'
# 			elif mode == 'Error':
# 				color = 'red'
# 			elif mode == 'Hold':
# 				color = 'blue'
# 			elif mode == 'Smoke':
# 				color = 'grey'
# 			elif mode in ['Monitor', 'Manual']:
# 				color = 'purple'
# 			annotation = {
# 							'type' : 'line',
# 							'xMin' : metrics_data[index]['starttime'],
# 							'xMax' : metrics_data[index]['starttime'],
# 							'borderColor' : color,
# 							'borderWidth' : 2,
# 							'label': {
# 								'backgroundColor': color,
# 								'borderColor' : 'black',
# 								'color': 'white',
# 								'content': mode,
# 								'enabled': True,
# 								'position': 'end',
# 								'rotation': 0,
# 								},
# 							'display': True
# 						}
# 			annotation_json[f'event_{index}'] = annotation

# 	return(annotation_json)

# def _prepare_metrics_csv(metrics_data, filename):
# 	filename = filename.replace('.json', '')
# 	filename = filename.replace('./history/', '')
# 	filename = '/tmp/' + filename + '-PiCycle-Metrics-Export.csv'

# 	csvfile = open(filename, 'w')

# 	list_length = len(metrics_data) # Length of list

# 	if(list_length > 0):
# 		# Build the header row
# 		writeline=''
# 		for item in range(0, len(metrics_items)):
# 			writeline += f'{metrics_items[item][0]}, '
# 		writeline += '\n'
# 		csvfile.write(writeline)
# 		for index in range(0, list_length):
# 			writeline = ''
# 			for item in range(0, len(metrics_items)):
# 				writeline += f'{metrics_data[index][metrics_items[item][0]]}, '
# 			writeline += '\n'
# 			csvfile.write(writeline)
# 	else:
# 		writeline = 'No Data\n'
# 		csvfile.write(writeline)

# 	csvfile.close()
# 	return(filename)

# def _prepare_event_totals(events):
# 	auger_time = 0
# 	for index in range(0, len(events)):
# 		auger_time += events[index]['augerontime']
# 	auger_time = int(auger_time)

# 	event_totals = {}
# 	event_totals['augerontime'] = seconds_to_string(auger_time)

# 	grams = int(auger_time * settings['globals']['augerrate'])
# 	pounds = round(grams * 0.00220462, 2)
# 	ounces = round(grams * 0.03527392, 2)
# 	event_totals['estusage_m'] = f'{grams} grams'
# 	event_totals['estusage_i'] = f'{pounds} pounds ({ounces} ounces)'

# 	seconds = int((events[-1]['starttime']/1000) - (events[0]['starttime']/1000))
	
# 	event_totals['cooktime'] = seconds_to_string(seconds)

# 	event_totals['pellet_level_start'] = events[0]['pellet_level_start']
# 	event_totals['pellet_level_end'] = events[-2]['pellet_level_end']

# 	return(event_totals)

# def _paginate_list(datalist, sortkey='', reversesortorder=False, itemsperpage=10, page=1):
# 	if sortkey != '':
# 		#  Sort list if key is specified
# 		tempdatalist = sorted(datalist, key=lambda d: d[sortkey], reverse=reversesortorder)
# 	else:
# 		#  If no key, reverse list if specified, or keep order 
# 		if reversesortorder:
# 			datalist.reverse()
# 		tempdatalist = datalist.copy()
# 	listlength = len(tempdatalist)
# 	if listlength <= itemsperpage:
# 		curpage = 1
# 		prevpage = 1 
# 		nextpage = 1 
# 		lastpage = 1
# 		displaydata = tempdatalist.copy()
# 	else: 
# 		lastpage = (listlength // itemsperpage) + ((listlength % itemsperpage) > 0)
# 		if (lastpage < page):
# 			curpage = lastpage
# 			prevpage = curpage - 1 if curpage > 1 else 1
# 			nextpage = curpage + 1 if curpage < lastpage else lastpage 
# 		else: 
# 			curpage = page if page > 0 else 1
# 			prevpage = curpage - 1 if curpage > 1 else 1
# 			nextpage = curpage + 1 if curpage < lastpage else lastpage 
# 		#  Calculate starting / ending position and create list with that data
# 		start = itemsperpage * (curpage - 1)  # Get starting position 
# 		end = start + itemsperpage # Get ending position 
# 		displaydata = tempdatalist.copy()[start:end]

# 	reverse = 'true' if reversesortorder else 'false'

# 	pagination = {
# 		'displaydata' : displaydata,
# 		'curpage' : curpage,
# 		'prevpage' : prevpage,
# 		'nextpage' : nextpage, 
# 		'lastpage' : lastpage,
# 		'reverse' : reverse,
# 		'itemspage' : itemsperpage
# 	}

# 	return (pagination)

# def _get_cookfilelist(folder=HISTORY_FOLDER):
# 	# Grab list of Historical Cook Files
# 	if not os.path.exists(folder):
# 		os.mkdir(folder)
# 	dirfiles = os.listdir(folder)
# 	cookfiles = []
# 	for file in dirfiles:
# 		if file.endswith('.picycle'):
# 			cookfiles.append(file)
# 	return(cookfiles)

# def _get_cookfilelist_details(cookfilelist):
# 	cookfiledetails = []
# 	for item in cookfilelist:
# 		filename = HISTORY_FOLDER + item['filename']
# 		cookfiledata, status = read_json_file_data(filename, 'metadata')
# 		if(status == 'OK'):
# 			thumbnail = unpack_thumb(cookfiledata['thumbnail'], filename) if ('thumbnail' in cookfiledata) else ''
# 			cookfiledetails.append({'filename' : item['filename'], 'title' : cookfiledata['title'], 'thumbnail' : thumbnail})
# 		else:
# 			cookfiledetails.append({'filename' : item['filename'], 'title' : 'ERROR', 'thumbnail' : ''})
# 	return(cookfiledetails)

# def _get_recipefilelist(folder=RECIPE_FOLDER):
# 	# Grab list of Recipe Files
# 	if not os.path.exists(folder):
# 		os.mkdir(folder)
# 	dirfiles = os.listdir(folder)
# 	recipefiles = []
# 	for file in dirfiles:
# 		if file.endswith('.pfrecipe'):
# 			recipefiles.append(file)
# 	return(recipefiles)

# def _get_recipefilelist_details(recipefilelist):
# 	recipefiledetails = []
# 	for item in recipefilelist:
# 		filename = RECIPE_FOLDER + item['filename']
# 		recipefiledata, status = read_json_file_data(filename, 'metadata')
# 		if(status == 'OK'):
# 			thumbnail = unpack_thumb(recipefiledata['thumbnail'], filename) if ('thumbnail' in recipefiledata) else ''
# 			recipefiledetails.append({'filename' : item['filename'], 'title' : recipefiledata['title'], 'thumbnail' : thumbnail})
# 		else:
# 			recipefiledetails.append({'filename' : item['filename'], 'title' : 'ERROR', 'thumbnail' : ''})
# 	return(recipefiledetails)

# def _zip_files_dir(dir_name):
# 	memory_file = BytesIO()
# 	with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
# 		for root, dirs, files in os.walk(dir_name):
# 			for file in files:
# 				zipf.write(os.path.join(root, file))
# 	memory_file.seek(0)
# 	return memory_file

# def _zip_files_logs(dir_name):
# 	time_now = datetime.datetime.now()
# 	time_str = time_now.strftime('%m-%d-%y_%H%M%S') # Truncate the microseconds
# 	file_name = f'/tmp/PiCycle_Logs_{time_str}.zip'
# 	directory = pathlib.Path(f'{dir_name}')
# 	with zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED) as archive:
# 		for file_path in directory.rglob("*"):
# 			archive.write(file_path, arcname=file_path.relative_to(directory))
# 	return file_name

# '''
# ==============================================================================
#  SocketIO Section
# ==============================================================================
# '''
# thread = Thread()
# thread_lock = threading.Lock()
# clients = 0
# force_refresh = False

# @socketio.on("connect")
# def connect():
# 	global clients
# 	clients += 1

# @socketio.on("disconnect")
# def disconnect():
# 	global clients
# 	clients -= 1

# @socketio.on('get_dash_data')
# def get_dash_data(force=False):
# 	global thread
# 	global force_refresh
# 	force_refresh = force

# 	with thread_lock:
# 		if not thread.is_alive():
# 			thread = socketio.start_background_task(emit_dash_data)

# def emit_dash_data():
# 	global clients
# 	global force_refresh
# 	previous_data = ''

# 	while (clients > 0):
# 		control = read_control()
# 		pelletdb = read_pellet_db()
# 		probe_info = read_current()

# 		if control['timer']['end'] - time.time() > 0 or bool(control['timer']['paused']):
# 			timer_info = {
# 				'timer_paused' : bool(control['timer']['paused']),
# 				'timer_start_time' : math.trunc(control['timer']['start']),
# 				'timer_end_time' : math.trunc(control['timer']['end']),
# 				'timer_paused_time' : math.trunc(control['timer']['paused']),
# 				'timer_active' : 'true'
# 			}
# 		else:
# 			timer_info = {
# 				'timer_paused' : 'false',
# 				'timer_start_time' : '0',
# 				'timer_end_time' : '0',
# 				'timer_paused_time' : '0',
# 				'timer_active' : 'false'
# 			}

# 		current_data = {
# 			'probe_info' : probe_info,
# 			'notify_data' : control['notify_data'],
# 			'timer_info' : timer_info,
# 			'current_mode' : control['mode'],
# 			'smoke_plus' : control['s_plus'],
# 			'pwm_control' : control['pwm_control'],
# 			'hopper_level' : pelletdb['current']['hopper_level']
# 		}

# 		if force_refresh:
# 			socketio.emit('grill_control_data', current_data)
# 			force_refresh = False
# 			socketio.sleep(2)
# 		elif previous_data != current_data:
# 			socketio.emit('grill_control_data', current_data)
# 			previous_data = current_data
# 			socketio.sleep(2)
# 		else:
# 			socketio.sleep(2)

# @socketio.on('get_app_data')
# def get_app_data(action=None, type=None):
# 	global settings

# 	if action == 'settings_data':
# 		return settings

# 	elif action == 'pellets_data':
# 		return read_pellet_db()

# 	elif action == 'events_data':
# 		event_list, num_events = read_events()
# 		events_trim = []
# 		for x in range(min(num_events, 60)):
# 			events_trim.append(event_list[x])
# 		return { 'events_list' : events_trim }

# 	elif action == 'info_data':
# 		return {
# 			'uptime' : os.popen('uptime').readline(),
# 			'cpuinfo' : os.popen('cat /proc/cpuinfo').readlines(),
# 			'ifconfig' : os.popen('ifconfig').readlines(),
# 			'temp' : _check_cpu_temp(),
# 			'outpins' : settings['outpins'],
# 			'inpins' : settings['inpins'],
# 			'dev_pins' : settings['dev_pins'],
# 			'server_version' : settings['versions']['server'],
# 			'server_build' : settings['versions']['build'] }

# 	elif action == 'manual_data':
# 		control = read_control()
# 		return {
# 			'manual' : control['manual'],
# 			'mode' : control['mode'] }
# 	else:
# 		return {'response': {'result':'error', 'message':'Error: Received request without valid action'}}

# @socketio.on('post_app_data')
# def post_app_data(action=None, type=None, json_data=None):
# 	global settings

# 	if json_data is not None:
# 		request = json.loads(json_data)
# 	else:
# 		request = {''}

# 	if action == 'update_action':
# 		if type == 'settings':
# 			for key in request.keys():
# 				if key in settings.keys():
# 					settings = deep_update(settings, request)
# 					write_settings(settings)
# 					return {'response': {'result':'success'}}
# 				else:
# 					return {'response': {'result':'error', 'message':'Error: Key not found in settings'}}
# 		elif type == 'control':
# 			control = read_control()
# 			for key in request.keys():
# 				if key in control.keys():
# 					'''
# 						Updating of control input data is now done in common.py > execute_commands() 
# 					'''
# 					write_control(request, origin='app-socketio')
# 					return {'response': {'result':'success'}}
# 				else:
# 					return {'response': {'result':'error', 'message':'Error: Key not found in control'}}
# 		else:
# 			return {'response': {'result':'error', 'message':'Error: Received request without valid type'}}

# 	elif action == 'admin_action':
# 		if type == 'clear_history':
# 			write_log('Clearing History Log.')
# 			read_history(0, flushhistory=True)
# 			return {'response': {'result':'success'}}
# 		elif type == 'clear_events':
# 			write_log('Clearing Events Log.')
# 			os.system('rm /tmp/events.log')
# 			return {'response': {'result':'success'}}
# 		elif type == 'clear_pelletdb':
# 			write_log('Clearing Pellet Database.')
# 			os.system('rm pelletdb.json')
# 			return {'response': {'result':'success'}}
# 		elif type == 'clear_pelletdb_log':
# 			pelletdb = read_pellet_db()
# 			pelletdb['log'].clear()
# 			write_pellet_db(pelletdb)
# 			write_log('Clearing Pellet Database Log.')
# 			return {'response': {'result':'success'}}
# 		elif type == 'factory_defaults':
# 			read_history(0, flushhistory=True)
# 			read_control(flush=True)
# 			os.system('rm settings.json')
# 			settings = default_settings()
# 			control = default_control()
# 			write_settings(settings)
# 			write_control(control, origin='app-socketio')
# 			write_log('Resetting Settings, Control, History to factory defaults.')
# 			return {'response': {'result':'success'}}
# 		elif type == 'reboot':
# 			write_log("Admin: Reboot")
# 			os.system("sleep 3 && sudo reboot &")
# 			return {'response': {'result':'success'}}
# 		elif type == 'shutdown':
# 			write_log("Admin: Shutdown")
# 			os.system("sleep 3 && sudo shutdown -h now &")
# 			return {'response': {'result':'success'}}
# 		elif type == 'restart':
# 			write_log("Admin: Restart Server")
# 			restart_scripts()
# 			return {'response': {'result':'success'}}
# 		else:
# 			return {'response': {'result':'error', 'message':'Error: Received request without valid type'}}

# 	elif action == 'units_action':
# 		if type == 'f_units' and settings['globals']['units'] == 'C':
# 			settings = convert_settings_units('F', settings)
# 			write_settings(settings)
# 			control = read_control()
# 			control['updated'] = True
# 			control['units_change'] = True
# 			write_control(control, origin='app-socketio')
# 			write_log("Changed units to Fahrenheit")
# 			return {'response': {'result':'success'}}
# 		elif type == 'c_units' and settings['globals']['units'] == 'F':
# 			settings = convert_settings_units('C', settings)
# 			write_settings(settings)
# 			control = read_control()
# 			control['updated'] = True
# 			control['units_change'] = True
# 			write_control(control, origin='app-socketio')
# 			write_log("Changed units to Celsius")
# 			return {'response': {'result':'success'}}
# 		else:
# 			return {'response': {'result':'error', 'message':'Error: Units could not be changed'}}

# 	elif action == 'remove_action':
# 		if type == 'onesignal_device':
# 			if 'onesignal_player_id' in request['onesignal_device']:
# 				device = request['onesignal_device']['onesignal_player_id']
# 				if device in settings['onesignal']['devices']:
# 					settings['onesignal']['devices'].pop(device)
# 				write_settings(settings)
# 				return {'response': {'result':'success'}}
# 			else:
# 				return {'response': {'result':'error', 'message':'Error: Device not specified'}}
# 		else:
# 			return {'response': {'result':'error', 'message':'Error: Remove type not found'}}

# 	elif action == 'pellets_action':
# 		pelletdb = read_pellet_db()
# 		if type == 'load_profile':
# 			if 'profile' in request['pellets_action']:
# 				pelletdb['current']['pelletid'] = request['pellets_action']['profile']
# 				now = str(datetime.datetime.now())
# 				now = now[0:19]
# 				pelletdb['current']['date_loaded'] = now
# 				pelletdb['current']['est_usage'] = 0
# 				pelletdb['log'][now] = request['pellets_action']['profile']
# 				control = read_control()
# 				control['hopper_check'] = True
# 				write_control(control, origin='app-socketio')
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			else:
# 				return {'response': {'result':'error', 'message':'Error: Profile not included in request'}}
# 		elif type == 'hopper_check':
# 			control = read_control()
# 			control['hopper_check'] = True
# 			write_control(control, origin='app-socketio')
# 			return {'response': {'result':'success'}}
# 		elif type == 'edit_brands':
# 			if 'delete_brand' in request['pellets_action']:
# 				delBrand = request['pellets_action']['delete_brand']
# 				if delBrand in pelletdb['brands']:
# 					pelletdb['brands'].remove(delBrand)
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			elif 'new_brand' in request['pellets_action']:
# 				newBrand = request['pellets_action']['new_brand']
# 				if newBrand not in pelletdb['brands']:
# 					pelletdb['brands'].append(newBrand)
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			else:
# 				return {'response': {'result':'error', 'message':'Error: Function not specified'}}
# 		elif type == 'edit_woods':
# 			if 'delete_wood' in request['pellets_action']:
# 				delWood = request['pellets_action']['delete_wood']
# 				if delWood in pelletdb['woods']:
# 					pelletdb['woods'].remove(delWood)
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			elif 'new_wood' in request['pellets_action']:
# 				newWood = request['pellets_action']['new_wood']
# 				if newWood not in pelletdb['woods']:
# 					pelletdb['woods'].append(newWood)
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			else:
# 				return {'response': {'result':'error', 'message':'Error: Function not specified'}}
# 		elif type == 'add_profile':
# 			profile_id = ''.join(filter(str.isalnum, str(datetime.datetime.now())))
# 			pelletdb['archive'][profile_id] = {
# 				'id' : profile_id,
# 				'brand' : request['pellets_action']['brand_name'],
# 				'wood' : request['pellets_action']['wood_type'],
# 				'rating' : request['pellets_action']['rating'],
# 				'comments' : request['pellets_action']['comments'] }
# 			if request['pellets_action']['add_and_load']:
# 				pelletdb['current']['pelletid'] = profile_id
# 				control = read_control()
# 				control['hopper_check'] = True
# 				write_control(control, origin='app-socketio')
# 				now = str(datetime.datetime.now())
# 				now = now[0:19]
# 				pelletdb['current']['date_loaded'] = now
# 				pelletdb['current']['est_usage'] = 0
# 				pelletdb['log'][now] = profile_id
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			else:
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 		if type == 'edit_profile':
# 			if 'profile' in request['pellets_action']:
# 				profile_id = request['pellets_action']['profile']
# 				pelletdb['archive'][profile_id]['brand'] = request['pellets_action']['brand_name']
# 				pelletdb['archive'][profile_id]['wood'] = request['pellets_action']['wood_type']
# 				pelletdb['archive'][profile_id]['rating'] = request['pellets_action']['rating']
# 				pelletdb['archive'][profile_id]['comments'] = request['pellets_action']['comments']
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			else:
# 				return {'response': {'result':'error', 'message':'Error: Profile not included in request'}}
# 		if type == 'delete_profile':
# 			if 'profile' in request['pellets_action']:
# 				profile_id = request['pellets_action']['profile']
# 				if pelletdb['current']['pelletid'] == profile_id:
# 					return {'response': {'result':'error', 'message':'Error: Cannot delete current profile'}}
# 				else:
# 					pelletdb['archive'].pop(profile_id)
# 					for index in pelletdb['log']:
# 						if pelletdb['log'][index] == profile_id:
# 							pelletdb['log'][index] = 'deleted'
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			else:
# 				return {'response': {'result':'error', 'message':'Error: Profile not included in request'}}
# 		elif type == 'delete_log':
# 			if 'log_item' in request['pellets_action']:
# 				delLog = request['pellets_action']['log_item']
# 				if delLog in pelletdb['log']:
# 					pelletdb['log'].pop(delLog)
# 				write_pellet_db(pelletdb)
# 				return {'response': {'result':'success'}}
# 			else:
# 				return {'response': {'result':'error', 'message':'Error: Function not specified'}}
# 		else:
# 			return {'response': {'result':'error', 'message':'Error: Received request without valid type'}}

# 	elif action == 'timer_action':
# 		control = read_control()
# 		for index, notify_obj in enumerate(control['notify_data']):
# 			if notify_obj['type'] == 'timer':
# 				break
# 		if type == 'start_timer':
# 			control['notify_data'][index]['req'] = True
# 			if control['timer']['paused'] == 0:
# 				now = time.time()
# 				control['timer']['start'] = now
# 				if 'hours_range' in request['timer_action'] and 'minutes_range' in request['timer_action']:
# 					seconds = request['timer_action']['hours_range'] * 60 * 60
# 					seconds = seconds + request['timer_action']['minutes_range'] * 60
# 					control['timer']['end'] = now + seconds
# 					control['notify_data'][index]['shutdown'] = request['timer_action']['timer_shutdown']
# 					control['notify_data'][index]['keep_warm'] = request['timer_action']['timer_keep_warm']
# 					write_log('Timer started.  Ends at: ' + epoch_to_time(control['timer']['end']))
# 					write_control(control, origin='app-socketio')
# 					return {'response': {'result':'success'}}
# 				else:
# 					return {'response': {'result':'error', 'message':'Error: Start time not specified'}}
# 			else:
# 				now = time.time()
# 				control['timer']['end'] = (control['timer']['end'] - control['timer']['paused']) + now
# 				control['timer']['paused'] = 0
# 				write_log('Timer unpaused.  Ends at: ' + epoch_to_time(control['timer']['end']))
# 				write_control(control, origin='app-socketio')
# 				return {'response': {'result':'success'}}
# 		elif type == 'pause_timer':
# 			control['notify_data'][index]['req'] = False
# 			now = time.time()
# 			control['timer']['paused'] = now
# 			write_log('Timer paused.')
# 			write_control(control, origin='app-socketio')
# 			return {'response': {'result':'success'}}
# 		elif type == 'stop_timer':
# 			control['notify_data'][index]['req'] = False
# 			control['timer']['start'] = 0
# 			control['timer']['end'] = 0
# 			control['timer']['paused'] = 0
# 			control['notify_data'][index]['shutdown'] = False
# 			control['notify_data'][index]['keep_warm'] = False
# 			write_log('Timer stopped.')
# 			write_control(control, origin='app-socketio')
# 			return {'response': {'result':'success'}}
# 		else:
# 			return {'response': {'result':'error', 'message':'Error: Received request without valid type'}}
# 	else:
# 		return {'response': {'result':'error', 'message':'Error: Received request without valid action'}}

'''
==============================================================================
 Main Program Start
==============================================================================
'''
settings = read_settings(init=True)
ui_port = int(settings['globals']['ui_port'])

if __name__ == '__main__':
	if is_real_hardware():
		socketio.run(app, host='0.0.0.0', port=ui_port)
	else:
		socketio.run(app, host='0.0.0.0', port=ui_port, debug=True)
