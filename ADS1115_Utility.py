#Utility sampling routines for using the ADS1115 ADC RPI HAT.
# J. Gutow <jgutow@new.rr.com> Nov. 12, 2018
# license GPL V3 or greater
import time
import numpy as np
#We may be running on a machine with out a functional analog to digital converter.
class dummyClass(): #dummy routine(s) if the adc routines cannot be loaded.
    def __init__(self):
        pass
    def read_adc(self,chan,gain, data_rate):
        return(1.00) #should never get called
adc=None
try:
    import Adafruit_ADS1x15
    # Create an ADS1115 ADC (16-bit) instance.
    adc = Adafruit_ADS1x15.ADS1115()           
except ImportError:
    adc=dummyClass()
    warnstr='Warning: No analog to digital converter driver found. Using dummy '
    warnstr+='function to allow loading. Code should use alternative Demo function.'
    print(warnstr)
# Optimized for Pi 3B+
RATE = 475 # 475 Hz with oversampling best S/N on Pi 3B+ per unit time interval.
           # other rates 8, 16, 32, 64, 128, 250, 475, 860 in Hz.

def V_oversampchan(chan, gain, avg_sec, data_rate = RATE):
    '''
    This routine returns the average voltage for the channel
    averaged at (0.0012 + 1/data_rate)^-1 Hz for avg_sec
    number of seconds. The 0.0012 is the required loop time
    on a RPI 3B+ in python.
    TODO: a more sophisticated initialization, which determines
    the loop time.
    Parameters
        chan    the channel number 0, 1, 2, 3
        gain    2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V), 4(+/-1.024V),
                8 (+/-0.512V), 16 (+/-0.256V)
        data_rate the ADC sample rate in Hz (8, 16, 32, 64, 128, 250, 475 or 860 Hz)
        avg_sec seconds to average for, actual averaging interval will be as close
                as possible for an integer number of samples.
    Returns a tuple (V_avg, V_min, V_max, time_stamp)
        V_avg   the averaged voltage
        V_min   the minimum voltage read during the interval
        V_max   the maximum voltage read during the interval
        time_stamp the time at halfway through the averaging interval in seconds
                since the beginning of the epoch (OS dependent begin time).
        
    '''
    n_samp = int(round(avg_sec/(0.0012+1/data_rate)))
    value = [0]*n_samp
    avgmax = adc.read_adc(chan,gain=gain, data_rate = data_rate)
    avgmin = avgmax
    start = time.time()
    for k in range(n_samp):
        value[k]= adc.read_adc(chan,gain=gain, data_rate = data_rate)
    end = time.time()
    time_stamp = (start+end)/2
    V_avg = sum(value)*4.096/n_samp/gain/32767
    V_min = min(value)*4.096/gain/32767
    V_max = max(value)*4.096/gain/32767
    return (V_avg, V_min, V_max, time_stamp)

def V_oversampchan_stats(chan, gain, avg_sec, data_rate = RATE):
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
    n_samp = int(round(avg_sec/(0.0017+1/data_rate)))
    if (n_samp < 1):
        n_samp=1
    value = []
    start = 0
    end = 0
    while (len(value)==0): # we will try until we get some values in case of bad reads
        start = time.time()
        for k in range(n_samp):
            try:
                tempval = adc.read_adc(chan,gain=gain, data_rate = data_rate)
            except (ValueError,OverflowError):
                print('Bad adc read.')
                pass
            else:
                if (tempval >=-32767) and (tempval <=32767):
                    value.append(tempval)
            #time.sleep(0.0005)
        end = time.time()
    time_stamp = (start+end)/2
    V_avg = sum(value)*4.096/len(value)/gain/32767
    stdev = np.std(value,ddof=1,dtype=np.float64)*4.096/gain/32767
    stdev_avg = stdev/np.sqrt(float(len(value)))
    decimals = 0
    if (stdev_avg==0):
        decimals=6
    else:
        if (stdev_avg!=float('inf')) and (stdev_avg >0):
            decimals = -int(np.floor(np.log10(stdev_avg)))
    V_avg = np.around(V_avg,decimals=decimals)
    stdev= np.around(stdev,decimals=decimals)
    stdev_avg=np.around(stdev_avg,decimals=decimals)
    return (V_avg, stdev, stdev_avg, time_stamp)

def V_sampchan(chan, gain, data_rate = RATE):
    '''
    This routine returns the voltage for the channel
    Parameters
        chan    the channel number 0, 1, 2, 3
        gain    2/3 (+/-6.144V), 1(+/-4.096V), 2(+/-2.048V), 4(+/-1.024V),
                8 (+/-0.512V), 16 (+/-0.256V)
        data_rate the ADC sample rate in Hz (8, 16, 32, 64, 128, 250, 475 or 860 Hz)
    Returns a tuple (V, time_stamp)
        V       the voltage
        time_stamp the time at halfway through the averaging interval in seconds
                since the beginning of the epoch (OS dependent begin time).
        
    '''
    start = time.time()
    value= adc.read_adc(chan,gain=gain, data_rate = data_rate)
    end = time.time()
    time_stamp = (start+end)/2
    V = value*4.096/gain/32767
    return (V, time_stamp)