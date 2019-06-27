# Separate process to read data from an analog to digital converter.
# It buffers the data so that a slow plotting process can run as slowly
# as necessary. The separate process takes advantage of timesliced multitasking
# to get reasonably consistent time spacing between the datapoints even when
# the drawing process gets bogged down.
# J. Gutow <jgutow@new.rr.com> May 19, 2019
# license GPL V3 or greater.

# ADC simulator
try:
    import ADCsim as Demo
    # print(str(Demo.V_oversampchan_stats(1,1,2)))
except (ImportError) as e:
    print(e)

# utilities for timing and queues
from collections import deque
import time

# ADC routinees
try:
    import ADS1115_Utility as ADS1115
except (ImportError) as e:
    print(e)


def DAQProc(whichchn, gains, avgtime, timedelta, DAQconn, DAQCTL, mode='Demo'):
    # f=open('daq.log','w')
    adc = globals()[mode]
    databuf = deque()
    collect = True
    transmit = False
    chncnt = 0
    for i in range(len(whichchn)):
        if (whichchn[i]):
            chncnt += 1
    starttime = time.time()
    while collect:
        pkg = []
        times = []
        values = []
        stdevs = []
        avg_stdevs = []
        for i in range(len(whichchn)):
            if (whichchn[i]):
                time.sleep(0.001)
                # f.write('Calling adc...')
                v_avg, v_std, avg_std, meastime = adc.V_oversampchan_stats(i, gains[i], avgtime)
                # f.write('Successful return from call to adc.\n')
                times.append(meastime - starttime)
                values.append(v_avg)
                stdevs.append(v_std)
                avg_stdevs.append(avg_std)
        pkg.append(times)
        pkg.append(values)
        pkg.append(stdevs)
        pkg.append(avg_stdevs)
        databuf.append(pkg)
        # f.write('Buffer length: '+str(len(databuf))+'\n')
        if DAQCTL.poll():
            CTLmsg = DAQCTL.recv()
            if (CTLmsg == 'Send' or CTLmsg == 'send'):
                transmit = True
            if (CTLmsg == 'Stop' or CTLmsg == 'stop'):
                collect = False
        #   f.write('Received msg: '+str(CTLmsg)+'\n')
        if transmit:  # the other end is ready
            navail = len(databuf)
            nsend = 60
            if (navail <= 60):
                nsend = navail
            for i in range(nsend):
                DAQconn.send(databuf.popleft())
            #  f.write('Sent '+str(nsend)+' buffer chunks.\n')
            transmit = False  # we've done our burst of sending.
        time.sleep(timedelta - 0.002 - (avgtime + 0.0035) * chncnt)
    # We should now send anything left...
    # f.write('Left in buffer: '+str(len(databuf))+'\n')
    while len(databuf) > 1:
        if DAQCTL.poll():
            CTLmsg = DAQCTL.recv()
            if (CTLmsg == 'Send' or CTLmsg == 'send'):
                transmit = True
        if transmit:  # the other end is ready
            navail = len(databuf)
            nsend = 60
            if (navail <= 60):
                nsend = navail
            for i in range(nsend):
                DAQconn.send(databuf.popleft())
            transmit = False  # we've done our burst of sending.
    DAQCTL.send('done')
    # f.write('Cleared buffer. Quitting.\n\n')
    # f.close()
