import pexpect, os, sys
from pymavlink import mavutil
import util, arduplane
from common import *

class ModeTest():

    modes = ['AUTO', 'RTL', 'FBWA', 'FBWB', 'CIRCLE', 'MANUAL']

    def check_enter_mode(self, mode):
        #Attempt to enter a mode
        self.mavproxy.send('mode %s\n' % mode)
        wait_seconds(1.5)
        #wait_mode(self.mav, mode, timeout=self.TIMEOUT)

        if mode == 'INITIALISING':
            assert not (self.mav.flightmode == mode)
        else:
            assert {0: True, 1: False}[self.mavproxy.expect('%s>' % mode, self.TIMEOUT)]

    def test_enter_modes(self):

        for mode in ModeTest.modes:

            yield self.check_enter_mode, mode