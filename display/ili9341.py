#!/usr/bin/env python3
'''
*****************************************
PiCycle Display Interface Library
*****************************************

 Description: 
   This library supports using 
 the ILI9341 display with 240Hx320W resolution.
 This module utilizes Luma.LCD to interface 
 this display. 

*****************************************
'''

'''
 Imported Libraries
'''
import threading
import time
from luma.core.interface.serial import spi
from luma.lcd.device import ili9341
from display.base_240x320 import DisplayBase
import RPi.GPIO as gpio

'''
Display class definition
'''
class Display(DisplayBase):

	def __init__(self, dev_pins, config):
		super().__init__(dev_pins, config)

	def _init_display_device(self):
		# Init Device
		dc_pin = self.dev_pins['display']['dc']
		led_pin = self.dev_pins['display']['led']
		rst_pin = self.dev_pins['display']['rst']

#		self.serial = spi(port=0, device=0, gpio_DC=dc_pin, gpio_RST=rst_pin, bus_speed_hz=32000000,
#						  reset_hold_time=0.2, reset_release_time=0.2)
		self.serial = spi(port=0, device=0, gpio_DC=dc_pin, gpio_RST=rst_pin)

#		self.device = ili9341(self.serial, active_low=False, width=320, height=240, gpio_LIGHT=led_pin,
#							  rotate=self.rotation)
		self.device = ili9341(self.serial, active_low=False, gpio_LIGHT=led_pin, rotate=self.rotation)

		# Setup & Start Display Loop Thread 
		display_thread = threading.Thread(target=self._display_loop)
		display_thread.start()

		print('started display thread')


	def _init_input(self):
		self.input_enabled = True
		
		# Init gpio for button input, setup callbacks
		self.chan_a_pin = self.dev_pins['rotary_encoder']['chan_a']
		self.chan_b_pin = self.dev_pins['rotary_encoder']['chan_b']
		button_pin = self.dev_pins['rotary_encoder']['push']

		gpio.setmode(gpio.BCM)
		gpio.setup(self.chan_a_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
		gpio.setup(self.chan_b_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
		gpio.setup(button_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

		gpio.add_event_detect(self.chan_a_pin, gpio.BOTH, callback=self._encoder_callback)
		gpio.add_event_detect(self.chan_b_pin, gpio.BOTH, callback=self._encoder_callback)
		gpio.add_event_detect(button_pin, gpio.RISING, callback=self._enter_callback)

		self.input_event = None
		self.input_counter = 0

		self.prev_a_state = gpio.input(self.chan_a_pin)
		self.prev_b_state = gpio.input(self.chan_b_pin)

		self._init_menu()

	def __del__(self):
		print('display delete called')
		gpio.cleanup()

	'''
	============== Input Callbacks ============= 
	'''
	def _enter_callback(self, channel):
		# gets called when the rotary pushbutton is pressed
		self.input_event='ENTER'

	def _encoder_callback(self, channel):
		# gets called when the rotary is turned.  The rotary has two channels.  We can determine direction
		# based on the order they change.  Each detent of the rotary generates the pattern as follows (and there
		# may be repeats:  0 1 or 1 0, 0 0, 1,1.  The first 0 1 or 1 0 tells us the direction
  
		# Read the current state of the channels
		a_state = gpio.input(self.chan_a_pin)
		b_state = gpio.input(self.chan_b_pin)

		# The transision we are looking for always follows a 1 1 state
		if self.prev_a_state == 1 and self.prev_b_state == 1:
			if a_state == 1 and b_state == 0:
				self.input_event = 'UP'
			elif b_state == 1 and a_state == 0:
				self.input_event = 'DOWN'

		# Save current states for next time
		self.prev_a_state = a_state
		self.prev_b_state = b_state

	'''
	============== Graphics / Display / Draw Methods ============= 
	'''

	def _display_clear(self):
		self.device.clear()
		self.device.backlight(False)
		self.device.hide()

	def _display_canvas(self, canvas):
		# Display Image
		self.device.backlight(True)
		self.device.show()
		self.device.display(canvas.convert(mode="RGB"))

	'''
	 ====================== Input & Menu Code ========================
	'''
	def _event_detect(self):
		"""
		Called to detect input events from buttons.
		"""

		#print(f'Received command {self.input_event}')

		command = self.input_event  # Save to variable to prevent spurious changes 
		if command:
			self.display_timeout = None  # If something is being displayed i.e. text, network, splash then override this

			if command not in ['UP', 'DOWN', 'ENTER']:
				return

			self.display_command = None
			self.display_data = None
			self.input_event=None
			self.menu_active = True
			self.menu_time = time.time()
			self._menu_display(command)
			self.input_counter = 0
