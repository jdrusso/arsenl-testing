from UnitTestGroup.ArduPlaneTestGroup import ParamTestGroup
from UnitTestGroup.ArduPlaneTestGroup import ModeTestGroup
from UnitTestGroup.ArduPlaneTestGroup import WaypointTestGroup
from UnitTestGroup.ArduPlaneTestGroup import FenceTestGroup
from UnitTestGroup.ArduPlaneTestGroup import CalibrationTestGroup
from UnitTestGroup.ArduPlaneTestGroup import RCTestGroup
from UnitTestGroup.ArduPlaneTestGroup import RallyTestGroup
import pexpect, os, sys, signal, psutil
from pymavlink import mavutil
import util, arduplane
from common import *
import subprocess
from GenericTest import GenericTests



class Unit_Tests(GenericTests,
    #ParamsTestsGroup.ParamsTest,
    ModeTestGroup.ModeTest,
    WaypointTestGroup.WaypointTest,
    FenceTestGroup.FenceTest,
    CalibrationTestGroup.CalibrationTest,
    RallyTestGroup.RallyTest
    ):

    pass


signal.signal(signal.SIGINT, GenericTests.signal_handler)