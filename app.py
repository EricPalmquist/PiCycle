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
#from flask_mobility import Mobility
from flask_socketio import SocketIO
#from flask_qrcode import QRcode
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

server_status = 'available'

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

'''
==============================================================================
 App Routes
==============================================================================
'''
@app.route('/')
def index():
	global settings
	return redirect('/dash')

@app.route('/dash')
def dash():
	
	global settings
	control = read_control()

	return render_template('picycle.html',
 						   control=control,
						   page_theme=settings['globals']['page_theme'],
						   cycle_name=settings['globals']['cycle_name'])

@app.route('/settings/<action>', methods=['POST','GET'])
@app.route('/settings', methods=['POST','GET'])
def settings_page(action=None):

	global settings
	#control = read_control()
	
	# When someone clicks SAVE the settings global form we will land here
	if request.method == 'POST' and action == 'global':
		response = request.form

		if _is_checked(response, 'debug_mode'):
			settings['globals']['debug_mode'] = True
		else:
			settings['globals']['debug_mode'] = False
		
		if _is_checked(response, 'real_hw'):
			settings['globals']['real_hw'] = True
		else:
			settings['globals']['real_hw'] = False
		
		if _is_checked(response, 'darkmode'):
			settings['globals']['page_theme'] = 'dark'
		else:
			settings['globals']['page_theme'] = 'light'		
		
		if _is_not_blank(response, 'wheel_rad_inches'):
			settings['globals']['wheel_rad_inches'] = response['wheel_rad_inches']
		
		if _is_not_blank(response, 'ui_port'):
			settings['globals']['ui_port'] = int(response['ui_port'])
		
		if _is_not_blank(response, 'cycle_name'):
			settings['globals']['cycle_name'] = response['cycle_name']

	if request.method == 'POST' and action == 'gpio':
		response = request.form

		if _is_not_blank(response, 'gpio_wheel'):
			settings['gpio_assignments']['wheel']['pulses'] = response['gpio_wheel']

		if _is_not_blank(response, 'gpio_dc'):
			settings['gpio_assignments']['display']['dc'] = response['gpio_dc']

		if _is_not_blank(response, 'gpio_led'):
			settings['gpio_assignments']['display']['led'] = response['gpio_led']

		if _is_not_blank(response, 'gpio_rst'):
			settings['gpio_assignments']['display']['rst'] = response['gpio_rst']

		#control['settings_update'] = True

		write_settings(settings)
		#write_control(control, origin='app')

	return render_template('settings.html',
						   settings=settings,
						   page_theme=settings['globals']['page_theme'],
						   cycle_name=settings['globals']['cycle_name'])

@app.route('/api', methods=['GET'])
@app.route('/api/<action>', methods=['GET'])
def api_page(action=None, arg0=None, arg1=None, arg2=None, arg3=None):
	global settings
	global server_status
	
	if request.method == 'GET':
		if action == 'current':
			''' Only fetch data from RedisDB or locally available, to improve performance '''
			current = read_current()
			return jsonify({'current':current}), 201
		else:
			return jsonify({'Error':'Received GET request, without valid action'}), 404

'''
==============================================================================
 Supporting Functions
==============================================================================
'''

def _is_not_blank(response, setting):
	return setting in response and setting != ''

def _is_checked(response, setting):
	return setting in response and response[setting] == 'on'

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
		socketio.run(app, host='0.0.0.0', debug=True)