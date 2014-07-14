import pexpect, os, sys, re
from pymavlink import mavutil
import util, arduplane
from common import *

class Param():

    def __init__(self, paramName, validValues = [], invalidValues = [], toggle=False):

        self.name = paramName
        self.validValues = validValues
        self.invalidValues = invalidValues
        self.toggle = toggle

#Test setting various params, also tests setting throttle
class ParamsTest():

    #Create dict of params to test.
    #Format is key : [valid values], [invalid values], toggle
    #TODO: Move paramValues definition into its own file
    paramValues = [
        Param("AHRS_EKF_USE",       toggle=True),
        Param("AHRS_GPS_MINSATS",   range(0,11,5), [-10]),
        Param("AHRS_ORIENTATION",   range(0,38)),
        Param("ALT_CTRL_ALG",       [0]),
        Param("ALT_HOLD_FBWCM",     [0, 2500, 5000, 7500, 10000]),
        Param("ALT_HOLD_RTL",       [0, 2500, 5000, 7500, 10000]),
        Param("ALT_MIX",            [0, .4, .8, 1]),
        Param("ALT_OFFSET",         [-32767, 0, 32767]),
        Param("ARMING_CHECK",       [0, 2, 4, 8, 16, 32, 64, 128, 256]),
        Param("ARMING_DIS_RUD",     toggle=True),
        Param("ARMING_REQUIRE",     [0, 1, 2]),
        Param("ARSPD_AUTOCAL",      toggle=True),
        Param("ARSPD_ENABLE",       toggle=True),
        Param("ARSPD_FBW_MAX",      [5, 25, 50]),
        Param("ARSPD_FBW_MIN",      [5, 25, 50]),
        Param("ARSPD_OFFSET",       [-5, -2.5, 0, 2.5, 5]),
        Param("ARSPD_PIN",          [11, 15, 65]),
        Param("ARSPD_RATIO",        [0, .5, 1]),
        Param("ARSPD_TUBE_ORDER",   [0, 1, 2]),
        Param("ARSPD_USE",          toggle=True),
        Param("AUTOTUNE_LEVEL",     range(0,11)),
        Param("AUTO_FBW_STEER",     toggle=True),
        #TODO:Better value for this
        #Param("BATT_AMP_OFFSET",)
        Param("BATT_AMP_PERVOLT",   [17]),
        #TODO:Better value for this
        Param("BATT_CAPACITY",      [1000, 2050, 3000]),
        Param("BATT_CURR_PIN",      [-1, 1, 2, 3, 12, 101]),
        Param("BATT_MONITOR",       [0,3,4]),
        Param("BATT_VOLT_MULT",     [10.1, 12.02]),
        Param("BATT_VOLT_PIN",      [-1, 0, 1, 2, 13, 100]),
        Param("COMPASS_AUTODEC",    toggle=True),
        Param("COMPASS_DEC",        [-3.142, 0, 3.142]),
        Param("COMPASS_EXTERNAL",   toggle=True),
        Param("COMPASS_LEARN",      toggle=True),
        Param("COMPASS_ORIENT",     range(0, 38)),
        Param("COMPASS_USE",        toggle=True),
        Param("ELEVON_CH1_REV",     [-1, 1]),
        Param("ELEVON_CH2_REV",     [-1, 1]),
        Param("ELEVON_MIXING",      toggle=True),
        Param("ELEVON_OUTPUT",      [0,1,2,3,4]),
        Param("ELEVON_REVERSE",     toggle=True),
        Param("FBWB_CLIMB_RATE",    [1, 5.5, 10]),
        Param("FBWB_ELEV_REV",      toggle=True),
        Param("FENCE_ACTION",       [0,1,2,3]),
        Param("FENCE_AUTOENABLE",   toggle=True),
        Param("FENCE_CHANNEL",      range(1,9)),
        Param("FENCE_MAXALT",       [0, 16000, 32767]),
        Param("FENCE_MINALT",       [0, 16000, 32767]),
        Param("FENCE_RETALT",       [0, 16000, 32767]),
        Param("FENCE_RET_RALLY",    toggle=True),
        #Param("FENCE_TOTAL"),  
        Param("FLTMODE1",           [x for x in range(0,16) if x not in [9,13,14]]),
        Param("FLTMODE2",           [x for x in range(0,16) if x not in [9,13,14]]),
        Param("FLTMODE3",           [x for x in range(0,16) if x not in [9,13,14]]),
        Param("FLTMODE4",           [x for x in range(0,16) if x not in [9,13,14]]),
        Param("FLTMODE5",           [x for x in range(0,16) if x not in [9,13,14]]),
        Param("FLTMODE6",           [x for x in range(0,16) if x not in [9,13,14]]),
        Param("FLTMODE_CH",         range(1,9)),
        #TODO:Better value for this
        #Param("FS_BATT_MAH",)
        #TODO:Better value for this
        #Param("FS_BATT_VOLTAGE")
        #TODO:Debug this.
        #Param("FS_GCS_ENABLE",      [0,1,2]),
        Param("FS_LONG_ACTN",       [0,1,2]),
        Param("FS_LONG_TIMEOUT",    [1, 100, 150.5, 200, 300]),
        Param("FS_SHORT_ACTN",      [0,1,2]),
        Param("FS_SHORT_TIMEOUT",   [1, 25, 50.5, 75, 100]),
        Param("GND_ALT_OFFSET",     [-128,-64,0,64,-128]),
        Param("GPS_NAVFILTER",      [0] + range(2,9)),
        Param("GPS_TYPE",           range(0,9)),
        Param("GPS_TYPE2",          range(0,9)),
        Param("KFF_RDDRMIX",        [float(x)/10 for x in range(0,11,2)]),
        Param("KFF_THR2PTCH",       [0, 1.1, 2.2, 3.3, 4.4, 5]),
        Param("LAND_FLARE_ALT",     [0, 10.5, 20, 50, 100]),
        Param("LAND_FLARE_SEC",     [0, 10.5, 20, 50, 100]),
        #Param("LAND_PITCH_CD")
        Param("LEVEL_ROLL_LIMIT",   range(0, 46, 5)),
        Param("LIM_PITCH_MAX",      range(0, 9001, 1000)),
        Param("LIM_PITCH_MIN",      range(0, 9001, 1000)),
        Param("LIM_ROLL_CD",        range(0, 9001, 1000)),
        Param("LOG_BITMASK",        [0, 65535]),
        Param("MAG_ENABLE",         toggle=True),
        #TODO:Better value for this
        #Param("MIN_GNDSPD_CM",      ),
        Param("MIS_RESTART",        toggle=True),
        Param("MIXING_GAIN",        [0.5, 0.8, 1.0, 1.2]),
        Param("NAVL1_DAMPING",      [0.6, 0.85, 1]),
        Param("NAVL1_PERIOD",       [1, 15, 30, 45, 60]),
        Param("NAV_CONTROLLER",     toggle=True),
        Param("PTCH2SRV_D",         [0, .1, .5, .7, 1]),
        Param("PTCH2SRV_I",         [0, .25, .5]),
        Param("PTCH2SRV_IMAX",      [0, 1500, 3000, 4500]),
        Param("PTCH2SRV_P",         [.1, .5, 1, 1.5, 2]),
        Param("PTCH2SRV_RLL",       [.7, 1, 1.25, 1.5]),
        Param("PTCH2SRV_RMAX_DN",   [0, 25, 50, 100]),
        Param("PTCH2SRV_RMAX_UP",   [0, 25, 50, 100]),
        Param("PTCH2SRV_TCONST",    [.4, .7, .9, 1]),
        Param("RALLY_LIMIT_KM",     [0, 50, 100, 1000]),
        Param("RC1_DZ",             [0, 50, 100, 150, 200]),
        Param("RC1_MAX",            [800, 1500, 2000, 2200]),
        Param("RC1_MIN",            [800, 1500, 2000, 2200]),
        Param("RC1_REV",            [-1, 1]),
        Param("RC1_TRIM",           [800, 1500, 2000, 2200]),
        Param("RC2_DZ",             [0, 50, 100, 150, 200]),
        Param("RC2_MAX",            [800, 1500, 2000, 2200]),
        Param("RC2_MIN",            [800, 1500, 2000, 2200]),
        Param("RC2_REV",            [-1, 1]),
        Param("RC2_TRIM",           [800, 1500, 2000, 2200]),
        Param("RC3_DZ",             [0, 50, 100, 150, 200]),
        Param("RC3_MAX",            [800, 1500, 2000, 2200]),
        #TODO: Why does this cause a float exception if min is equal to max?
        #ONLY does it for RC3, no other channels
        Param("RC3_MIN",            [800, 1500, 2200]),
        Param("RC3_REV",            [-1, 1]),
        Param("RC3_TRIM",           [800, 1500, 2000, 2200]),
        Param("RC4_DZ",             [0, 50, 100, 150, 200]),
        Param("RC4_MAX",            [800, 1500, 2000, 2200]),
        Param("RC4_MIN",            [800, 1500, 2000, 2200]),
        Param("RC4_REV",            [-1, 1]),
        Param("RC4_TRIM",           [800, 1500, 2000, 2200]),
        Param("RLL2SRV_D",          [0, .02, .05, .07, .1]),
        Param("RLL2SRV_I",          [0, .25, .5, .75, 1]),
        Param("RLL2SRV_IMAX",       [0, 1500, 3000, 4500]),
        Param("RLL2SRV_P",          [.1, .5, 1, 1.5, 2]),
        Param("RLL2SRV_RMAX",       [0, 60, 120, 180]),
        Param("RLL2SRV_TCONST",     [.4, .6, .8, 1]),
        Param("RSSI_RANGE",         [3.3, 5.0]),
        Param("RST_MISSION_CH",     range(0,9)),
        Param("SERIAL0_BAUD",       [1,2,4,9,19,38,57,111,115,500,921,15000]),
        Param("SERIAL1_BAUD",       [1,2,4,9,19,38,57,111,115,500,921,15000]),
        Param("SERIAL2_BAUD",       [1,2,4,9,19,38,57,111,115,500,921,15000]),
        Param("SKIP_GYRO_CAL",      toggle=True),
        Param("STICK_MIXING",       [0,1,2]),
        #TODO: Better value for this
        Param("TECS_CLMB_MAX",      [0, 2.5, 5]),
        Param("TECS_HGT_OMEGA",     [1, 2, 2.5, 3.05, 5]),
        Param("TECS_INTEG_GAIN",    [0, .2, .24, .4, .5]),
        Param("TECS_LAND_ARSPD",    [-1, 0, 1, 50, 100, 127]),
        Param("TECS_LAND_SPDWGT",   [0, .5, 1, 1.5, 2]),
        #TODO: Better value for this. Not in documentation
        #Param("TECS_LAND_THR",      []),
        Param("TECS_PTCH_DAMP",     [.1, .5, 1]),
        Param("TECS_RLL2THR",       [5, 15, 30]),
        #TODO: Better value for these
        #Param("TECS_SINK_MAX",      [0, .5, 1]),
        #Param("TECS_SINK_MIN"),
        Param("TECS_SPDWEIGHT",     [0, .5, 1, 1.5, 2]),
        Param("TECS_SPD_OMEGA",     [.5, 1.25, 1.75, 2]),
        Param("TECS_THR_DAMP",      [.1, .5, 1]),
        Param("TECS_TIME_CONST",    [3, 5.6, 10]),
        Param("TECS_VERT_ACC",      [1, 2.5, 5, 7.5, 10]),
        Param("TELEM_DELAY",        [0, 5, 10]),
        Param("THROTTLE_NUDGE",     toggle=True),
        Param("THR_FAILSAFE",       toggle=True),
        Param("THR_FS_VALUE",       [925, 1000, 1100]),
        Param("THR_MAX",            range(0,101,25)),
        Param("THR_MIN",            range(0,101,25)),
        Param("THR_PASS_STAB",      toggle=True),
        Param("THR_SLEWRATE",       range(0,101,25)),
        Param("THR_SUPP_MAN",       toggle=True),
        Param("TKOFF_ROTATE_SPD",   [0, 15.5, 30]),
        Param("TKOFF_TDRAG_ELEV",   [-100, -50, 0, 50, 100]),
        Param("TKOFF_TDRAG_SPD1",   [0, 15.5, 30]),
        Param("TKOFF_THR_DELAY",    [0, 5.5, 10, 15]),
        Param("TKOFF_THR_MAX",      range(0,101,25)),
        Param("TKOFF_THR_MINACC",   [0, 15.5, 30]),
        Param("TKOFF_THR_MINSPD",   [0, 15.5, 30]),
        Param("TKOFF_THR_SLEW",     range(0,101,25)),
        #TODO: Better value for these
        #Param("TRIM_ARSPD_CM"),
        Param("TRIM_AUTO",          toggle=True),
        #TODO: Better value for these
        #Param("TRIM_PITCH_CD"),
        Param("TRIM_THROTTLE",      range(0,101,25)),
        Param("WP_LOITER_RAD",      [-32767, 0, 32767]),
        Param("WP_MAX_RADIUS",      [0, 16000, 32767]),
        Param("WP_RADIUS",          [1, 16000, 32767]),
        Param("YAW2SRV_DAMP",       [0, .75, 1, 1.25, 2]),
        Param("YAW2SRV_IMAX",       [0, 1500, 3000, 4500]),
        Param("YAW2SRV_INT",        [0, .75, 1, 1.25, 2]),
        Param("YAW2SRV_RLL",        [.8, .95, 1.05, 1.2]),
        Param("YAW2SRV_SLIP",       [0, 1.75, 3.25, 4])
    ]

    paramNamesList = []
    for param in paramValues:
        paramNamesList += param.name


    def test_params_arm_throttle(self):
        #Attempt to arm the throttle
        
        self.mavproxy.send('arm throttle\n')
        #self.mavproxy.send('status\n')
        assert {0:True, 1:False}[self.mavproxy.expect('Throttle armed', timeout=self.TIMEOUT)]
        pass


    def test_params_disarm_throttle(self):
        #Attempt to disarm the throttle
        
        self.mavproxy.send('disarm throttle\n')
        #self.mavproxy.send('status\n')
        assert {0:True, 1:False}[self.mavproxy.expect('Throttle disarmed', timeout=self.TIMEOUT)]

    def check_set_param(self, paramName, validValues=[], invalidValues=[], toggle=False):
        #Set a parameter, check it was successfully set, and restore the original value

        DELAY = .1

        self.mavproxy.send('param show %s\n' % paramName)
        self.mavproxy.expect('%s\s*(-?\d+\.?\d*)' % paramName, timeout=self.TIMEOUT)
        oldValue = re.match("%s\s*(-?\d+\.?\d*)" % paramName, self.mavproxy.after).group(1)
        print("Old value was %s" % oldValue)

        if toggle:
            validValues = [0, 1]

        #Attempt to set the valid values
        for value in validValues:

            print("Testing value %s" % value)

            #Set the new value
            self.mavproxy.send('param set %s %s\n' % (paramName, str(value)))
            wait_seconds(DELAY)
            #Check it was set
            self.mavproxy.send('param fetch %s\n' % paramName)
            wait_seconds(DELAY)
            self.mavproxy.send('param show %s\n' % paramName)
            wait_seconds(DELAY)
            assert {0:True, 1:False}[self.mavproxy.expect('%s(\s*)%s' % (paramName, str(value)), timeout=self.TIMEOUT)], "Failed to set %s" % paramName

            #Reset to original value
            self.mavproxy.send('param set %s %s\n' % (paramName, oldValue))
            wait_seconds(DELAY)
            #Check it was reset
            self.mavproxy.send('param fetch %s\n' % paramName)
            wait_seconds(DELAY)
            assert {0:True, 1:False}[self.mavproxy.expect('Requested parameter', timeout=self.TIMEOUT)], "Failed ato set %s" % paramName
            self.mavproxy.send('param show %s\n' % paramName)
            wait_seconds(DELAY)
            assert {0:True, 1:False}[self.mavproxy.expect('%s(\s*)%s' % (paramName, str(oldValue)), timeout=self.TIMEOUT)], "Failed to reset %s" % paramName

    #TODO: Boundary testing

    def test_set_params(self):
        
        #Make sure throttle is disarmed
        wait_seconds(self.DELAY)
        self.mavproxy.send('disarm throttle\n')
        wait_seconds(self.DELAY)

        for param in ParamsTest.paramValues:

            yield self.check_set_param, param.name, param.validValues, param.invalidValues, param.toggle