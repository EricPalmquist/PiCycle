#!/usr/bin/env python3
'''
*****************************************
PiFire Display Interface Library
*****************************************

 Description: 
   This is a base class for displays using 
 a 240Hx320W resolution.  Other display 
 libraries will inherit this base class 
 and add device specific features.

*****************************************
'''

'''
 Imported Libraries
'''
import os
import time
import socket
import qrcode
import logging
from PIL import Image, ImageDraw, ImageFont
from common import read_control, write_control

'''
Display base class definition
'''
class DisplayBase:

	def __init__(self, dev_pins, config={}):
		
		print('init base')
		# Init Global Variables and Constants
		self.dev_pins = dev_pins
		#self.buttonslevel = config['buttonslevel']
		self.rotation = int(config['rotation'])
		self.display_active = False
		self.in_data = None
		self.status_data = None
		self.display_timeout = None
		self.display_command = 'splash'
		self.input_counter = 0
		self.input_enabled = False
		self.primary_font = 'trebuc.ttf'
		#self.primary_font = 'DejaVuSans.ttf'  # May need to switch to a default font in Raspberry Pi OS Lite due to MSTCorefonts Package Deprecation 
		# Attempt to set the log level of PIL so that it does not pollute the logs
		logging.getLogger('PIL').setLevel(logging.CRITICAL + 1)
		# Init Display Device, Input Device, Assets
		self._init_globals()
		self._init_assets() 
		self._init_input()
		self._init_display_device()

	def _init_globals(self):
		# Init constants and variables
		'''
		0 = Zero Degrees Rotation
		90, 1 = 90 Degrees Rotation (Pimoroni Libraries, Luma.LCD Libraries)
		180, 2 = 180 Degrees Rotation (Pimoroni Libraries, Luma.LCD Libraries)
		270, 3 = 270 Degrees Rotation (Pimoroni Libraries, Luma.LCD Libraries)
		'''
		if self.rotation in [90, 270, 1, 3]:
			self.WIDTH = 240
			self.HEIGHT = 320
		else:
			self.WIDTH = 320
			self.HEIGHT = 240

		self.inc_pulse_color = True 
		self.icon_color = 100

	def _init_display_device(self):
		'''
        Inheriting classes will override this function to init the display device and start the display thread.
        '''
		pass

	def _init_input(self):
		'''
		Inheriting classes will override this function to setup the inputs.
		'''
		self.input_enabled = False  # If the inheriting class does not implement input, then clear this flag
		self.input_counter = 0

	def _init_menu(self):
		self.menu_active = False
		self.menu_time = 0
		self.menu_item = ''

		self.menu = {}

		self.menu['inactive'] = {
			# List of options for the 'inactive' menu.  This is the initial menu when smoker is not running.
			'Start': {
				'displaytext': 'Start',
				'icon': '\uf04b', # FontAwesome Play Icon
				'iconcolor': (255,255,255)  
			},
			'Network': {
				'displaytext': 'IP QR Code',
				'icon': '\uf1eb', # FontAwesome Wifi Icon
				'iconcolor': (255,255,255)
			},
			'Power':{
				'displaytext': 'Power Menu',
				'icon': '\uf0e7', #FontAwesome Power Icon
				'iconcolor' : (255,255,255)
			}
		}

		self.menu['active'] = {
			# List of options for the 'active' menu.  This is the second level menu of options while running.
			'Stop': {
				'displaytext': 'Stop',
				'icon': '\uf04d',  # FontAwesome Stop Icon
				'iconcolor': (255,255,255)
			},
			'Network': {
				'displaytext': 'IP QR Code',
				'icon': '\uf1eb', # FontAwesome Wifi Icon
				'iconcolor': (255,255,255)
			},
		}

		self.menu['power_menu'] = {
			'Power_Off' : {
				'displaytext' : 'Shutdown',
				'icon': '\uf011', # FontAwesome Power Button
				'iconcolor': (255,255,255)
			},
			'Power_Restart' : {
				'displaytext': 'Restart',
				'icon': '\uf2f9', # FontAwesome Circle Arrow
				'iconcolor': (255,255,255)
			},
			'Menu_Back' : {
				'displaytext' : 'Back',
				'icon' : '\uf060', # FontAwesome Back Arrow
				'iconcolor': (255,255,255)
			}
		}

		self.menu['current'] = {}
		self.menu['current']['mode'] = 'none'  # Current Menu Mode (inactive, active)
		self.menu['current']['option'] = 0  # Current option in current mode

	def _display_loop(self):
		"""
		Main display loop
		"""
		while True:
		
			#print(f'display_command={self.display_command}')

			if self.input_enabled:
				self._event_detect()

			if self.display_timeout:
				if time.time() > self.display_timeout:
					self.display_timeout = None
					if not self.display_active:
						self.display_command = 'clear'

			if self.display_command == 'clear':
				self.display_active = False
				self.display_timeout = None
				self.display_command = None
				self._display_clear()

			if self.display_command == 'splash':
				self._display_splash()
				self.display_timeout = time.time() + 3
				self.display_command = 'clear'
				time.sleep(3) # Hold splash screen for 3 seconds

			if self.display_command == 'text':
				self._display_text()
				self.display_command = None
				self.display_timeout = time.time() + 10

			if self.display_command == 'network':
				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				s.connect(("8.8.8.8", 80))
				network_ip = s.getsockname()[0]
				if network_ip != '':
					self._display_network(network_ip)
					self.display_timeout = time.time() + 30
					self.display_command = None
				else:
					self.display_text("No IP Found")
			
			# input("Press Enter to continue...")
			if self.input_enabled:
				#print('a', self.menu_active, self.display_timeout, self.display_active)
				if self.menu_active and not self.display_timeout:
					if time.time() - self.menu_time > 5:
						self.menu_active = False
						self.menu['current']['mode'] = 'none'
						self.menu['current']['option'] = 0
						if not self.display_active:
							self.display_command = 'clear'
				elif not self.display_timeout and self.display_active:
					#print(self.in_data)
					if self.in_data is not None:
						self._display_current(self.in_data)

			elif not self.display_timeout and self.display_active:
				if self.in_data is not None:
					self._display_current(self.in_data)

			time.sleep(0.1)

	'''
	============== Input Callbacks ============= 
	
	Inheriting classes will override these functions for all inputs.
	'''
	def _enter_callback(self):
		'''
		Inheriting classes will override this function.
		'''
		pass

	def _up_callback(self, held=False):
		'''
		Inheriting classes will override this function to clear the display device.
		'''
		pass
	
	def _down_callback(self, held=False):
		'''
		Inheriting classes will override this function to clear the display device.
		'''
		pass

	def _encoder_callback(self):
		'''
		Inheriting classes will override this function to read a rotary encoder.
		'''
		pass

	'''
	============== Graphics / Display / Draw Methods ============= 
	'''
	def _init_assets(self): 
		self._init_background()
		self._init_splash()

	def _init_background(self):
		self.background = Image.open('static/img/display/background.jpg')
		self.background = self.background.resize((self.WIDTH, self.HEIGHT))
	
	def _init_splash(self):
		self.splash = Image.open('static/img/display/color-boot-splash.png')
		(self.splash_width, self.splash_height) = self.splash.size
		self.splash_width *= 2
		self.splash_height *= 2
		self.splash = self.splash.resize((self.splash_width, self.splash_height))

	def _rounded_rectangle(self, draw, xy, rad, fill=None):
		x0, y0, x1, y1 = xy
		draw.rectangle([(x0, y0 + rad), (x1, y1 - rad)], fill=fill)
		draw.rectangle([(x0 + rad, y0), (x1 - rad, y1)], fill=fill)
		draw.pieslice([(x0, y0), (x0 + rad * 2, y0 + rad * 2)], 180, 270, fill=fill)
		draw.pieslice([(x1 - rad * 2, y1 - rad * 2), (x1, y1)], 0, 90, fill=fill)
		draw.pieslice([(x0, y1 - rad * 2), (x0 + rad * 2, y1)], 90, 180, fill=fill)
		draw.pieslice([(x1 - rad * 2, y0), (x1, y0 + rad * 2)], 270, 360, fill=fill)

	def _draw_text(self, text, font_name, font_point_size, text_color, rect=False, fill_color=None, outline_color=None):
		font = ImageFont.truetype(font_name, font_point_size)
		font_bbox = font.getbbox(str(text))  # Grab the width of the text
		font_canvas_size = (font_bbox[2], font_bbox[3])
		font_canvas = Image.new('RGBA', font_canvas_size)
		font_draw = ImageDraw.Draw(font_canvas)
		font_draw.text((0,0), str(text), font=font, fill=text_color)
		if rect:
			font_canvas = font_canvas.crop(font_canvas.getbbox())
			font_canvas_size = font_canvas.size 
			rect_canvas_size = (font_canvas_size[0] + 16, font_canvas_size[1] + 16)
			rect_canvas = Image.new('RGBA', rect_canvas_size)
			rect_draw = ImageDraw.Draw(rect_canvas)
			rect_draw.rounded_rectangle((0, 0, rect_canvas_size[0], rect_canvas_size[1]), radius=8, fill=fill_color, outline=outline_color, width=3)
			rect_canvas.paste(font_canvas, (8,8), font_canvas) 
			return rect_canvas 
		return font_canvas.crop(font_canvas.getbbox())

	def _text_circle(self, draw, position, size, text, fg_color=(255,255,255), bg_color=(0,0,0)):
		# Draw outline with fg_color
		coords = (position[0], position[1], position[0] + size[0], position[1] + size[1])
		draw.ellipse(coords, fill=fg_color)
		# Fill circle with Center with bg_color
		fill_coords = (coords[0]+2, coords[1]+2, coords[2]-2, coords[3]-2)
		draw.ellipse(fill_coords, fill=bg_color)
		# Place Text
		font_point_size = round(size[1] * 0.6)  # Convert size to height of circle * font point ratio 0.6
		font = ImageFont.truetype(self.primary_font, font_point_size)
		font_bbox = font.getbbox(str(text))  # Grab the bounding box of the text
		font_width = font_bbox[2]
		label_x = position[0] + (size[0] // 2) - (font_width // 2)
		label_y = position[1] + round((size[1] // 2) - (font_point_size // 2))  
		label_origin = (label_x, label_y)
		draw.text(label_origin, text, font=font, fill=fg_color)

	def _create_icon(self, charid, size, color):
		icon_canvas = self._draw_text(charid, 'static/font/FA-Free-Solid.otf', size, color)
		return(icon_canvas)

	def _paste_icon(self, icon, canvas, position, rotation):
		# Rotate the icon
		icon = icon.rotate(rotation)
		# Set the position & paste the icon onto the canvas
		canvas.paste(icon, position, icon)
		return(canvas)

	def _draw_pause_icon(self, canvas, position):
		# Create a drawing object
		draw = ImageDraw.Draw(canvas)

		# Recipe Pause Icon
		icon_char = '\uf04c'
		icon_color = (255,self.icon_color, 0)

		# Draw Rounded Rectangle Border
		self._rounded_rectangle(draw, 
			(position[0], position[1], 
			position[0] + 42, position[1] + 42), 
			5, icon_color)

		# Fill Rectangle with Black
		self._rounded_rectangle(draw, 
			(position[0] + 2, position[1] + 2, 
			position[0] + 40, position[1] + 40), 
			5, (0,0,0))

		# Create Icon Image
		icon = self._create_icon(icon_char, 28, icon_color)
		icon_position = (position[0] + 9, position[1] + 9)
		canvas = self._paste_icon(icon, canvas, icon_position, 0)

		return canvas

	def _draw_gauge(self, canvas, position, size, fg_color, bg_color, percents, temps, label, sp1_color=(0, 200, 255), sp2_color=(255, 255, 0)):
		# Create drawing object
		draw = ImageDraw.Draw(canvas)
		# bgcolor = (50, 50, 50)  # Grey
		# fgcolor = (200, 0, 0)  # Red
		# percents = [temperature, setpoint1, setpoint2]
		# temps = [current, setpoint1, setpoint2]
		# sp1_color = (0, 200, 255)  # Cyan 
		# sp2_color = (255, 255, 0)  # Yellow
		fill_color = (0, 0, 0)  # Black 

		# Draw Background Line
		coords = (position[0], position[1], position[0] + size[0], position[1] + size[1])
		draw.ellipse(coords, fill=bg_color)

		# Draw Arc for Temperature (Percent)
		if (percents[0] > 0) and (percents[0] < 100):
			endpoint = (360 * (percents[0] / 100)) + 90 
		elif percents[0] > 100:
			endpoint = 360 + 90
		else:
			endpoint = 90 
		draw.pieslice(coords, start=90, end=endpoint, fill=fg_color)

		# Draw Tic for Setpoint[1] 
		if percents[1] > 0:
			if percents[1] < 100:
				setpoint = (360 * (percents[1] / 100)) + 90 
			else: 
				setpoint = 360 + 90 
			draw.pieslice(coords, start=setpoint - 2, end=setpoint + 2, fill=sp1_color)

		# Draw Tic for Setpoint[2] 
		if percents[2] > 0:
			if percents[2] < 100:
				setpoint = (360 * (percents[2] / 100)) + 90 
			else: 
				setpoint = 360 + 90 
			draw.pieslice(coords, start=setpoint - 2, end=setpoint + 2, fill=sp2_color)

		# Fill Circle with Center with black
		fill_coords = (coords[0]+10, coords[1]+10, coords[2]-10, coords[3]-10)
		draw.ellipse(fill_coords, fill=fill_color)

		# Gauge Label
		if len(label) <= 5:
			font_point_size = round((size[1] * 0.75) / 4) + 1 # Convert size to height of circle * font point ratio / 8
		elif len(label) <= 6: 
			font_point_size = round((size[1] * 0.60) / 4) + 1 # Convert size to height of circle * font point ratio / 8
		else:
			font_point_size = round((size[1] * 0.40) / 4) + 1 # Convert size to height of circle * font point ratio / 8
		label_canvas = self._draw_text(label, self.primary_font, font_point_size, (255,255,255))
		label_x = int(position[0] + (size[0] // 2) - (label_canvas.width // 2))
		label_y = int(position[1] + (round(((size[1] * 0.75) / 8) * 6.6)))
		label_origin = (label_x, label_y)
		canvas.paste(label_canvas, label_origin, label_canvas)

		# SetPoint1 Label 
		if percents[1] > 0:
			sp1_label = f'>{temps[1]}<'
			font_point_size = round((size[1] * 0.6) / 4) # Convert size to height of circle * font point ratio
			label_canvas = self._draw_text(sp1_label, self.primary_font, font_point_size, sp1_color)
			label_x = int(position[0] + (size[0] // 2) - (label_canvas.width // 2))
			label_y = int(position[1] + round(size[1] / 8))
			label_origin = (label_x, label_y)
			canvas.paste(label_canvas, label_origin, label_canvas)

		# Current Temperature (Large Centered)
		cur_temp = str(temps[0])[:5]
		if self.units == 'F':
			font_point_size = round(size[1] * 0.4)  # Convert size to height of circle * font point ratio / 8
		else:
			font_point_size = round(size[1] * 0.3)  # Convert size to height of circle * font point ratio / 8
		label_canvas = self._draw_text(cur_temp, self.primary_font, font_point_size, (255,255,255))
		label_x = int(position[0] + (size[0] // 2) - (label_canvas.width // 2))
		label_y = int(position[1] + ((size[1] // 1.8) - (font_point_size // 1.5)))
		label_origin = (label_x, label_y)
		canvas.paste(label_canvas, label_origin, label_canvas)

		return(canvas)

	def _display_clear(self):
		'''
		Inheriting classes will override this function to clear the display device.
		'''
		pass

	def _display_canvas(self, canvas):
		'''
		Inheriting classes will override this function to show the canvas on the display device.
		'''
		pass

	def _display_splash(self):
		# Create canvas
		img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))

		# Set the position & paste the splash image onto the canvas
		position = ((self.WIDTH - self.splash_width) // 2, (self.HEIGHT - self.splash_height) // 2)
		img.paste(self.splash, position, self.splash)

		self._display_canvas(img)

	def _display_text(self):
		# Create canvas
		img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))

		label_canvas = self._draw_text(self.display_data, self.primary_font, 42, (255,255,0))
		label_x = (self.WIDTH // 2 - label_canvas.width // 2)
		label_y = self.HEIGHT // 2 - label_canvas.height // 2
		label_origin = (label_x, label_y)
		img.paste(label_canvas, label_origin, label_canvas)

		self._display_canvas(img)

	def _display_network(self, network_ip):
		# Create canvas
		img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(255, 255, 255))
		img_qr = qrcode.make('http://' + network_ip)
		img_qr_width, img_qr_height = img_qr.size
		img_qr_width *= 2
		img_qr_height *= 2
		w = min(self.WIDTH, self.HEIGHT)
		new_image = img_qr.resize((w, w))
		position = (int((self.WIDTH/2)-(w/2)), 0)
		img.paste(new_image, position)

		self._display_canvas(img)

	def _display_current(self, in_data):
		
		# current['curr_speed'] = speed_input.curr_speed()
		# current['avg_speed'] = speed_input.avg_speed()
		# current['distance'] = speed_input.distance()
		
		# Create canvas
		img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))

		# Set the position and paste the background image onto the canvas
		# Note: 0,0 is the upper left corner, so 320 is the right side and 240 is the bottom.
		# +------------------------------------------+
		# | (0,0)                             (320,0)|
		# |                                          |
		# |                                          |
		# |                                          |
		# | (0,240)                         (320,240)|
		# +------------------------------------------+
	
		position = (0, 0)

		#TODO - get a better background image!
		img.paste(self.background, position)

		# Create drawing object
		draw = ImageDraw.Draw(img)

		# ========  Circle Gauge ========
		# position = (self.WIDTH // 2 - 80, self.HEIGHT // 2 - 110)
		# size = (160, 160)
		# bg_color = (50, 50, 50)  # Grey
		# fg_color = (200, 0, 0)  # Red

		speed = in_data['curr_speed']
		avg_speed = in_data['avg_speed']
		distance = in_data['distance']

		# This is where we could get fancy with stuff like gauges
		#img = self._draw_gauge(img, position, size, fg_color, bg_color, 
		#	percents, temps, label)
  
		# Add the speed
		txt = f'Speed: {speed:.1f}'
		speed_canvas = self._draw_text(text=txt, font_name=self.primary_font, font_point_size=40, text_color=(0,0,0), rect=True, 
								 outline_color=(3, 161, 252), fill_color=(255,255,255))
		if self.WIDTH == 240:
			coords = (self.WIDTH // 2 - (speed_canvas.width // 2), 0)
		else:
			# Leave 1/8 of a screen padding on top and left
			coords = (self.WIDTH // 8, self.HEIGHT // 8)
		img.paste(speed_canvas, coords, speed_canvas)
		
		# Add the distance
		txt = f'Distance: {distance:.1f}'
		distance_canvas = self._draw_text(text=txt, font_name=self.primary_font, font_point_size=40, text_color=(0,0,0), rect=True, 
								 outline_color=(3, 161, 252), fill_color=(255,255,255))
		if self.WIDTH == 240:
			coords = (self.WIDTH // 2 - (speed_canvas.width // 2), 0)
		else:
			# Add another 1/8 of a screen gap for between the bottom of speed and top of height.
			coords = (self.WIDTH // 8, 2 * self.HEIGHT // 8 + speed_canvas.height)
		img.paste(distance_canvas, coords, distance_canvas)

		# Display Final Screen
		self._display_canvas(img)

	'''
	 ====================== Input & Menu Code ========================
	'''
	def _event_detect(self):
		"""
		Called to detect input events from buttons, encoder, touch, etc.
		This function should be overriden by the inheriting class. 
		"""
		pass

	def _menu_display(self, action):
		''' Process user input from th display
		    action: Will be UP, DOWN, or ENTER '''
		
		# If menu is not currently being displayed, check mode and draw menu
		print('action=',action)
		print("  menu=", self.menu['current'])

		# When the display has timed out it will be set to 'none'.  Wake it up based
		# not the current operating mode
		# Note the menu has the following modes: none, inactive, and active
		if self.menu['current']['mode'] == 'none':
			control = read_control()
			# If in an inactive mode
			if control['mode'] in ['Stop', 'Error']:
				self.menu['current']['mode'] = 'inactive'
			else:
				self.menu['current']['mode'] = 'active'

			self.menu['current']['option'] = 0  # Set the menu option to the very first item in the list

		# If selecting either active menu items or inactive menu items, take action based on what the button press was
		else:
			if action == 'DOWN':
				self.menu['current']['option'] -= 1
				if self.menu['current']['option'] < 0:  # Check to make sure we haven't gone past 0
					self.menu['current']['option'] = len(self.menu[self.menu['current']['mode']]) - 1
				temp_value = self.menu['current']['option']
				temp_mode = self.menu['current']['mode']
				index = 0
				selected = 'undefined'
				for item in self.menu[temp_mode]:
					if index == temp_value:
						selected = item
						break
					index += 1
			elif action == 'UP':
				self.menu['current']['option'] += 1
				# Check to make sure we haven't gone past the end of the menu
				if self.menu['current']['option'] == len(self.menu[self.menu['current']['mode']]):
					self.menu['current']['option'] = 0
				temp_value = self.menu['current']['option']
				temp_mode = self.menu['current']['mode']
				index = 0
				selected = 'undefined'
				for item in self.menu[temp_mode]:
					if index == temp_value:
						selected = item
						break
					index += 1
			elif action == 'ENTER':
				index = 0
				selected = 'undefined'
				for item in self.menu[self.menu['current']['mode']]:
					if (index == self.menu['current']['option']):
						selected = item
						break
					index += 1
				# Inactive Mode Items
				if selected == 'Start':
					self.display_active = True
					self.menu['current']['mode'] = 'none'
					#self.menu['current']['mode'] = 'riding'
					self.menu['current']['option'] = 0
					self.menu_active = False
					self.menu_time = 0
					control = read_control()
					control['updated'] = True
					control['mode'] = 'Riding'
					write_control(control, origin='display')
					control = read_control()

				elif selected == 'Stop':
					self.menu['current']['mode'] = 'none'
					self.menu['current']['option'] = 0
					self.menu_active = False
					self.menu_time = 0
					self.clear_display()
					control = read_control()
					control['updated'] = True
					control['mode'] = 'Stop'
					write_control(control, origin='display')
				elif selected == 'Power':
					self.menu['current']['mode'] = 'power_menu'
					self.menu['current']['option'] = 0
				elif 'Power_' in selected:
					control = read_control()
					if 'Off' in selected:
						#TODO - splash a shutdown screen!

						os.system('sudo shutdown -h now &')
					elif 'Restart' in selected:
						os.system('sudo reboot &')
				
				# Master Menu Back Function
				elif 'Menu_Back' in selected:
					self.menu['current']['mode'] = 'inactive'
					self.menu['current']['option'] = 0
				
				# Active Mode
				elif selected == 'Shutdown':
					self.display_active = True
					self.menu['current']['mode'] = 'none'
					self.menu['current']['option'] = 0
					self.menu_active = False
					self.menu_time = 0
					control = read_control()
					control['updated'] = True
					control['mode'] = 'Shutdown'
					write_control(control, origin='display')
				elif selected == 'Network':
					self.display_network()
				else:
					print(f'menu selection {selected} is not supported!')
					#TODO log this instead

		# Create canvas
		img = Image.new('RGBA', (self.WIDTH, self.HEIGHT), color=(0, 0, 0))
		# Set the position & paste background image onto canvas 
		position = (0, 0)
		img.paste(self.background, position)
		# Create drawing object
		draw = ImageDraw.Draw(img)

		if self.menu['current']['mode'] == 'riding':
			
			# ...
			font_point_size = 80 if self.WIDTH == 240 else 120 
			label_canvas = self._draw_text(str(self.menu['current']['option']), self.primary_font, font_point_size, (255,255,255))
			label_origin = (int(self.WIDTH // 2 - label_canvas.width // 2), int(self.HEIGHT // 3 - label_canvas.height // 2)) if self.WIDTH == 240 else (int(self.WIDTH // 2 - label_canvas.width // 2 - 20), int(self.HEIGHT // 2.5 - label_canvas.height // 2))
			img.paste(label_canvas, label_origin, label_canvas)

			# Current Mode (Bottom Center)
			font_point_size = 40
			text = "Riding"
			label_canvas = self._draw_text(text, self.primary_font, font_point_size, (0,0,0))

			# Draw White Rectangle
			draw.rectangle([(0, (self.HEIGHT // 8) * 6), (self.WIDTH, self.HEIGHT)], fill=(255, 255, 255))
			# Draw White Line/Rectangle
			draw.rectangle([(0, (self.HEIGHT // 8) * 6), (self.WIDTH, ((self.HEIGHT // 8) * 6) + 2)],
						   fill=(130, 130, 130))
			# Draw Text
			label_origin = (int(self.WIDTH // 2 - label_canvas.width // 2), int((self.HEIGHT // 8) * 6.35))
			img.paste(label_canvas, label_origin, label_canvas)

		elif self.menu['current']['mode'] != 'none':
			# Menu Option (Large Top Center)
			index = 0
			selected = 'undefined'
			for item in self.menu[self.menu['current']['mode']]:
				if index == self.menu['current']['option']:
					selected = item
					break
				index += 1
			font_point_size = 80 if self.WIDTH == 240 else 120 
			icon_color = self.menu[self.menu['current']['mode']][selected].get('iconcolor', (255,255,255))  # Get color from menu item, default to white if not defined
			text = self.menu[self.menu['current']['mode']][selected]['icon']
			label_canvas = self._draw_text(text, 'static/font/FA-Free-Solid.otf', font_point_size, icon_color)
			label_origin = (int(self.WIDTH // 2 - label_canvas.width // 2), int(self.HEIGHT // 2.5 - label_canvas.height // 2))
			img.paste(label_canvas, label_origin, label_canvas)

			# Current Mode (Bottom Center)
			# Draw White Rectangle
			draw.rectangle([(0, (self.HEIGHT // 8) * 6), (self.WIDTH, self.HEIGHT)], fill=(255, 255, 255))
			# Draw Gray Line/Rectangle
			draw.rectangle([(0, (self.HEIGHT // 8) * 6), (self.WIDTH, ((self.HEIGHT // 8) * 6) + 2)],
						   fill=(130, 130, 130))
			# Draw Text
			font_point_size = 40
			text = self.menu[self.menu['current']['mode']][selected]['displaytext']
			label_canvas = self._draw_text(text, self.primary_font, font_point_size, (0,0,0))
			label_origin = (int(self.WIDTH // 2 - label_canvas.width // 2), int((self.HEIGHT // 8) * 6.35))
			img.paste(label_canvas, label_origin, label_canvas)

		self._display_canvas(img)

	'''
	================ Externally Available Methods ================
	'''

	def display_status(self, current):
		"""
		- Updates the current data for the display loop, if in a work mode
		"""
		self.display_active = True
		self.in_data = current 
	
	def display_splash(self):
		"""
		- Calls Splash Screen
		"""
		self.display_command = 'splash'

	def clear_display(self):
		"""
		- Clear display and turn off backlight
		"""
		self.display_command = 'clear'

	def display_text(self, text):
		"""
		- Display some text
		"""
		self.display_command = 'text'
		self.display_data = text

	def display_network(self):
		"""
		- Display Network IP QR Code
		"""
		self.display_command = 'network'
