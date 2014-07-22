import pexpect, os, sys
from pymavlink import mavutil
import util, arduplane
from common import *
import testutils
import testutils

class GeneralFailsafeTests():

    def test_heartbeat_failsafe(self, checkGPS=True):

        self.mavproxy.send('fence disable\n')
        wait_seconds(self.DELAY)
        self.mavproxy.send('set heartbeat 0\n')
        wait_seconds(self.DELAY)
        assert testutils.check_mode(self, 'RTL', 3, delay=21)
        if checkGPS:
            assert testutils.check_GPS(self), "GPS Failsafe test failed."

    def test_battery_current_failsafe(self, checkGPS=True):

        self.oldCurrentValue = testutils.get_old_value(self, 'FS_BATT_MAH')

        wait_seconds(self.DELAY)
        self.mavproxy.send('param set FS_BATT_MAH 123456\n')
        #Should trigger immediately
        assert testutils.check_mode(self, 'RTL', delay=1)
        if checkGPS:
            assert testutils.check_GPS(self), "GPS Failsafe test failed."

    #TODO: Can't run both battery failsafe tests without a reset.

    def test_battery_voltage_failsafe(self, checkGPS=True):
    
        assert True

        oldVoltageValue = testutils.get_old_value(self, 'FS_BATT_VOLTAGE')

        wait_seconds(self.DELAY)
        self.mavproxy.send('param set FS_BATT_VOLTAGE 123456\n')
        #Should trigger after 5 seconds, but seems to need longer
        wait_seconds(10)
        assert testutils.check_mode(self, 'RTL', delay=1), "Did not enter RTL"
        print("RTL Entered")
        if checkGPS:
            assert testutils.check_GPS(self), "GPS Failsafe test failed."
        print("GPS Passed")

    def test_fence_breach_failsafe(self, checkGPS=True):
        wait_seconds(self.DELAY)
        self.mavproxy.send('fence load %sRegressionFence\n' % self.resource_path)
        wait_seconds(self.DELAY)
        self.mavproxy.send('fence enable\n')
        wait_seconds(5)
        assert testutils.check_mode(self, 'GUIDED')
        if checkGPS:
            assert testutils.check_GPS(self), "GPS Failsafe test failed."