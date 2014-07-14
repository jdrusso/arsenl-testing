import pexpect, os, sys
from pymavlink import mavutil
import util, arduplane
from common import *

class GPSFailsafeTests():

    def test_gps_failsafe(self):
        assert self.check_GPS()