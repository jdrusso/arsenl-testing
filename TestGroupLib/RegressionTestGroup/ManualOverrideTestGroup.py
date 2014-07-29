import pexpect, os, sys
from pymavlink import mavutil
import util, arduplane
from common import *
import testutils

class ManualOverrideTests():
    def test_manual_overrides(self):
        #TODO: Why isnt setup running?
        self.mavproxy.send('set heartbeat 1\n')
        wait_seconds(self.DELAY)
        self.mavproxy.send('mode AUTO\n')
        wait_seconds(self.DELAY)
        print("STARTING MANUAL OVERRIDE TESTS")
        self.mavproxy.send('wp set 3\n')
        wait_seconds(self.DELAY)

        testList = [self.test_battery_current_failsafe,
        #self.test_battery_voltage_failsafe,
        self.test_gps_failsafe,
        self.test_fence_breach_failsafe,
        self.test_heartbeat_failsafe]

        testResults = {}

        for test in testList:

            print("Running %s" % test.__name__)
            try:

                print("Starting try")

                wait_seconds(self.DELAY)
                print("Test starting.")
                self.setup(altCheck=False)
                print("GOING UP")
                self.mavproxy.send('wp set 3\n')
                testutils.wait_altitude(self, 890, 950, timeout=45)
                print("NOW UP")
                self.mavproxy.send('mode MANUAL\n')
                testutils.check_mode(self, 'MANUAL')
                wait_seconds(self.DELAY)
                self.mavproxy.send('fence disable\n')
                wait_seconds(self.DELAY)
                if test.__name__ == 'test_gps_failsafe':
                    test()
                else:
                    test(False)
                wait_seconds(self.DELAY)
                self.mavproxy.send('fence disable\n')
                wait_seconds(self.DELAY)
                self.teardown()
                print("Test finished.")
                wait_seconds(self.DELAY)

            except Exception as e:

                wait_seconds(self.DELAY)
                print("Failsafe didn't trip -- this means manual override is working")
                print(e)
                success = True
                wait_seconds(self.DELAY)
            else:

                wait_seconds(self.DELAY)
                print("Failsafe tripped -- this shouldn't happen")
                success = False
                wait_seconds(self.DELAY)
            finally:

                testResults[test.__name__] = success

        print testResults
        print(False in testResults.values())
        assert not False in testResults.values()