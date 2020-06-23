# Use os tools for file path and such
import os, logging
import time

# Below allows asynchronous calls to get and plot the data in real time.
# Actually read the DAQ board on a different process.
from multiprocessing import Process, Pipe

from DAQProc import DAQProc
import Boards.boards as boards


def test_DAQProc(nchans, gains, avgtime, timedelta, totaltime):
    # Start Logging
    logname = 'test_DAQProc' + time.strftime('%y-%m-%d_%H%M%S',
                                             time.localtime()) \
              + '.log'
    logging.basicConfig(filename=logname, level=logging.DEBUG)
    availboards = boards.load_boards()
    whichchn = []
    for k in range(nchans):
        thisboard = availboards[0]
        whichchn.append({'board':thisboard,'chnl':k})
    starttime = time.time()
    global data
    data = []
    global timestamp
    timestamp = []
    global stdev
    stdev = []
    PLTconn, DAQconn = Pipe()
    DAQCTL, PLTCTL = Pipe()
    DAQ = Process(target=DAQProc,
                  args=(
                  whichchn, gains, avgtime, timedelta, DAQconn,
                  DAQCTL))
    DAQ.start()


    while (time.time() - starttime) < totaltime:
        while PLTconn.poll():
            pkg = PLTconn.recv()
            lastpkgstr = str(pkg)
            # convert voltage to requested units.
            # for i in range(len(pkg[0])):
            #     avg = pkg[1][i]
            #     std = pkg[2][i]
            #     avg_std = pkg[3][i]
            #     avg, std, avg_std = self.channels[
            #         self.channelmap[i]].toselectedunits(avg, std, avg_std)
            #     avg, std, avg_std = to_reasonable_significant_figures_fast(avg,
            #                                                                std,
            #                                                                avg_std)
            #     pkg[1][i] = avg
            #     pkg[2][i] = std
            #     pkg[3][i] = avg_std
            timestamp.append(pkg[0])
            data.append(pkg[1])
            stdev.append(pkg[2])
        PLTCTL.send('send')
        time.sleep(timedelta)
        pts = len(timestamp)
    PLTCTL.send('stop')
    time.sleep(0.5)  # wait 0.5 second to collect remaining data
    PLTCTL.send('send')
    time.sleep(0.5)
    msg = ''
    while (msg != 'done'):
        while PLTconn.poll():
            pkg = PLTconn.recv()
            # print(str(pkg))
            timestamp.append(pkg[0])
            data.append(pkg[1])
            stdev.append(pkg[2])
        PLTCTL.send('send')
        time.sleep(0.2)
        if PLTCTL.poll():
            msg = PLTCTL.recv()
            # print (str(msg))
            if (msg != 'done'):
                print('Received unexpected message: ' + str(msg))
    print (timestamp)
    print (data)
    print (stdev)
    logging.shutdown()
    try:
        if os.stat(logname).st_size == 0:
            os.remove(logname)
    except FileNotFoundError:
        pass