# Utility sampling routines Vernier LabQuest interfaces.
# Only Analog channels.
# J. Gutow <gutow@uwosh.edu> April 2023
# license GPL V3 or greater
import time
import numpy as np

import logging

try:
    import labquest
    labquestdrvs = True
except Exception as e:
    print("LabQuest: "+str(e))
    labquestdrvs = False

from jupyterpidaq.Boards import Board

logger = logging.getLogger(__name__)

# Optimized for Pi 3B+ for an installed ADS1115 ADC PiHAT. This is
# actually ignored by this board, but necessary for ADC call
# compatibility.
RATE = 10000 #maximum 100 kHz

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
        if LabQuests.open() == 1:
            # Count number of boards
            nboards = len(hDevice)
            # Close things
            LabQuests.close()
            # launch a process to talk to, need Pipes to communicate.
            from multiprocessing import Process, Pipe
            send, cmdrcv = Pipe()
            datasend, rcv = Pipe()
            LQ = Process(target = LQProc,
                         args = (cmdrcv, datasend))
            LQ.start()
            # append an object for each board that knows how to talk to the
            # process and get information from that particular device
            for addr in range(nboards):
                # TODO what to pass to each Board_LQ
                boards.append(Board_LQ(addr, send, rcv))
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

        :param int data_rate: maximum?

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
        LabQuests = self.labquest.LabQuest()
        LabQuests.open()
        read = ['no_sensor', 'no_sensor', 'no_sensor']
        read[chan - 1] = 'raw_voltage'
        nsamples = round(avg_sec*data_rate)
        period = 1000/data_rate
        LabQuests.select_sensors(ch1=read[0], ch2=read[1],
                                 ch3=read[2], device=self.addr)
        starttime = time.time()
        self.LabQuests.start(period)
        value = self.LabQuests.read_multi_pt('ch'+str(chan), nsamples, self.addr)
        endtime = starttime + avg_sec
        self.LabQuests.stop()
        time_stamp = (starttime + endtime) / 2
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
        read = ['no_sensor', 'no_sensor', 'no_sensor']
        read[chan - 1] = 'raw_voltage'
        nsamples = round(avg_sec * data_rate)
        period = 1000 / data_rate
        self.LabQuests.select_sensors(ch1=read[0], ch2=read[1],
                                 ch3=read[2], device=self.addr)
        starttime = time.time()
        self.LabQuests.start(period)
        value = self.LabQuests.read_multi_pt('ch'+str(chan), nsamples, self.addr)
        endtime = starttime + avg_sec
        self.LabQuests.stop()
        time_stamp = (starttime + endtime) / 2
        ndata = len(value)
        logging.debug('channel:'+str(chan)+', starttime:'+str(starttime)+', '
                      'endtime:'+str(endtime)+', ndata:'+str(ndata)+'.')
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

        :return float ref:
        '''
        read = ['no_sensor', 'no_sensor', 'no_sensor']
        read[chan - 1] = 'raw_voltage'
        period = 1000 / data_rate
        self.LabQuests.select_sensors(ch1=read[0], ch2=read[1],
                                 ch3=read[2], device=self.addr)
        starttime = time.time()
        self.LabQuests.start(period)
        value = self.LabQuests.read('ch' + str(chan), self.addr)
        endtime = time.time()
        self.LabQuests.stop()
        time_stamp = (starttime + endtime) / 2
        ref = 5.00
        return value, time_stamp, ref

def LQProc(cmdrcv, datasend):
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
    if lqs.open() == 1:
        # we're good to go
        # make a list of boards with a deque for each the channel voltages
        # in each board list (e.g. deque channel X, where X = 1, 2 or 3,
        # of board 0 accessed as `boards[0][X-1]`).
        boards = []
        nboards = len(labquest.config.hDevice)
        for i in range(nboards):
            boards.append([])
            # Tell the board we will monitor all three channels
            lqs.select_sensors(ch1="raw_voltage", ch2="raw_voltage",
                               ch3="raw_voltage",
                               device=i)
            for k in range(3):
                # deque with max 200000 data points allowing 2 second buffer
                # at max collection rate of 100 kHz.
                boards[i].append(deque(maxlen=200000))
        lqs.start(0.01)
        running = True
        while running:
            # TODO use existing buffers and read from them as
            #  commands come in.
            # TODO need to clear the buffer at beginning of run to
            #  have good time zero.
            # check for a command
            # send requested data
        lqs.close()
        return
    else:
        # something happened
        lqs.close()
        raise IOError("")
    return