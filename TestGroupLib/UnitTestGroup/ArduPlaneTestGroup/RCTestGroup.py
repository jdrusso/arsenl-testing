import pexpect, os, sys, re
from pymavlink import mavutil
import nose
import util, arduplane
from common import *

class RCTest():

	def test_rc_negative_value(self):

		for channel in range(1,9):

			yield self.check_send_rc_channel, channel, -2

	def test_rc_nonint_value(self):

		for channel in range(1,9):

			yield self.check_send_rc_channel, channel, 1500.5

	def test_rc_valid_value(self):
		
		valid_values = [1000, 1500, 2000]

		for channel in range(1,9):

			for value in valid_values:

				wait_seconds(self.DELAY)

				yield self.check_send_rc_channel, channel, value

	def check_send_rc_channel(self, channel, value):

		#RCTests require a much longer delay.
		#TODO: WHY?
		#self.DELAY = self.DELAY * 2

		#Get original value
		wait_seconds(self.DELAY)
		self.mavproxy.send('status\n')
		wait_seconds(self.DELAY)
		self.mavproxy.expect('chan%s_raw : (\d+)' % channel, timeout=self.TIMEOUT)
		originalValue = re.match('chan%s_raw : (\d+)' % channel, self.mavproxy.after).group(1)

		#Send the test value
		wait_seconds(self.DELAY)
		self.mavproxy.send('rc %s %s\n' % (channel, value))

		#Verify it was received
		wait_seconds(self.DELAY)
		self.mavproxy.send('status\n')
		wait_seconds(self.DELAY)
		if value in range(-1,65535):
			assert {0:True, 1:False}[self.mavproxy.expect('chan%s_raw : %d'\
			 % (str(channel), value), timeout=self.TIMEOUT)]
		#If it was an invalid value, verify it was not accepted
		else:
			try:
				assert {0:False, 1:True}[self.mavproxy.expect('chan%s_raw : %4.1f'\
				 % (str(channel), value), timeout=2)]
			except pexpect.TIMEOUT:
				pass

		#Reset the original value
		wait_seconds(self.DELAY)
		self.mavproxy.send('rc %s %s\n' % (channel, originalValue))
		wait_seconds(self.DELAY)

		#self.DELAY = self.DELAY / 2