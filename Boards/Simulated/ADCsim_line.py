# Noisy line substitute for actual analog to digital converter.
# Used to allow a 'demo' mode for JupyterPiDAQ.
# J. Gutow <jgutow@new.rr.com> June 11, 2020
# license GPL V3 or greater

import time

from numpy import around
from numpy import float64
from numpy import floor
from numpy import log10
from numpy import random
from numpy import sqrt
from numpy import std

from Boards.boards import Board

# mimicking an installed ADS1115 ADC PiHAT.
RATE = 475  # 475 Hz with oversampling best S/N on Pi 3B+ per unit time interval.


# other rates 8, 16, 32, 64, 128, 250, 475, 860 in Hz.
def find_boards():
    return Board_ADCsim_line('placeholder')


class Board_ADCsim_line(Board):
    def __init__(self, adc):
        super().__init__()
        self.name = 'ADCsym Line'
        self.vendor = 'JupyterPiDAQ'
        self.channels = (0, 1, 2, 3)
        self.gains = [1]
        self.Vdd = 3.3
        self.adc = adc

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
        """
        This routine returns the average voltage for the channel
        averaged at (0.0012 + 1/data_rate)^-1 Hz for avg_sec
        number of seconds. The 0.0012 is the required loop time
        on a RPI 3B+ in python3. The voltage is rounded to the number
        of decimals indicated by the standard deviation. The standard
        deviation and the estimated deviation of the mean are also
        returned.
        Parameters
            chan    the channel number 0, 1, 2, 3
            gain    2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V), 4(+/-1.024V),
                    8 (+/-0.512V), 16 (+/-0.256V)
            data_rate the ADC sample rate in Hz (8, 16, 32, 64, 128, 250, 475 or 860 Hz)
            avg_sec seconds to average for, actual averaging interval will be as close
                    as possible for an integer number of samples.
        Returns a tuple (V_avg, V_min, V_max, time_stamp)
            V_avg   the averaged voltage
            stdev   estimated standard deviation of the measurements
            stdev_avg   estimated standard deviation of the mean
            time_stamp the time at halfway through the averaging interval in seconds
                    since the beginning of the epoch (OS dependent begin time).

        """
        time_tuple = time.localtime()
        nearesthr = time.mktime((time_tuple.tm_year, time_tuple.tm_mon,
                                 time_tuple.tm_mday, time_tuple.tm_hour, 0, 0,
                                 time_tuple.tm_wday, time_tuple.tm_yday,
                                 time_tuple.tm_isdst))
        n_samp = int(round(avg_sec / (0.0017 + 1 / data_rate)))
        if (n_samp < 1):
            n_samp = 1
        value = []
        start = time.time()
        intercept = (time.time() - nearesthr) / 1800
        slope = (time.time() - nearesthr) / 692000
        for k in range(n_samp):
            tempval = intercept + slope * (time.time() - nearesthr) + (
                    random.random() - 0.5) * slope
            value.append(tempval)
        end = time.time()
        time_stamp = (start + end) / 2.0
        V_avg = sum(value) / len(value) / gain
        V_max = max(value)
        V_min = min(value)
        return V_avg, V_min, V_max, time_stamp, self.Vdd

    def V_oversampchan_stats(self, chan, gain, avg_sec, data_rate=RATE):
        '''
        This routine returns the average voltage for the channel
        averaged at (0.0012 + 1/data_rate)^-1 Hz for avg_sec
        number of seconds. The 0.0012 is the required loop time
        on a RPI 3B+ in python3. The voltage is rounded to the number
        of decimals indicated by the standard deviation. The standard
        deviation and the estimated deviation of the mean are also
        returned.
        Parameters
            chan    the channel number 0, 1, 2, 3
            gain    2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V), 4(+/-1.024V),
                    8 (+/-0.512V), 16 (+/-0.256V)
            data_rate the ADC sample rate in Hz (8, 16, 32, 64, 128, 250, 475 or 860 Hz)
            avg_sec seconds to average for, actual averaging interval will be as close
                    as possible for an integer number of samples.
        Returns a tuple (V_avg, V_min, V_max, time_stamp)
            V_avg   the averaged voltage
            stdev   estimated standard deviation of the measurements
            stdev_avg   estimated standard deviation of the mean
            time_stamp the time at halfway through the averaging interval in seconds
                    since the beginning of the epoch (OS dependent begin time).

        '''
        time_tuple = time.localtime()
        nearesthr = time.mktime((time_tuple.tm_year, time_tuple.tm_mon,
                                 time_tuple.tm_mday, time_tuple.tm_hour, 0, 0,
                                 time_tuple.tm_wday, time_tuple.tm_yday,
                                 time_tuple.tm_isdst))
        n_samp = int(round(avg_sec / (0.0017 + 1 / data_rate)))
        if (n_samp < 1):
            n_samp = 1
        value = []
        start = time.time()
        intercept = (time.time() - nearesthr) / 1800
        slope = (time.time() - nearesthr) / 692000
        for k in range(n_samp):
            tempval = intercept + slope * (time.time() - nearesthr) + (
                    random.random() - 0.5) * slope
            value.append(tempval)
        end = time.time()
        time_stamp = (start + end) / 2
        V_avg = sum(value) / len(value) / gain
        stdev = std(value, ddof=1, dtype=float64) / gain
        stdev_avg = stdev / sqrt(float(len(value)))
        decimals = 0
        if (stdev_avg == 0):
            decimals = 6
        else:
            if (stdev_avg != float('inf')) and (stdev_avg > 0):
                decimals = -int(floor(log10(stdev_avg)))
        # print('decimals = '+str(decimals))
        V_avg = around(V_avg, decimals=decimals)
        stdev = around(stdev, decimals=decimals)
        stdev_avg = around(stdev_avg, decimals=decimals)
        return V_avg, stdev, stdev_avg, time_stamp, self.Vdd

    def V_sampchan(self, chan, gain, data_rate=RATE):
        '''
        This routine returns the average voltage for the channel
        averaged at (0.0012 + 1/data_rate)^-1 Hz for avg_sec
        number of seconds. The 0.0012 is the required loop time
        on a RPI 3B+ in python3. The voltage is rounded to the number
        of decimals indicated by the standard deviation. The standard
        deviation and the estimated deviation of the mean are also
        returned.
        Parameters
            chan    the channel number 0, 1, 2, 3
            gain    2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V), 4(+/-1.024V),
                    8 (+/-0.512V), 16 (+/-0.256V)
            data_rate the ADC sample rate in Hz (8, 16, 32, 64, 128, 250, 475 or 860 Hz)
            avg_sec seconds to average for, actual averaging interval will be as close
                    as possible for an integer number of samples.
        Returns a tuple (V_avg, V_min, V_max, time_stamp)
            V_avg   the averaged voltage
            stdev   estimated standard deviation of the measurements
            stdev_avg   estimated standard deviation of the mean
            time_stamp the time at halfway through the averaging interval in seconds
                    since the beginning of the epoch (OS dependent begin time).

        '''
        time_tuple = time.localtime()
        nearesthr = time.mktime((time_tuple.tm_year, time_tuple.tm_mon,
                                 time_tuple.tm_mday, time_tuple.tm_hour, 0, 0,
                                 time_tuple.tm_wday, time_tuple.tm_yday,
                                 time_tuple.tm_isdst))
        start = time.time()
        intercept = (time.time() - nearesthr) / 1800
        slope = (time.time() - nearesthr) / 692000
        V = intercept + slope * (time.time() - nearesthr) + (random.random()
                                                             - 0.5) * slope
        end = time.time()
        time_stamp = (start + end) / 2.0
        return V, time_stamp, self.Vdd
