# Random number generator substitute for actual analog to digital converter.
# Used to allow a 'demo' mode for JupyterPiDAQ.
# J. Gutow <jgutow@new.rr.com> March 16, 2019
# license GPL V3 or greater

from numpy import random
from numpy import std
from numpy import sqrt
from numpy import around
from numpy import float64
from numpy import log10
from numpy import floor
import time

# Optimized for Pi 3B+ mimicking an installed ADS1115 ADC PiHAT.
RATE = 475  # 475 Hz with oversampling best S/N on Pi 3B+ per unit time interval.


# other rates 8, 16, 32, 64, 128, 250, 475, 860 in Hz.

def V_oversampchan_stats(chan, gain, avg_sec, data_rate=RATE):
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
    n_samp = int(round(avg_sec / (0.0017 + 1 / data_rate)))
    if (n_samp < 1):
        n_samp = 1
    value = []
    start = 0
    end = 0
    while (len(value) == 0):  # we will try until we get some values in case of bad reads
        start = time.time()
        center = random.random()
        for k in range(n_samp):
            try:
                tempval = round((random.normal(center, center / 10)) * 32767)
                # positive only to avoid problems mimicking some sensors
                #if (tempval<0):
                 #   tempval = -1*tempval
                #if (tempval == 0):
                 #   tempval=1
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
    stdev = std(value, ddof=1, dtype=float64) * 4.096 / gain / 32767
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
    return (V_avg, stdev, stdev_avg, time_stamp)
