import pexpect, os, sys
from pymavlink import mavutil
import util, arduplane
from common import *

class CalibrationTest():

	def test_calibrate_barometer(self):

		self.mavproxy.send('calpress\n')

		assert {0:True, 1:False}[self.mavproxy.expect('barometer calibration complete',timeout=self.TIMEOUT)]

