# Separate process to read data from an analog to digital converter.
# It buffers the data so that a slow plotting process can run as slowly
# as necessary. The separate process takes advantage of timesliced multitasking
# to get reasonably consistent time spacing between the datapoints even when
# the drawing process gets bogged down.
# J. Gutow <gutow@uwosh.edu> May 19, 2019
# license GPL V3 or greater.

# utilities for timing and queues
from collections import deque
import time

def DAQProc(whichchn, gains, avgtime, timedelta, DAQconn, DAQCTL):
    """
    This function is to be run in a separate thread to asynchronously
    communicate with the ADC board.

    :param list whichchn: a list of dictionaries. Each dictionary is of the
     form:{'board': board_object, 'chnl': chnlID}.

    :param list gains: a list of the numerical gain for each channel.

    :param float avgtime: the averaging time in seconds for a data point.

    :param float timedelta: the target time between data points.

    :param pipe DAQconn: the connection pipe

    :param pipe DAQCTL: the control pipe

    :return: Data is returned via the pipes.
        On the DAQCTL pipe this only returns 'done'
        On the DAQconn pipe a list of lists with data is returned.
    """
    # f=open('daq.log','w')
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
        avg_vdds = []
        calltime = time.time()
        for i in range(len(whichchn)):
            if (whichchn[i]):
                time.sleep(0.001)
                # f.write('Calling adc...')
                v_avg, v_std, avg_std, meastime, vdd_avg = \
                    whichchn[i]['board'].V_oversampchan_stats(whichchn[i][
                                                                   'chnl'],
                                                              gains[i],
                                                           avgtime)
                # f.write('Successful return from call to adc.\n')
                times.append(meastime - starttime)
                values.append(v_avg)
                stdevs.append(v_std)
                avg_stdevs.append(avg_std)
                avg_vdds.append(vdd_avg)
        pkg.append(times)
        pkg.append(values)
        pkg.append(stdevs)
        pkg.append(avg_stdevs)
        pkg.append(avg_vdds)
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
        elapsedtime = time.time() - calltime
        if elapsedtime < timedelta:
            time.sleep(timedelta -elapsedtime- 0.002)
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
