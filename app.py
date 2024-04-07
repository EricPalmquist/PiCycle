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
'''
==============================================================================
 Main Program Start
==============================================================================
'''
settings = read_settings(init=True)
ui_port = int(settings['globals']['ui_port'])

if __name__ == '__main__':
	if is_real_hardware():
		socketio.run(app, host='0.0.0.0')
	else:
		socketio.run(app, host='0.0.0.0', debug=True)