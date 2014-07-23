import pexpect, os, sys, re
from pymavlink import mavutil
import subprocess
import util, arduplane
from common import *
from nose.plugins.attrib import attr

#TODO: Find a way to detect whether or not the plane is breaching
class FenceTest():

	#TODO: Does fence list even work?
	def test_fence_list(self):
		#initialize list of waypoints

		self.mavproxy.send('fence load %stestFence\n' % self.resource_path)
		assert {0: True, 1: False}[self.mavproxy.expect('Loaded 6 geo-fence points'\
			, self.TIMEOUT)]
		wait_seconds(self.DELAY)

		self.mavproxy.send('fence list\n')

		self.mavproxy.send('fence clear\n')
		self.mavproxy.send('fence list\n')

		assert {0: True, 1: False}[self.mavproxy.expect('Saved fence', self.TIMEOUT)]

	def test_fence_clear(self):
		#clear the fence

		self.mavproxy.send('fence clear\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence list\n')

		assert {0: True, 1: False}[self.mavproxy.expect('No geo-fence points', self.TIMEOUT)]

		self.mavproxy.send('fence clear\n')
		self.mavproxy.send('fence list\n')

	def test_fence_load(self):
		#attempt to load a fence file

		self.mavproxy.send('fence load %stestFence\n' % self.resource_path)

		assert {0: True, 1: False}[self.mavproxy.expect('Loaded 6 geo-fence points'\
			, self.TIMEOUT)]

		self.mavproxy.send('fence clear\n')
		self.mavproxy.send('fence list\n')

	def test_fence_save(self):
		#Attempts to save the currently loaded geofence
		self.mavproxy.send('fence load %stestFence\n' % self.resource_path)
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence save temp_fence\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence clear\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence load temp_fence\n')
		assert {0:True, 1:False}[self.mavproxy.expect('Loaded \d geo-fence points', timeout=self.TIMEOUT)]
		pass

	@attr('gui')
	def test_fence_move(self):
		#Attempts to move a geofence point

		self.mavproxy.send('fence list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence load %stestFence\n' % self.resource_path)
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence list\n')
		wait_seconds(self.DELAY)
		window_id = int(subprocess.check_output('xdotool search --name "Map"', shell=True))
		regex = re.compile('X=(\d*)\s*Y=(\d*)\s*WIDTH=(\d*)\s*HEIGHT=(\d*)\s*')

		results = regex.search(subprocess.check_output('xdotool getwindowgeometry --shell %d'\
			% window_id, shell=True)).groups()
		x_offset = int(results[0])
		y_offset = int(results[1])
		width    = int(results[2])
		height   = int(results[3])

		#Set the click position to the upper right third of the map
		#This position is arbitrary
		mouse_click_x = x_offset + (width//3)
		mouse_click_y = y_offset + (height//3)
		
		#Bring the Map window to the front && Click
		subprocess.call('xdotool windowactivate %d && xdotool mousemove %d %d click 1'\
		 	% (window_id, mouse_click_x, mouse_click_y), shell=True)

		wait_seconds(self.DELAY)
		self.mavproxy.send('fence list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence move 2\n')

		assert {0:True, 1:False}[self.mavproxy.expect('Moved fence point 2', timeout=self.TIMEOUT)]

		wait_seconds(self.DELAY)

		self.mavproxy.send('fence list\n')

	def test_fence_remove(self):
		#Attempts to remove a geofence point

		self.mavproxy.send('fence load %stestFence\n' % self.resource_path)
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence disable\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence remove 5\n')
		wait_seconds(self.DELAY)
		self.mavproxy.expect('fence removed', timeout=self.TIMEOUT), 'Fence point could not be removed'
		
	def test_fence_enable(self):
		#Attempts to enable the geofence

		wait_seconds(self.DELAY)
		self.mavproxy.send('mode FBWA\n')
		wait_seconds(self.DELAY)

		self.mavproxy.send('fence load %stestFence\n' % self.resource_path)
		assert {0: True, 1: False}[self.mavproxy.expect('Loaded 6 geo-fence points'\
			, self.TIMEOUT)]
		wait_seconds(self.DELAY)

		self.mavproxy.send('fence disable\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence enable\n')
		wait_seconds(self.DELAY)
		assert {0:True, 1:True, 2:False}[self.mavproxy.expect('fence enabled', timeout=self.TIMEOUT)], \
		'Fence could not be enabled.'

		self.mavproxy.send('fence clear\n')
		self.mavproxy.send('fence list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('mode MANUAL\n')
		wait_seconds(self.DELAY)


	def test_fence_disable(self):
		#Attempts to disable the geofence

		wait_seconds(self.DELAY)
		self.mavproxy.send('mode FBWA\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence load %stestFence\n' % self.resource_path)
		assert {0: True, 1: False}[self.mavproxy.expect('Loaded 6 geo-fence points'\
			, self.TIMEOUT)]
		wait_seconds(self.DELAY)

		self.mavproxy.send('fence enable\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('fence disable\n')
		wait_seconds(self.DELAY)
		assert {0:True, 1:True, 2:False}[self.mavproxy.expect('fence disabled', timeout=self.TIMEOUT)], \
		'Fence could not be disabled.'

		self.mavproxy.send('fence clear\n')
		self.mavproxy.send('fence list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('mode MANUAL\n')
		wait_seconds(self.DELAY)