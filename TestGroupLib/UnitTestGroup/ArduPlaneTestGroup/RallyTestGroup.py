import pexpect, os, sys, re
from pymavlink import mavutil
from nose.tools import *
import subprocess
import util, arduplane
from common import *

class RallyTest():

	#Generic setup method for a rally test fixture
	def rally_setup(self):

		print("\n" + "*"*15)
		print("Beginning setup")
		print("*"*15)

		self.mavproxy.send('rally list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally clear\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally list\n')
		wait_seconds(self.DELAY)


	def rally_teardown(self):
		pass

	def test_rally_list(self):
		#initialize list of rallys

		self.mavproxy.send('rally list\n')
		self.mavproxy.expect(['Failed to fetch rally point 0', 
			'lat=.* lng=.* alt=.* break_alt=.* land_dir=.*', 'No rally points'], timeout=self.TIMEOUT)

	def test_rally_load(self):
		#attempt to load a rally point

		self.mavproxy.send('rally load %srally_test\n' % self.resource_path)
		wait_seconds(self.DELAY)
		assert {0:True, 1:False}[self.mavproxy.expect('Loaded \d* rally points from', timeout=self.TIMEOUT)]
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally list\n')

	def test_rally_clear(self):
		#attempt to clear the rally points

		#Load some points
		self.mavproxy.send('rally load %srally_test\n' % self.resource_path)
		wait_seconds(self.DELAY)
		assert {0:True, 1:False}[self.mavproxy.expect('Loaded \d* rally points from', timeout=self.TIMEOUT)]
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally list\n')
		wait_seconds(self.DELAY)
		#Make sure they successfully loaded. This should time out
		try:
			self.mavproxy.expect('No rally points', timeout=3)
		except Exception:
			assert True
		wait_seconds(self.DELAY)
		#Now try to clear them
		self.mavproxy.send('rally clear\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally list\n')
		wait_seconds(self.DELAY)

		assert {0:True, 1:False}[self.mavproxy.expect('No rally points', timeout=self.TIMEOUT)]

	def test_rally_save(self):
		#attempts to save rally points to a file

		self.mavproxy.send('rally list\n')
		#Load a point file
		self.mavproxy.send('rally load %srally_test\n' % self.resource_path)
		wait_seconds(self.DELAY)
		assert {0:True, 1:False}[self.mavproxy.expect('Loaded \d* rally points from', timeout=self.TIMEOUT)]
		try:
			originalNumPoints = re.match("Loaded (\d*) rally points from", self.mavproxy.after).group(1)
		except AttributeError:
			print self.mavproxy.after

		wait_seconds(self.DELAY)
		self.mavproxy.send('rally list\n')

		#Save it as temp_rally
		self.mavproxy.send('rally save temp_rally\n')
		wait_seconds(self.DELAY)
		assert{0:True,1:False}[self.mavproxy.expect('Saved rally file temp_rally', timeout=self.TIMEOUT)]
		wait_seconds(self.DELAY)

		#Clear your current points
		self.mavproxy.send('rally clear\n')
		self.mavproxy.send('rally list\n')
		wait_seconds(self.DELAY)
		assert{0:True,1:False}[self.mavproxy.expect('No rally points', timeout=self.TIMEOUT)]

		#Now reload to see if it saved properly
		self.mavproxy.send('rally load temp_rally\n')
		wait_seconds(self.DELAY)
		assert {0:True, 1:False}[self.mavproxy.expect('Loaded \d* rally points from', timeout=self.TIMEOUT)]
		try:
			numPoints = re.match("Loaded (\d*) rally points from", self.mavproxy.after).group(1)
		except AttributeError:
			print self.mavproxy.after
		wait_seconds(self.DELAY)

		assert numPoints == originalNumPoints

	def test_rally_remove(self):
		#attempts to remove a rally point

		#Load rally_test with 2 rally points in it
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally load %srally_test\n' % self.resource_path)
		self.mavproxy.expect('Loaded 2 rally points', timeout=self.TIMEOUT)
		wait_seconds(self.DELAY)

		#Remove the second rally point
		self.mavproxy.send('rally remove 2\n')
		wait_seconds(self.DELAY)

		#Verify it was removed by listing, and making sure there's only 1 entry
		self.mavproxy.send('rally list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('status\n')
		wait_seconds(self.DELAY)
		assert {0:True, 1:False}[self.mavproxy.expect('RALLY_POINT {.*count : 1.*}', timeout=self.TIMEOUT)]


	def test_rally_move(self):
		#attempts to move a rally point

		self.mavproxy.send('rally load %srally_test\n' % self.resource_path)
		wait_seconds(self.DELAY)

		window_id = int(subprocess.check_output('xdotool search --name Map', shell=True))

		regex = re.compile('X=(\d*)\s*Y=(\d*)\s*WIDTH=(\d*)\s*HEIGHT=(\d*)\s*')

		results = regex.search(subprocess.check_output('xdotool getwindowgeometry --shell %d'\
			% window_id, shell=True)).groups()

		x_offset = int(results[0])
		y_offset = int(results[1])
		width    = int(results[2])
		height   = int(results[3])

		#Set the click position to the upper right third of the map
		#This position is somewhat arbitrary
		mouse_click_x = x_offset + (width//3)*2
		mouse_click_y = y_offset + (height//3)*2

		#Bring the Map window to the front and click
		subprocess.call('xdotool windowactivate %d && xdotool mousemove %d %d click 1'\
		 	% (window_id, mouse_click_x, mouse_click_y), shell=True)

		wait_seconds(self.DELAY)
		self.mavproxy.send('rally move 2\n')
		assert {0:True, 1:False}[self.mavproxy.expect('Moved rally point', timeout=self.TIMEOUT)]
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally list\n')


		pass

	def test_rally_add(self):
		#attempts to add a rally point

		self.mavproxy.send('rally list\n')

		window_id = int(subprocess.check_output('xdotool search --name Map', shell=True))

		regex = re.compile('X=(\d*)\s*Y=(\d*)\s*WIDTH=(\d*)\s*HEIGHT=(\d*)\s*')

		results = regex.search(subprocess.check_output('xdotool getwindowgeometry --shell %d'\
			% window_id, shell=True)).groups()

		x_offset = int(results[0])
		y_offset = int(results[1])
		width    = int(results[2])
		height   = int(results[3])

		#Set the click position to the upper right third of the map
		#This position is somewhat arbitrary
		mouse_click_x = x_offset + (width//3)*2
		mouse_click_y = y_offset + (height//3)

		#Bring the Map window to the front
		assert subprocess.call('xdotool windowactivate %d' % window_id, shell=True) == 0
		#Click
		subprocess.call('xdotool windowactivate %d && xdotool mousemove %d %d click 1'\
		 	% (window_id, mouse_click_x, mouse_click_y), shell=True)

		wait_seconds(self.DELAY)
		self.mavproxy.send('rally add\n')
		assert {0:True, 1:False}[self.mavproxy.expect('Added Rally point', timeout=self.TIMEOUT)]
		wait_seconds(self.DELAY)
		self.mavproxy.send('rally list\n')