import pexpect, os, sys, signal, psutil, re
from pymavlink import mavutil
from nose.tools import nottest
from nose.plugins.skip import Skip, SkipTest
import time
import util, arduplane
from common import *
import subprocess

from RegressionTestGroup.ArduPlaneTestGroup import GeneralFailsafeTestGroup
from RegressionTestGroup.ArduPlaneTestGroup import GPSFailsafeTestGroup
from RegressionTestGroup import OverrideTestGroup
from GenericTest import GenericTests

class Regression_ManualOverride_Tests(GenericTests,
                                      OverrideTestGroup.MANUALOverrideTests):

    def __init__(self):
        self.MAX_HEIGHT = 700

    def setup(self, altCheck=True):
        print("*****************SETUP****************")
        wait_seconds(self.DELAY)
        self.mavproxy.send('mode AUTO\n')
        wait_seconds(self.DELAY)
        self.mavproxy.send('wp set 2\n')
        wait_seconds(self.DELAY)        
        #wait_altitude(self.mav, 380, 1200, timeout=1800)
        if altCheck:
            self.mav.recv_match(condition='VFR_HUD.alt>375', blocking=True)
        wait_seconds(self.DELAY)
        self.mavproxy.send('fence disable\n')
        wait_seconds(self.DELAY)

        print("Done setup.")
        pass

    def teardown(self):

        self.mavproxy.send('set heartbeat 1\n')
        wait_seconds(self.DELAY)

        self.mavproxy.send("param load %ssitl.parm\n" % self.resource_path)
        self.mavproxy.expect('Loaded [0-9]+ parameters')
        
        #Fetch list of params
        self.mavproxy.send("param fetch\n")

    @classmethod
    def setup_class(cls):
        
        GenericTests.setup_class()

        #TODO:Add this to sitl.parm
        cls.mavproxy.send('param set BATT_MONITOR 4\n')

        print("Taking off to begin testing.")

        cls.takeoff()

        cls.oldCurrentValue = -3
        cls.oldVoltageValue = -3

    @classmethod
    def takeoff(cls):

        wait_seconds(cls.DELAY)
        cls.mavproxy.send('wp load %sTestPoint\n' % cls.resource_path)
        wait_seconds(cls.DELAY)

        cls.mavproxy.send('arm throttle\n')
        wait_seconds(cls.DELAY)

        cls.mavproxy.send('mode AUTO\n')
        wait_seconds(cls.DELAY)
        assert wait_mode(cls.mav, 'AUTO', timeout=3)

signal.signal(signal.SIGINT, Regression_ManualOverride_Tests.signal_handler)
