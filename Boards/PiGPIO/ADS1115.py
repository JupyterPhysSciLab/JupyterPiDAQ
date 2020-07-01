# Utility sampling routines for using the ADS1115 ADC RPI HAT.
# J. Gutow <gutow@uwosh.edu> Nov. 12, 2018
# license GPL V3 or greater
import time
import numpy as np

import logging

import Adafruit_PureIO.smbus as smbus
import Adafruit_ADS1x15

from Boards.boards import Board

logger = logging.getLogger(__name__)

# Optimized for Pi 3B+
RATE = 475  # 475 Hz with oversampling best S/N on Pi 3B+ per unit time interval.
# TODO: a more sophisticated initialization, which determines the loop time
#  and optimal value for RATE.

# other rates 8, 16, 32, 64, 128, 250, 475, 860 in Hz.

def find_boards():
    """
    A routine like this must be implemented by all board packages.

    :return: list of ADS1115 board objects (maximum of 4 boards)
    """
    POSS_ADDR = (0x48, 0x49, 0x4A, 0x4B)
    boards = []
    tmpmod = None
    try:
        I2Cbus = smbus.SMBus(1)
    except OSError:
        # no bus so there cannot be any boards.
        return boards
    for addr in POSS_ADDR:
        try:
            I2Cbus.read_byte(addr)
        except OSError:
            continue
        try:
            tmpmod = Adafruit_ADS1x15.ADS1115(address=addr)            
        except RuntimeError as e:
            logger.debug(e)
            # print('No ADS1115 at: '+str(addr))
            tmpmod = None
        if tmpmod:
            boards.append(Board_ADS1115(tmpmod))
    return boards

