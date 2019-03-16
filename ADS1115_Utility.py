#Utility sampling routines for using the ADS1115 ADC RPI HAT.
# J. Gutow <jgutow@new.rr.com> Nov. 12, 2018
# license GPL V3 or greater
import time
import numpy as np
import Adafruit_ADS1x15
# Optimized for Pi 3B+
RATE = 475 # 475 Hz with oversampling best S/N on Pi 3B+ per unit time interval.
           # other rates 8, 16, 32, 64, 128, 250, 475, 860 in Hz.

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()           

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
'''
V,time_stamp=V_sampchan(0, 2)
print ('Single read time: '+str(time.localtime(time_stamp))+' Voltage: '+str(V))
V_avg,V_min, V_max, time_stamp =V_oversampchan(0, 2, 2)
valueR = V_avg*2.20e3/(3.30-V_avg)
valueC = (valueR - 1023.537)/3.85
valueF = 9*valueC/5 + 32
print ('Time: '+str(time.localtime(time_stamp)))
print ('Average deg C: '+str(valueC)+' Averge deg F: '+str(valueF))
valueR = V_min*2.20e3/(3.30-V_min)
valueC = (valueR - 1023.537)/3.85
valueF = 9*valueC/5 + 32
print ('Min deg C: '+str(valueC)+' Min deg F: '+str(valueF))
valueR = V_max*2.20e3/(3.30-V_min)
valueC = (valueR - 1023.537)/3.85
valueF = 9*valueC/5 + 32
print ('Max deg C: '+str(valueC)+' Max deg F: '+str(valueF))
print ('Avg time of 0.05 sec: '+str(V_oversampchan(0,2,0.05)))
print ('Avg time of 1 sec: '+str(V_oversampchan(0,2,1)))
print ('Avg time of 2 sec: '+str(V_oversampchan(0,2,2)))
print ('Avg time of 4 sec: '+str(V_oversampchan(0,2,4)))
print ('Avg time of 8 sec: '+str(V_oversampchan(0,2,8)))
'''