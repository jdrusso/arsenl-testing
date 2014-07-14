import pexpect, os, sys, re
from pymavlink import mavutil
from nose.tools import *
import subprocess
import util, arduplane
from common import *

#TODO: Find a way to test 'wp move'. Uses map clicks
class WaypointTest():

	#Generic setup method for a waypoint test fixture
	def waypoint_setup(self):

		print("\n" + "*"*15)
		print("Beginning setup")
		print("*"*15)

		self.mavproxy.send('wp list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('wp clear\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('wp list\n')
		wait_seconds(self.DELAY)
		assert (self.mav.recv_match(type='MISSION_REQUEST', blocking=True, \
			condition='MISSION_COUNT.count == 0', timeout=self.TIMEOUT) != None)

	def waypoint_teardown(self):

		print("\n" + "*"*15)
		print("Beginning teardown")
		print("*"*15)

		# self.mavproxy.send('wp list\n')
		# self.mavproxy.send('wp clear\n')
		# self.mavproxy.send('wp list\n')
		# assert (self.mav.recv_match(type='MISSION_REQUEST', blocking=True, \
		# 	condition='MISSION_COUNT.count == 0', timeout=self.TIMEOUT) != None)
		pass

	def test_waypoint_list(self):
		#initialize list of waypoints

		self.mavproxy.send('wp list\n')

		assert {0: True, 1:False}[self.mavproxy.expect('Requesting \d waypoints', self.TIMEOUT)]

	def test_waypoints_load(self):
		#attempt to load a mission

		self.mavproxy.send('wp load %snewtie.txt\n' % self.resource_path)

		wait_seconds(self.DELAY)

		self.mavproxy.send('wp list\n')

		#TODO: Pick one of these to use. They all test the same thing.
		assert {0:True, 1:False}[self.mavproxy.expect('Loaded 8 waypoints')]
		assert (self.mav.recv_match(type='MISSION_COUNT', blocking=True, \
    		condition='MISSION_COUNT.count == 8', timeout=self.TIMEOUT) != None)
		assert (self.mav.field('MISSION_COUNT', 'count') == 8)

	# def test_waypoints_clear(self):
	# 	#attempt to clear the mission

	# 	wait_seconds(self.DELAY)

	# 	self.mavproxy.send('wp clear\n')

	# 	wait_seconds(self.DELAY)
	# 	self.mavproxy.send('wp list\n')
	# 	wait_seconds(self.DELAY)

	# 	self.mavproxy.send('status\n')

	# 	#re.compile("MISSION_COUNT {(.*)count : (.*)}\n").search(string).group(2)
	# 	#self.mavproxy.expect("MISSION_COUNT {(.*)count : 0}", timeout=self.TIMEOUT)
	# 	self.mavproxy.expect("re-requesting WP 0", timeout=self.TIMEOUT)

	# 	#self.mav.recv_match(type='MISSION_COUNT', blocking=True, \
 #    	#	condition='MISSION_COUNT.count == 0', timeout=self.TIMEOUT)

	# 	#assert (self.mav.field('MISSION_COUNT', 'count') == 0)

	# 	wait_seconds(self.DELAY)

	@with_setup(waypoint_setup, waypoint_teardown)
	def test_waypoints_save(self):
		#attempt to load a waypoint list, save it, and reload it

		print("\n" + "*"*15)
		print("Beginning save waypoint test")
		print("*"*15)

		self.mavproxy.send('wp clear\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('wp list\n')
		wait_seconds(self.DELAY)

		self.mavproxy.send('wp load %snewtie.txt\n' % self.resource_path)

		#This needs to be here so the waypoints successfully load
		wait_seconds(self.DELAY)
		assert {0: True, 1: False}[self.mavproxy.expect('Loaded 8 waypoints', timeout=60)], "Waypoint load failed"

		self.mavproxy.send('wp list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('wp save temp.txt\n')
		wait_seconds(self.DELAY)

		assert {0:True, 1:False}[self.mavproxy.expect('Saved 8 waypoints to temp.txt', timeout=self.TIMEOUT)], "Temp file write failed"

		wait_seconds(self.DELAY)
		self.mavproxy.send('wp clear\n')
		wait_seconds(self.DELAY)

		self.mavproxy.send('wp list\n')
		wait_seconds(self.DELAY)

		#Ensure waypoint list was successfully cleared
		assert {0:True, 1:False}[self.mavproxy.expect('Saved [0-7] waypoints', timeout=self.TIMEOUT)], "Clearing WP list failed"

		self.mavproxy.send('wp load temp.txt\n')
		wait_seconds(self.DELAY)

		self.mavproxy.send('wp list\n')

		#Ensure it was successfully reloaded
		assert {0:True, 1:False}[self.mavproxy.expect('Loaded 8 waypoints from temp.txt', timeout=self.TIMEOUT)], "Reloading temp file failed"

		try:
			os.remove('temp.txt')
		except OSError:
			print("Couldn't delete temp.txt.")
		pass

	@with_setup(waypoint_setup, waypoint_teardown)
	def test_waypoints_remove(self):
		#attempt to remove one waypoint from a set

		print("\n" + "*"*15)
		print("Beginning remove waypoint test")
		print("*"*15)

		self.mavproxy.send('wp clear\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('wp list\n')
		wait_seconds(self.DELAY)

		self.mavproxy.send('wp load %snewtie.txt\n' % self.resource_path)

		#This needs to be here so the waypoints successfully load
		wait_seconds(self.DELAY)

		assert {0: True, 1: False}[self.mavproxy.expect('Loaded 8 waypoints', timeout=self.TIMEOUT)]

		self.mavproxy.send('wp list\n')

		assert {0: True, 1: False}[self.mavproxy.expect('Saved 8 waypoints', timeout=self.TIMEOUT)]

		self.mavproxy.send('wp remove 7\n')

		assert {0: True, 1: False}[(self.mavproxy.expect('Removed WP 7', timeout=2))]
		wait_seconds(self.DELAY)

		self.mavproxy.send('wp list\n')
		wait_seconds(self.DELAY)
		self.mavproxy.send('status\n')
		assert {0: True, 1: True, 2:False}[(self.mavproxy.expect(['Saved 7 waypoints', 
			'seq : 7'], timeout=self.TIMEOUT))]

	def test_waypoints_set(self):
		#Attempt to add a waypoint to the list.

		self.mavproxy.send('wp load %snewtie.txt\n' % self.resource_path)
		wait_seconds(self.DELAY)
		self.mavproxy.send('wp set 2\n')
		wait_seconds(self.DELAY)
		assert {0:True, 1:False}[self.mavproxy.expect('waypoint 2', timeout=self.TIMEOUT)]

	def test_waypoints_move(self):
		#Attempts to move a waypoint.

		self.mavproxy.send('wp load %snewtie.txt\n' % self.resource_path)
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
		#This position is arbitrary
		mouse_click_x = x_offset + (width//3)
		mouse_click_y = y_offset + (height//3)

		#Bring the Map window to the front && Click
		subprocess.call('xdotool windowactivate %d && xdotool mousemove %d %d click 1'\
		 	% (window_id, mouse_click_x, mouse_click_y), shell=True)

		wait_seconds(self.DELAY)
		self.mavproxy.send('wp move 2\n')
		assert {0:True, 1:False}[self.mavproxy.expect('Moved WP 2', timeout=self.TIMEOUT)]
		wait_seconds(self.DELAY)
		self.mavproxy.send('wp list\n')