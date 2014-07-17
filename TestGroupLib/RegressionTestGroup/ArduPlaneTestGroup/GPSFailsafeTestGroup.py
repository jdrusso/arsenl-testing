import pexpect, os, sys
from pymavlink import mavutil
import util, arduplane
from common import *
import testutils

class GPSFailsafeTests():

    def test_gps_failsafe(self):
        assert testutils.check_GPS(self)
