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

		print('Special keys on erics keyboard, forward, back, and *')

		#keywords = {'name': 'keyreader'}
		key_listener_thread = keyboard.Listener(on_press=self._keypress)
		key_listener_thread.start()

		self._init_menu()
		print('initialized menu')

	'''
	============== Input Callbacks ============= 
	'''
	def _keypress(self, key:keyboard.Key):

		try:
			if key.vk == 171:
				self.input_event='ENTER'
			elif key.vk == 167:
				self.input_event = 'UP'
			elif key.vk == 166:
				self.input_event = 'DOWN'
		except:
			# Some keys (like enter) don't supply the above with a .vk value, so
			# we will just ignore them
			pass

	'''
	============== Graphics / Display / Draw Methods ============= 
	'''

	def _display_clear(self):
		blank_image = np.zeros((self.HEIGHT,self.WIDTH,3), np.uint8)
		cv2.imshow('PiCycle', blank_image)
		cv2.waitKey(delay=1)

	def _display_canvas(self, canvas):
		npImage = np.array(canvas)
		opencvImage = cv2.cvtColor(npImage, cv2.COLOR_RGB2BGR)
		cv2.imshow('PiCycle', opencvImage)
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
			self.input_event=None
			self.menu_active = True
			self.menu_time = time.time()
			self._menu_display(command)
			self.input_counter = 0