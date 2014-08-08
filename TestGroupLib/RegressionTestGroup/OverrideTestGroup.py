import pexpect, os, sys
from pymavlink import mavutil
import util, arduplane
from common import *
import testutils

from ArduPlaneTestGroup import GeneralFailsafeTestGroup
from ArduPlaneTestGroup import GPSFailsafeTestGroup

# This class is currently commented out because the override
# tests have been broken out into Regression_ManualOverride_Tests.py
# and Regression_FBWAOverride_Tests.py so the SITL instance
# is rebuilt between override tests.
# This is done to circumvent the bug that prevents two battery
# failsafes from being triggered in the same autopilot run.
#
# When this bug is patched, uncomment this, and scrap the
# FBWAOverrideTests and MANUALOverrideTests classes, scrap
# Regression_MANUAL/FBWAOverride_Tests.py modules, and
# just inherit OverrideTests in Regression_Tests.py:Regression_Tests.
# Also make sure to add 'cls.' before all the methods in

# class OverrideTests():

#     def test_overrides(self):
#         overrideModes = ['MANUAL', 'FBWA']

#         for mode in overrideModes:
#             yield check_overrides, self, mode


    # def check_overrides(self, startMode):
    #     #TODO: Why isnt setup running?
    #     self.mavproxy.send('set heartbeat 1\n')
    #     wait_seconds(self.DELAY)
    #     self.mavproxy.send('mode AUTO\n')
    #     wait_seconds(self.DELAY)
    #     print("STARTING %s OVERRIDE TESTS" % startMode)
    #     self.mavproxy.send('wp set 3\n')
    #     wait_seconds(self.DELAY)

    #     testList = [#self.test_battery_current_failsafe,
    #     #self.test_battery_voltage_failsafe,
    #     self.test_gps_failsafe,
    #     self.test_fence_breach_failsafe,
    #     self.test_heartbeat_failsafe]

    #     testResults = {}

    #     for test in testList:

    #         print("Running %s" % test.__name__)
    #         try:

    #             print("Starting try")

    #             wait_seconds(self.DELAY)
    #             print("Test starting.")
    #             self.setup(altCheck=False)
    #             print("GOING UP")
    #             self.mavproxy.send('wp set 3\n')
    #             testutils.wait_altitude(self, 950, 1000, timeout=75)
    #             print("NOW UP")
    #             self.mavproxy.send('mode %s\n' % startMode)
    #             testutils.check_mode(self, '%s' % startMode)
    #             wait_seconds(self.DELAY)
    #             self.mavproxy.send('fence disable\n')
    #             wait_seconds(self.DELAY)
    #             if test.__name__ == 'test_gps_failsafe':
    #                 test()
    #             else:
    #                 test(self, False)
    #             wait_seconds(self.DELAY)
    #             self.mavproxy.send('fence disable\n')
    #             wait_seconds(self.DELAY)
    #             self.teardown()
    #             print("Test finished.")
    #             wait_seconds(self.DELAY)

    #         #Exception is thrown by test's assert if the failsafe RTL is not triggered
    #         except Exception as e:

    #             wait_seconds(self.DELAY)
    #             print("Failsafe didn't trip -- this means %s override is working" % startMode)
    #             print(e)
    #             success = True
    #             wait_seconds(self.DELAY)
    #         else:

    #             wait_seconds(self.DELAY)
    #             print("Failsafe tripped -- this shouldn't happen")
    #             success = False
    #             wait_seconds(self.DELAY)
    #         finally:

    #             testResults[test.__name__] = success

    #     print testResults
    #     print '%s overrides successfully passed: %r' %(startMode, (not False in testResults.values()))
    #     assert not False in testResults.values()

class FBWAOverrideTests():

    def test_overrides(self):
        check_overrides(self, 'FBWA')

class MANUALOverrideTests():

    def test_overrides(self):
        check_overrides(self, 'MANUAL')

def check_overrides(cls, startMode):
    #TODO: Why isnt setup running?
    cls.mavproxy.send('set heartbeat 1\n')
    wait_seconds(cls.DELAY)
    cls.mavproxy.send('mode AUTO\n')
    wait_seconds(cls.DELAY)
    print("STARTING %s OVERRIDE TESTS" % startMode)
    cls.mavproxy.send('wp set 3\n')
    wait_seconds(cls.DELAY)

    testList = [test_battery_current_failsafe,
    #cls.test_battery_voltage_failsafe,
    test_gps_failsafe,
    test_fence_breach_failsafe,
    test_heartbeat_failsafe
    ]

    testResults = {}


    testutils.wait_altitude(cls, 1400, 1500, timeout=180)

    for test in testList:

        print("Running %s" % test.__name__)
        try:

            print("Starting try")

            wait_seconds(cls.DELAY)
            print("Test starting.")
            cls.setup(altCheck=False)
            print("GOING UP")
            cls.mavproxy.send('wp set 3\n')
            testutils.wait_altitude(cls, 1400, 1500, timeout=85)
            print("NOW UP")
            cls.mavproxy.send('mode %s\n' % startMode)
            testutils.check_mode(cls, '%s' % startMode)
            wait_seconds(cls.DELAY)
            cls.mavproxy.send('fence disable\n')
            wait_seconds(cls.DELAY)
            test(cls, False)
            wait_seconds(cls.DELAY)
            cls.mavproxy.send('fence disable\n')
            wait_seconds(cls.DELAY)
            cls.teardown()
            print("Test finished.")
            wait_seconds(cls.DELAY)

        #Exception is thrown by test's assert if the failsafe RTL is not triggered
        except Exception as e:

            wait_seconds(cls.DELAY)
            print("Failsafe didn't trip -- this means %s override is working" % startMode)
            print(e)
            success = True
            wait_seconds(cls.DELAY)
        else:

            wait_seconds(cls.DELAY)
            print("Failsafe tripped -- this shouldn't happen")
            success = False
            wait_seconds(cls.DELAY)
        finally:

            testResults[test.__name__] = success

    print testResults
    print '%s overrides successfully passed: %r' %(startMode, (not False in testResults.values()))
    assert not False in testResults.values()




# These functions are redefined here to work with the stopgap
# MANUAL/FBWAOverride classes. Delete them when that battery
# failsafe bug is fixed.

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

def test_fence_breach_failsafe(self, checkGPS=True):
    wait_seconds(self.DELAY)
    self.mavproxy.send('fence load %sRegressionFence\n' % self.resource_path)
    wait_seconds(self.DELAY)
    self.mavproxy.send('fence enable\n')
    wait_seconds(5)
    assert testutils.check_mode(self, 'GUIDED')
    if checkGPS:
        assert testutils.check_GPS(self), "GPS Failsafe test failed."


def test_gps_failsafe(self, checkGPS=True):
    assert testutils.check_GPS(self)