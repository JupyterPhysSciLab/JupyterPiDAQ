# Utility sampling routines for using the ADC block of the
# Pi-Plates DAQC2plate RPI HAT.
# J. Gutow <gutow@uwosh.edu> June 2020
# license GPL V3 or greater
import time
import numpy as np

import logging

try:
    from piplates import DAQC2plate
except RuntimeError as e:
    print("DAQC2plate: "+str(e))
    DAQC2plate = None

from jupyterpidaq.Boards import Board

logger = logging.getLogger(__name__)

# Optimized for Pi 3B+ for an installed ADS1115 ADC PiHAT. This is
# actually ignored by this board, but necessary for ADC call
# compatibility.
RATE = 475

def find_boards():
    """
    A rountine like this must be implemented by all board packages.

    :return: list of DAQC2 board objects (maximum of 8 boards)
    """
    boards = []
    tmpmod = None
    if DAQC2plate:
        for addr in range(len(DAQC2plate.daqc2sPresent)):
            if DAQC2plate.daqc2sPresent[addr] == 1:
                boards.append(Board_DAQC2(addr))
    return boards


class Board_DAQC2(Board):
    """
    Class defining the properties of the analog-to-digital block of the
    pi-Plates DAQC2 board. Key characteristics:

    * 8 channels (0 - 7) with pseudo 16 bit resolution (oversampled 14 bit) and
      a range of +/- 12 V.
    * 1 channel (8) dedicated to monitoring Vdd.
    * Programmable RGB LED to use as indicator.
    * Other available facilities are Digital I/O, Digital-to-Analog and
      2-channel o-scope modes. These are not supported by this class.
    """
    def __init__(self, addr):
        super().__init__()
        self.name = 'DAQC2'
        self.vendor = 'Pi-Plates'
        # Note: channel 8 is wired to Vdd so cannot be used for measurements.
        self.channels = (0, 1, 2, 3, 4, 5, 6, 7, 8)
        self.addr = addr
        # Flash light green and then off to indicated found and set up.
        DAQC2plate.setLED(self.addr,'green')
        Vddcheck = float(self.V_oversampchan(8,1,5)[0])
        self.Vdd = Vddcheck
        DAQC2plate.setLED(self.addr,'off')

    def getsensors(self):
        """
        Return a list of valid sensor object names for this board.
        :return: list of classnames
        """
        sensorlist = ['RawAtoD',
                      'VernierSSTemp',
                      'VernierGasP',
                      'VernierGasP_OLD',
                      'VernierpH',
                      'VernierFlatpH'
                      ]
        # TODO: extend this list as appropriate. You can get a full list
        #  using the `Sensors.sensors.listSensors()` call.
        # The main program will use this list to access the actual sensor
        # objects when converting the raw board voltage and for producing
        # a menu of valid options for this particular board.
        return sensorlist

    def V_oversampchan(self, chan, gain, avg_sec, data_rate=RATE):
        """
        This routine returns the average voltage for the channel
        averaged at the default rate for the board and returns an
        average and observed range.

        Returns a tuple of the following 5 objects:
            V_avg -- float, the averaged voltage

            V_min -- float, the minimum voltage read during
            the interval

            V_max -- float, the maximum voltage read during the
            interval

            time_stamp -- float, the time at halfway through the averaging
            interval in seconds since the beginning of the epoch (OS
            dependent begin time)

            Vdd_avg -- float, the reference voltage (Vdd) collected
            simultaneously.

        :param int chan: the channel number (0, 1, 2, 3, 4, 5, 6, 7,
         8). NOTE: channel 8 returns a measurement of Vdd.

        :param gain: ignored by board. Defaults to 1.

        :param int data_rate: ignored by board.

        :param float avg_sec: seconds to average for, actual
         averaging interval will be as close as possible for an integer
         number of samples

        :returns: V_avg, V_min, V_max, time_stamp, Vdd_avg
        :return float V_avg: description
        :return float V_min:
        :return float V_max:
        :return float time_stamp:
        :return float Vdd_avg:
        """
        value = []
        ref = []
        starttime = time.time()
        endtime = starttime + avg_sec
        while time.time() < endtime:
            value.append(DAQC2plate.getADC(self.addr, chan))
            ref.append(DAQC2plate.getADC(self.addr, 8))
        time_stamp = (endtime + endtime) / 2
        ndata = len(value)
        V_avg = sum(value) / ndata
        Vdd_avg = sum(ref) / ndata
        V_min = min(value)
        V_max = max(value)
        return V_avg, V_min, V_max, time_stamp, Vdd_avg

    def V_oversampchan_stats(self, chan, gain, avg_sec, data_rate=RATE):
        '''
        This routine returns the average voltage for the channel
        averaged at the maximum rate for the board. The standard
        deviation and the estimated deviation of the mean are also
        returned.

        Returns a tuple of the following 5 objects:
            V_avg -- float, the averaged voltage

            stdev -- float, the standard deviation of the measured values
            during the averaging interval

            stdev_avg -- float, the estimated standard deviation of the
            returned average

            time_stamp -- float, the time at halfway through the averaging
            interval in seconds since the beginning of the epoch (OS
            dependent begin time)

            Vdd_avg -- float, the reference voltage (Vdd) collected
            simultaneously.

        :param int chan: the channel number (0, 1, 2, 3, 4, 5, 6, 7,
         8). NOTE: channel 8 returns a measurement of Vdd.

        :param gain: ignored by board. Defaults to 1.

        :param int data_rate: ignored by board.

        :param float avg_sec: seconds to average for, actual
         averaging interval will be as close as possible for an integer
         number of samples

        :returns: V_avg, stdev, stdev_avg, time_stamp, Vdd_avg
        :return float V_avg: description
        :return float stdev:
        :return float stdev_avg:
        :return float time_stamp:
        :return float Vdd_avg:
        '''
        value = []
        ref = []
        starttime = time.time()
        endtime = starttime + avg_sec
        while time.time() < endtime:
            value.append(DAQC2plate.getADC(self.addr, chan))
            ref.append(DAQC2plate.getADC(self.addr, 8))
        time_stamp = (starttime + endtime) / 2
        ndata = len(value)
        logging.debug('channel:'+str(chan)+', starttime:'+str(starttime)+', '
                      'endtime:'+str(endtime)+', ndata:'+str(ndata)+'.')
        V_avg = sum(value) / ndata
        Vdd_avg = sum(ref) / ndata
        stdev = np.std(value, ddof=1, dtype=np.float64)
        stdev_avg = stdev / np.sqrt(float(ndata))
        return V_avg, stdev, stdev_avg, time_stamp, Vdd_avg

    def V_sampchan(self, chan, gain, data_rate=RATE):
        '''
        This routine returns a single reading of the voltage for the channel.

        Returns a tuple of the following 5 objects:
            V -- float, the measured voltage

            time_stamp -- float, the time of the measurement in seconds since
            the beginning of the epoch (OS dependent begin time)

            ref -- float, the reference voltage (Vdd) collected
            simultaneously.

        :param int chan: the channel number (0, 1, 2, 3, 4, 5, 6, 7,
         8). NOTE: channel 8 returns a measurement of Vdd.

        :param gain: ignored by board. Defaults to 1.

        :param int data_rate: ignored by board.

        :returns: V_avg, stdev, stdev_avg, time_stamp, Vdd_avg
        :return float V:
        :return float time_stamp:
        :return float ref:
        '''
        start = time.time()
        value = DAQC2plate.getADC(self.addr, chan)
        ref = DAQC2plate.getADC(self.addr, 8)
        end = time.time()
        time_stamp = (start + end) / 2
        return value, time_stamp, ref
