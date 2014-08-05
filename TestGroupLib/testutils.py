import pexpect, util, re
from pymavlink import mavutil
from common import *

#TODO: GPS Failsafe doesn't exist in ArduPlane yet!
def check_GPS(self):

    self.mavproxy.send('param set SIM_GPS_DISABLE 1\n')


    check_mode(self, 'CIRCLE', delay=6)

    #LONG failsafe after 20s
    wait_seconds(16)
    self.mavproxy.send('status RC_CHANNELS_RAW\n')
    wait_seconds(self.DELAY)
    assert {0:True, 1:False}[self.mavproxy.expect('chan3_raw : 1000', timeout=self.TIMEOUT)]
    wait_seconds(self.DELAY)
    self.mavproxy.send('param set SIM_GPS_DISABLE 0\n')
    wait_seconds(4)
    return True

def get_old_value(self, paramName):

    self.mavproxy.send('param show %s\n' % paramName)
    self.mavproxy.expect('%s\s*(-?\d+\.?\d*)' % paramName, timeout=self.TIMEOUT)
    oldValue = re.match("%s\s*(-?\d+\.?\d*)" % paramName, self.mavproxy.after).group(1)
    return oldValue

def check_mode(self, mode, TIME=5, delay=0):
    #return wait_mode(self.mav, mode, timeout=TIME)

    if not hasattr(self, 'modemap'):
        #Create an inverse dictionary of {[mode name] : [number]}
        self.modemap= {v : k for k, v in mavutil.mode_mapping_apm.items()}

    wait_seconds(delay)

    wait_seconds(self.DELAY)
    self.mavproxy.send('status HEARTBEAT\n')
    wait_seconds(self.DELAY)

    success = {0:True, 1:False}[self.mavproxy.expect('custom_mode : %d(?![0-9])' % self.modemap[mode], timeout=TIME)]
   
    print(self.mavproxy.after)

    return success


#TODO: This is a stopgap workaround until I can why mavutil.wait_altitude doesn't work.
def wait_altitude(self, alt_min, alt_max, timeout=90):
    waitDelay = .2
    climb_rate = 0
    previous_alt = 0
    '''wait for a given altitude range'''
    tstart = time.time()
    print("Waiting for an altitude between %u and %u" % (alt_min, alt_max))
    while time.time() < tstart + timeout:


        self.mavproxy.send('mode AUTO\n')
        wait_seconds(waitDelay)
        self.mavproxy.send('param set SIM_GPS_DISABLE 0\n')
        wait_seconds(waitDelay)
        alt = -1
        self.mavproxy.send('status VFR_HUD\n')
        wait_seconds(waitDelay)
        self.mavproxy.expect('alt : \d*', timeout=self.TIMEOUT)
        alt = int(re.match("alt : (\d*)", self.mavproxy.after).group(1))
        assert alt in range(1, 100000), "Invalid altitude!"
        climb_rate =  alt - previous_alt
        previous_alt = alt
        print("Wait Altitude: Cur:%u, min_alt:%u, climb_rate: %u" % (alt, alt_min , climb_rate))
        if alt >= alt_min:
            print("Altitude OK")
            return True
        wait_seconds(1)
    print("Failed to attain altitude range")
    return False