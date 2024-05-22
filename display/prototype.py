#!/usr/bin/env python3

# *****************************************
# PiFire Display Prototype Interface Library
# *****************************************
#
# Description: This library simulates a display.
#
# *****************************************

# *****************************************
# Imported Libraries
# *****************************************

import threading
import time
from pynput import keyboard
from display.base_240x320 import DisplayBase

import cv2
import numpy as np


class Display(DisplayBase):

	def __init__(self, dev_pins):
		super().__init__(dev_pins)

	def __del__(self):
		cv2.destroyAllWindows()

	def _init_display_device(self):

		# Setup & Start Display Loop Thread 
		display_thread = threading.Thread(target=self._display_loop)
		display_thread.start()

		print('started display thread')

	def _init_input(self):
		self.input_enabled = True
		self.input_event = None

		# There is likely better keys than this, but it seems to work!
		key_listener_thread = keyboard.GlobalHotKeys({
			'<alt>+<ctrl>+q': self._do_up,
			'<alt>+<ctrl>+w': self._do_down,
			'<alt>+<ctrl>+e': self._do_enter})
		key_listener_thread.start()

		self._init_menu()
		print('initialized menu')

	'''
	============== Input Callbacks ============= 
	'''

	def _do_up(self):
		self.input_event = 'UP'

	def _do_down(self):
		self.input_event = 'DOWN'

	def _do_enter(self):
		self.input_event = 'ENTER'

	'''
	============== Graphics / Display / Draw Methods ============= 
	'''

	def _display_clear(self):
		blank_image = np.zeros((self.HEIGHT, self.WIDTH, 3), np.uint8)
		cv2.imshow('PiCycle', blank_image)
		cv2.waitKey(delay=1)

	def _display_canvas(self, canvas):
		np_image = np.array(canvas)
		opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
		cv2.imshow('PiCycle', opencv_image)
		cv2.waitKey(delay=1)

	'''
	====================== Input & Menu Code ========================
	'''

	def _event_detect(self):
		"""
		Called to detect input events from buttons.
		"""
		command = self.input_event  # Save to variable to prevent spurious changes 
		self.input_event = None

		if command:
			self.display_timeout = None  # If something is being displayed i.e. text, network, splash then override this

			if command not in ['UP', 'DOWN', 'ENTER']:
				return

			self.display_command = None
			self.display_data = None
			self.input_event = None
			self.menu_active = True
			self.menu_time = time.time()
			self._menu_display(command)
			self.input_counter = 0