class Board_ADS1115(Board):
    """
    Class defining the properties of Adafruit compatible ADS1115
    analog-to-digital boards for Raspberry-Pi style GPIO. Key characteristics:

    * 4 channels (0 - 3) with 16 bit resolution and a range of +/- 3.3 V
    * Programmable gain on each channel of 2/3, 1, 2, 4, 8, 16 making these
      good for small signals.
    * a differential mode is available but not implemented in this class.
    """
    def __init__(self,adc):
        super().__init__()
        self.name = 'ADS1115'
        self.vendor = '?' # Adafruit equivalent
        self.channels = (0, 1, 2, 3)
        self.gains = [2/3, 1, 2, 4, 8, 16]
        self.Vdd = 3.3
        self.adc = adc

    def getsensors(self):
        """
        Return a list of valid sensor object names for this board.
        :return: list of classnames
        """
        sensorlist = ['RawAtoD', 'BuiltInThermistor', 'VernierSSTemp']
        # TODO: extend this list as appropriate. You can get a full list
        #  using the `Sensors.sensors.listSensors()` call.
        # The main program will use this list to access the actual sensor
        # objects when converting the raw board voltage and for producing
        # a menu of valid options for this particular board.
        return sensorlist

    def V_oversampchan(self, chan, gain, avg_sec, data_rate=RATE):
        """
        This routine returns the average voltage for the channel
        averaged at (0.0012 + 1/data_rate)^-1 Hz for avg_sec
        number of seconds. The 0.0012 is the required loop time
        on a RPI 3B+ in python.

        Returns a tuple of the following 5 objects:
            V_avg -- float, the averaged voltage

            V_min -- float, the minimum voltage read during
            the interval

            V_max -- float, the maximum voltage read during the
            interval

            time_stamp -- float, the time at halfway through the averaging
            interval in seconds since the beginning of the epoch (OS
            dependent begin time)

            self.Vdd -- float, the reference voltage.

        :param int chan: the channel number (0, 1, 2, 3)

        :param gain: 2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V),
         4(+/-1.024V), 8 (+/-0.512V), 16 (+/-0.256V))

        :param int data_rate: the ADC sample rate in Hz (8, 16, 32, 64,
         128,250, 475 or 860 Hz). Set to 475 Hz by default.

        :param float avg_sec: seconds to average for, actual
         averaging interval will be as close as possible for an integer
         number of samples

        :returns: V_avg, V_min, V_max, time_stamp, self.Vdd
        :return float V_avg: description
        :return float V_min:
        :return float V_max:
        :return float time_stamp:
        :return float self.Vdd:
        """
        n_samp = int(round(avg_sec / (0.0012 + 1 / data_rate)))
        value = [0] * n_samp
        avgmax = self.adc.read_adc(chan, gain=gain, data_rate=data_rate)
        avgmin = avgmax
        start = time.time()
        # TODO: more error checking as in stats below
        for k in range(n_samp):
            value[k] = self.adc.read_adc(chan, gain=gain, data_rate=data_rate)
        end = time.time()
        time_stamp = (start + end) / 2
        V_avg = sum(value) * 4.096 / n_samp / gain / 32767
        V_min = min(value) * 4.096 / gain / 32767
        V_max = max(value) * 4.096 / gain / 32767
        return V_avg, V_min, V_max, time_stamp, self.Vdd


    def V_oversampchan_stats(self, chan, gain, avg_sec, data_rate=RATE):
        """
        This routine returns the average voltage for the channel
        averaged at (0.0012 + 1/data_rate)^-1 Hz for avg_sec
        number of seconds. The 0.0012 is the required loop time
        on a RPI 3B+ in python3. The standard
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

            self.Vdd -- float, the reference voltage.

        :param int chan: the channel number (0, 1, 2, 3)

        :param gain: 2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V),
         4(+/-1.024V), 8 (+/-0.512V), 16 (+/-0.256V))

        :param int data_rate: the ADC sample rate in Hz (8, 16, 32, 64,
         128,250, 475 or 860 Hz). Set to 475 Hz by default.

        :param float avg_sec: seconds to average for, actual
         averaging interval will be as close as possible for an integer
         number of samples

        :returns: VV_avg, stdev, stdev_avg, time_stamp, self.Vdd
        :return float V_avg: description
        :return float stdev:
        :return float stdev_avg:
        :return float time_stamp:
        :return float self.Vdd:
        """
        n_samp = int(round(avg_sec / (0.0017 + 1 / data_rate)))
        if (n_samp < 1):
            n_samp = 1
        value = []
        start = 0
        end = 0
        while (len(
                value) == 0):  # we will try until we get some values in case of bad reads
            start = time.time()
            for k in range(n_samp):
                try:
                    tempval = self.adc.read_adc(chan, gain=gain,
                                            data_rate=data_rate)
                except (ValueError, OverflowError):
                    print('Bad adc read.')
                    pass
                else:
                    if (tempval >= -32767) and (tempval <= 32767):
                        value.append(tempval)
                # time.sleep(0.0005)
            end = time.time()
        time_stamp = (start + end) / 2
        V_avg = sum(value) * 4.096 / len(value) / gain / 32767
        stdev = np.std(value, ddof=1, dtype=np.float64) * 4.096 / gain / 32767
        stdev_avg = stdev / np.sqrt(float(len(value)))
        return V_avg, stdev, stdev_avg, time_stamp, self.Vdd


    def V_sampchan(self, chan, gain, data_rate=RATE):
        """
        This routine returns the voltage for the

        Returns a tuple of the following 3 objects:
            V -- float, the measured voltage

            time_stamp -- float, the time at halfway through the averaging
            interval in seconds since the beginning of the epoch (OS
            dependent begin time)

            self.Vdd -- float, the reference voltage.

        :param int chan: the channel number (0, 1, 2, 3)

        :param gain: 2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V),
         4(+/-1.024V), 8 (+/-0.512V), 16 (+/-0.256V))

        :param int data_rate: the ADC sample rate in Hz (8, 16, 32, 64,
         128,250, 475 or 860 Hz). Set to 475 Hz by default.

        :returns: V, time_stamp, self.Vdd
        :return float V:
        :return float time_stamp:
        :return float self.Vdd:
        """
        start = time.time()
        value = self.adc.read_adc(chan, gain=gain, data_rate=data_rate)
        end = time.time()
        time_stamp = (start + end) / 2
        V = value * 4.096 / gain / 32767
        return V, time_stamp, self.Vdd