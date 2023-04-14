# Utility sampling routines Vernier LabQuest interfaces.
# Only Analog channels.
# J. Gutow <gutow@uwosh.edu> April 2023
# license GPL V3 or greater
import time
import numpy as np
from multiprocessing import Lock, Value

import logging

try:
    import labquest
    labquestdrvs = True
    starttime = Value('d',time.time())
    samples = []
    for k in range(3):
        samples.append(Value('i',0))
except Exception as e:
    print("LabQuest: "+str(e))
    labquestdrvs = False

from jupyterpidaq.Boards import Board

logger = logging.getLogger(__name__)

# Optimized for Pi 3B+ for an installed ADS1115 ADC PiHAT. This is
# actually ignored by this board, but necessary for ADC call
# compatibility.
RATE = 10000 #maximum 10 kHz

def find_boards():
    """
    A rountine like this must be implemented by all board packages.

    :return: list of LabQuests (Types too?)
    """
    boards = []
    # The following is a hack to get around the fact that the whole module
    # needs to be reinstantiated on the new thread. I think the best option
    # is to upon discovery spawn a process and then just communicate with it.
    if labquestdrvs:
        LabQuests = labquest.LabQuest()
        if LabQuests.open() == 0:
            # Count number of boards
            nboards = len(labquest.config.hDevice)
            # Close things
            LabQuests.close()
            # launch a process to talk to, need Pipes to communicate.
            from multiprocessing import Process, Pipe
            cmdsend, cmdrcv = Pipe()
            datasend, datarcv = Pipe()
            LQ = Process(target = LQProc,
                         args = (cmdrcv, datasend, starttime, samples))
            LQ.start()
            # append an object for each board that knows how to talk to the
            # process and get information from that particular device
            addr = 0
            for addr in range(nboards):
                # TODO what to pass to each Board_LQ
                boards.append(Board_LQ(addr, cmdsend, datarcv))
                addr+=1
    return boards

class Board_LQ(Board):
    """
    Class defining the properties of the analog-to-digital block of the
    LabQuests. Key characteristics:

    * 3 channels (1, 2, 3) a range of +/- 10 V.
    * 12 bit resolution
    * Other available but not implemented facilities are Digital I/O.
    """
    def __init__(self, addr, send, rcv):
        super().__init__()
        self.name = 'LabQuest'
        self.vendor = 'Vernier'
        self.channels = (1, 2, 3)
        self.addr = addr
        self.send = send
        self.rcv = rcv
        self.Vdd = 5.00
        # samples taken from a channel and starttime kept track of in
        #  shared memory samples[i].value = # of samples taken from channel
        #   i. starttime.value = time.time() immediately after las clearing
        #   of the buffers.

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

        :param int chan: the channel number (1, 2, 3)

        :param gain: ignored by board. Defaults to 1.

        :param int data_rate: maximum

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
        nsamples = round(data_rate*avg_sec)
        self.send.send(['send',self.addr, chan, nsamples])
        while not self.rcv.poll():
            #we wait for data
            pass
        value = self.rcv.recv()
        samples[chan - 1].value = samples[chan - 1].value + nsamples
        endtime = starttime.value + samples[chan-1].value/data_rate
        time_stamp = endtime - avg_sec / 2
        ndata = len(value)
        V_avg = sum(value) / ndata
        Vdd_avg = 5.00
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

            Vdd_avg -- float, returned as None.

        :param int chan: the channel number (1, 2, 3)

        :param gain: ignored by board. Defaults to 1.

        :param int data_rate:

        :param float avg_sec: seconds to average for, actual
         averaging interval will be as close as possible for an integer
         number of samples

        :returns: V_avg, stdev, stdev_avg, time_stamp, Vdd_avg
        :return float V_avg:
        :return float stdev:
        :return float stdev_avg:
        :return float time_stamp:
        :return float Vdd_avg:
        '''
        nsamples = round(data_rate * avg_sec)
        self.send.send(['send', self.addr, chan, nsamples])
        while  not self.rcv.poll():
            # we wait for data
            pass
        value = self.rcv.recv()
        samples[chan - 1].value = samples[chan - 1].value + nsamples
        endtime = starttime.value + samples[chan-1].value/data_rate
        time_stamp = endtime - avg_sec / 2
        ndata = len(value)
        V_avg = sum(value) / ndata
        Vdd_avg = 5.00
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

        :param int chan: the channel number (1, 2, 3).

        :param gain: ignored by board. Defaults to 1.

        :param int data_rate:

        :returns float value:

        :return float time_stamp:

        :return float Vdd:
        '''
        nsamples = 1
        self.send.send(['start', ])
        self.send.send(['send', self.addr, chan, nsamples])
        while not self.rcv.poll():
            # we wait for data
            pass
        value = self.rcv.recv()[0]
        samples[chan - 1].value = samples[chan - 1].value + nsamples
        time_stamp = starttime.value
        Vdd = 5.00
        return value, time_stamp, Vdd

def LQProc(cmdrcv, datasend, starttime, samples):
    """Process to spawn that continuously collects from the LabQuests(s)
    Parameters
    ----------
    cmdrcv: Pipe
        Where commands are received.

    datasend: Pipe
        Where data is sent in response to a command.
    """
    # First set up the LabQuest(s)
    import labquest
    from collections import deque
    lqs = labquest.LabQuest()
    cmd_deque = deque()
    PERIOD = 1000/RATE # msec
    if lqs.open() == 0:
        # we're good to go
        # make a list of boards
        boards = []
        nboards = len(labquest.config.hDevice)
        for i in range(nboards):
            # Tell the board we will monitor all three channels
            lqs.select_sensors(ch1="raw_voltage", ch2="raw_voltage",
                               ch3="raw_voltage",
                               device=i)
        lqs.start(PERIOD)
        starttime.value = time.time()
        running = True
        while running:
            # check for a command: start (clears buffers), send (sends content
            # of buffers, removing the sent content), close (shutdown the process).
            # Each command is a list ['cmd str',<cmd data>]:
            #    ['start',]
            #    ['close',]
            #    ['send',board#, ch#, num_pts].
            while cmdrcv.poll():
                cmd_deque.append(cmdrcv.recv())
            # Start responding to commands
            while len(cmd_deque) > 0:
                cmd = cmd_deque.popleft()
                if cmd[0] == 'close':
                    # stop thread
                    running = False
                if cmd[0] == 'start':
                    # restart data collection to get good zero
                    #lqs.stop()
                    #lqs.start(PERIOD)
                    print("Reached start.")
                    labquest.buf.buffer_clear()
                    now = time.time()
                    starttime.value = now
                    for k in range(3):
                        samples[k].value = 0
                    print("  Time should set to: "+str(now))
                if cmd[0] == 'send':
                    # return requested amount of data for the channel
                    chan = 'ch'+str(cmd[2])
                    data = lqs.read_multi_pt(chan,cmd[3],device=cmd[1])
                    datasend.send(data)
        lqs.close()
        return
    else:
        # something happened
        lqs.close()
        raise IOError("")
    return