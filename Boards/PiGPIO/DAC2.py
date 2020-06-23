# Utility sampling routines for using the ADC block of the
# Pi-Plates DAQC2plate RPI HAT.
# J. Gutow <jgutow@new.rr.com> June 2020
# license GPL V3 or greater
import time
import numpy as np

import logging

from piplates import DAQC2plate

from Boards.boards import Board

logger = logging.getLogger(__name__)

# Optimized for Pi 3B+ for an installed ADS1115 ADC PiHAT. This is
# actually ignored by this board, but necessary for ADC call
# compatibility.
RATE = 475


# 475 Hz with oversampling best S/N on Pi 3B+ per unit time interval.

def find_boards():
    """
    A rountine like this must be implemented by all board packages.

    :return: list of DAQC2 board objects (maximum of 8 boards)
    """
    boards = []
    tmpmod = None
    for addr in range(len(DAQC2plate.daqc2sPresent)):
        if DAQC2plate.daqc2sPresent[addr] == 1:
            boards.append(Board_DAQC2(addr))
    return boards


class Board_DAQC2(Board):
    def __init__(self, addr):
        super().__init__()
        self.name = 'DAQC2'
        self.vendor = 'Pi-Plates'
        self.channels = (0, 1, 2, 3, 4, 5, 6, 7)
        self.addr = addr
        Vddcheck = float(self.V_sampchan(8,1,5)[0])
        self.Vdd = Vddcheck
        # Flash light green and then off to indicated found and set up.
        DAQC2plate.setLED(self.addr,'green')
        time.sleep(2.0)
        DAQC2plate.setLED(self.addr,'off')

    def getsensors(self):
        """
        Return a list of valid sensor object names for this board.
        :return: list of classnames
        """
        sensorlist = ['RawAtoD', 'VernierSSTemp']
        # TODO: extend this list as appropriate. You can get a full list
        #  using the `Sensors.sensors.listSensors()` call.
        # The main program will use this list to access the actual sensor
        # objects when converting the raw board voltage and for producing
        # a menu of valid options for this particular board.
        return sensorlist

    def V_oversampchan(self, chan, gain, avg_sec, data_rate=RATE):
        '''
        This routine returns the average voltage for the channel
        averaged at the default rate for the board and returns an
        average and observed range.

        Parameters
            chan    the channel number 0, 1, 2, 3, 4, 5, 6, 7
            gain    always 1
            data_rate not used by this board
            avg_sec seconds to average for. Greater than 0.0058 seconds.
        Returns a tuple (V_avg, V_min, V_max, time_stamp)
            V_avg   the averaged voltage
            V_min   the minimum voltage read during the interval
            V_max   the maximum voltage read during the interval
            time_stamp the time at halfway through the averaging interval in seconds
                    since the beginning of the epoch (OS dependent begin time).
        '''
        value = []
        starttime = time.time()
        endtime = starttime + avg_sec
        while time.time() < endtime:
            value.append(DAQC2plate.getADC(self.addr, chan))
        time_stamp = (endtime + endtime) / 2
        ndata = len(value)
        V_avg = sum(value) / ndata
        V_min = min(value)
        V_max = max(value)
        return V_avg, V_min, V_max, time_stamp

    def V_oversampchan_stats(self, chan, gain, avg_sec, data_rate=RATE):
        '''
        This routine returns the average voltage for the channel
        averaged at the maximum rate for the board. The standard
        deviation and the estimated deviation of the mean are also
        returned.

        Parameters
            chan    the channel number 0, 1, 2, 3, 4, 5, 6, 7
            gain    ignored always 1 for this board
            data_rate ignored, will average as fast as possible (~ 500 Hz)
            avg_sec seconds to average for. Minimum of about 0.0058 seconds.
        Returns a tuple (V_avg, V_min, V_max, time_stamp)
            V_avg   the averaged voltage
            stdev   estimated standard deviation of the measurements
            stdev_avg   estimated standard deviation of the mean
            time_stamp the time at halfway through the averaging interval in seconds
                    since the beginning of the epoch (OS dependent begin time).
        '''
        value = []
        starttime = time.time()
        endtime = starttime + avg_sec
        while time.time() < endtime:
            value.append(DAQC2plate.getADC(self.addr, chan))
        time_stamp = (starttime + endtime) / 2
        ndata = len(value)
        V_avg = sum(value) / ndata
        stdev = np.std(value, ddof=1, dtype=np.float64)
        stdev_avg = stdev / np.sqrt(float(ndata))
        return V_avg, stdev, stdev_avg, time_stamp

    def V_sampchan(self, chan, gain, data_rate=RATE):
        '''
        This routine returns a single reading of the voltage for the channel
        Parameters
            chan    the channel number 0, 1, 2, 3, 4, 5, 6, 7
            gain    ignored by this board
            data_rate ignored by this board
        Returns a tuple (V, time_stamp)
            V       the voltage
            time_stamp the time at halfway through the averaging interval in seconds
                    since the beginning of the epoch (OS dependent begin time).
        '''
        start = time.time()
        value = DAQC2plate.getADC(self.addr, chan)
        end = time.time()
        time_stamp = (start + end) / 2
        return (value, time_stamp)
