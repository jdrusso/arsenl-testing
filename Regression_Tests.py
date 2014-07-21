import pexpect, os, sys, signal, psutil, re
from pymavlink import mavutil
from nose.tools import nottest
from nose.plugins.skip import Skip, SkipTest
import time
import util, arduplane
from common import *

from RegressionTestGroup.ArduPlaneTestGroup import GeneralFailsafeTestGroup
from RegressionTestGroup.ArduPlaneTestGroup import GPSFailsafeTestGroup
from RegressionTestGroup import ManualOverrideTestGroup

class Regression_Tests(GeneralFailsafeTestGroup.GeneralFailsafeTests,
                        GPSFailsafeTestGroup.GPSFailsafeTests,
                        ManualOverrideTestGroup.ManualOverrideTests):

    def __init__(self):
        self.TIMEOUT=5
        self.DELAY=.5

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
        cls.TIMEOUT=5
        cls.DELAY=1.5

        cls.resource_path = os.path.join(os.path.dirname(\
            os.path.dirname(ManualOverrideTestGroup.__file__)), 'Resources/')
        
        #start MAVLink, etc
        try:
            os.remove('eeprom.bin')
        except OSError:
            pass

        try:
            os.remove('jsb_pipe')
            os.remove('mavproxy_pipe')
        except Exception:
            pass

        util.run_cmd('mkfifo mavproxy_pipe')
        util.run_cmd('mkfifo jsb_pipe')

        #Comment these out to enable logging
        #util.run_cmd('xterm -e tail -f jsb_pipe &')
        #util.run_cmd('xterm -e tail -f mavproxy_pipe &')

        util.run_cmd('echo "INITIALIZED MAVPROXY PIPE" > mavproxy_pipe &')
        util.run_cmd('echo "INITIALIZED JSBSIM PIPE" > jsb_pipe &')
        
        cls.homeloc = None
        HOME_LOCATION='35.7168007,-120.7644466,275,295' #McMillan Lat/Lon/Alt/Heading
        WIND="0,180,0.0" # speed,direction,variance
        options = '--sitl=127.0.0.1:5501 --out=127.0.0.1:19550 --streamrate=100 '
        
        #Start SITL
        cls.sil = util.start_SIL('ArduPlane', wipe=True)
        cls.mavproxy = util.start_MAVProxy_SIL('ArduPlane', options=options)
        cls.mavproxy.expect('Received [0-9]+ parameters')
        
        #Load SITL params
        cls.mavproxy.send("param load %ssitl.parm\n" % cls.resource_path)
        cls.mavproxy.expect('Loaded [0-9]+ parameters')
        
        #Fetch list of params
        cls.mavproxy.send("param fetch\n")
        
        #TODO: Optimize this. Is it necessary to start and close it?
        util.pexpect_close(cls.mavproxy)
        util.pexpect_close(cls.sil)
        
        #Start JSBSim simulation
        cmd = util.reltopdir("Tools/autotest/jsbsim/runsim.py")
        cmd += " --home=%s --wind=%s" % (HOME_LOCATION, WIND)
        #cls.runsim = pexpect.spawn(cmd, logfile=sys.stdout, timeout=10)
        cls.runsim = pexpect.spawn(cmd, logfile=file('jsb_pipe', 'w+'), timeout=10)
        cls.runsim.delaybeforesend = 0
        util.pexpect_autoclose(cls.runsim)
        cls.runsim.expect('Simulator ready to fly.')
        cls.sil = util.start_SIL('ArduPlane', valgrind=True)
        options += ' --map --console'
        cls.mavproxy = util.start_MAVProxy_SIL('ArduPlane', 
            logfile=file('mavproxy_pipe', 'w+'), options=options)
        
        #TODO: Make these easier to find
        cls.mavproxy.expect('Logging to (\S+)')
        logfile = cls.mavproxy.match.group(1)
        print("LOGFILE %s" % logfile)
        
        #TODO: Make these easier to find
        buildlog = util.reltopdir("../buildlogs/ArduPlane-test.tlog")
        print("buildlog=%s" % buildlog)
        if os.path.exists(buildlog):
            os.unlink(buildlog)
        try:
            os.link(logfile, buildlog)
        except Exception:
            pass
            
        cls.mavproxy.expect('Received [0-9]+ parameters')
        
        util.expect_setup_callback(cls.mavproxy, expect_callback)
        
        expect_list_clear()
        expect_list_extend([cls.runsim, cls.sil, cls.mavproxy])
        
        print("Started simulator.")
        
        #Get a mavlink connection started.
        try:
            cls.mav = mavutil.mavlink_connection('127.0.0.1:19550', robust_parsing=True)
        except Exception, msg:
            print("Failed to start mavlink connection on 127.0.0.1:19550" % msg)
            raise
        cls.mav.message_hooks.append(message_hook)
        cls.mav.idle_hooks.append(idle_hook)
        
        #Establish mavlink connection
        try:
            print("Waiting for a heartbeat with mavlink protocol %s" 
                % cls.mav.WIRE_PROTOCOL_VERSION)
            cls.mav.wait_heartbeat()
            print("Setting up RC parameters")
            arduplane.setup_rc(cls.mavproxy)
            print("Waiting for GPS fix")
            cls.mav.recv_match(condition='VFR_HUD.alt>10', blocking=True)
            cls.mav.wait_gps_fix()
            while cls.mav.location().alt < 10:
                cls.mav.wait_gps_fix()
            cls.homeloc = cls.mav.location()
            print("Home location: %s" % cls.homeloc)
            
        except pexpect.TIMEOUT, e:
            print("Failed with timeout")
            failed = True
            
        #Wait to exit INITIALISING
        wait_mode(cls.mav, "MANUAL")

        cls.mavproxy.send('fence disable\n')
        wait_seconds(cls.DELAY)
        #TODO:Add this to sitl.parm
        cls.mavproxy.send('param set BATT_MONITOR 4\n')

        print("Taking off to begin testing.")

        cls.takeoff()

        cls.oldCurrentValue = -3
        cls.oldVoltageValue = -3

        print('*'*15)
        print('Starting testing')
        print('*'*15)

    @classmethod
    def teardown_class(cls):
        #stop MAVLink, any postrun code
        
        print('*'*20)
        print("Shutting down.")
        cls.mav.close()
        util.pexpect_close(cls.mavproxy)
        util.pexpect_close(cls.sil)
        util.pexpect_close(cls.runsim)

        PROCNAME = ["JSBSim", "mavproxy.py"]
        for proc in psutil.process_iter():
            if proc.name() in PROCNAME:
                proc.kill()

    @classmethod
    def signal_handler(self, signal, frame):
        print('-'*20)
        try:
            self.teardown_class()
        except AttributeError:
            #mav not created yet
            pass
        util.pexpect_close_all()

    @classmethod
    def takeoff(self):

        wait_seconds(self.DELAY)
        self.mavproxy.send('wp load %sTestPoint\n' % self.resource_path)
        wait_seconds(self.DELAY)

        self.mavproxy.send('arm throttle\n')
        wait_seconds(self.DELAY)

        self.mavproxy.send('mode AUTO\n')
        wait_seconds(self.DELAY)
        assert wait_mode(self.mav, 'AUTO', timeout=3)

signal.signal(signal.SIGINT, Regression_Tests.signal_handler)