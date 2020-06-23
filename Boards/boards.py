"""
This file handles loading adc board control software and sensor information.
It uses the list of known boards. It will skip boards that produce an error
either because the pypi package is not installed or an error occurs when
trying to communicate with the board.

The ADC simulator will be installed if no boards are available.
"""
from importlib import import_module
import logging

logger = logging.getLogger(__name__)

# TODO: Update this list of available board options as they are created.
# Name format is `.package.boardname` where `boardname` is the name of the
# python file defining the required board operations.

knownboardpkgs = ('.PiGPIO.ADS1115', '.PiGPIO.DAQC2')
knownsimulators = ('.Simulated.ADCsim', '.Simulated.ADCsim_line')


def load_boards():
    """
    Uses the list of known board packages to search for available boards.
    The file <boardname>.py should at minimum
    implement a `find_boards(): routine that overrides the function below and
    define a class for the particular board that extends the `Board` class
    defined below.

    :return: list of adc board objects.
    """
    # Load available board driver packages
    boardpkgs = []
    for pkg in knownboardpkgs:
        tmpmod = None
        try:
            tmpmod = import_module('Boards'+pkg)
        except ImportError as e:
            logger.debug(e)
            tmpmod = None
        if (tmpmod):
            boardpkgs.append(tmpmod)

    # Check for available boards
    boards = []
    if len(boardpkgs) >= 1:
        # All board pkgs must implement `find_boards().
        for drv in boardpkgs:
            avail = drv.find_boards()
            for hdw in avail:
                boards.append(hdw)
    if len(boards) == 0:
        # We found no boards
        print('No ADC boards found. Using simulated boards...')
        boards = _load_simulators()
    return boards

def find_boards():
    """
    A function overriding this must be implemented by all board packages.
    See examples of working packages and the pretend example below.

    :return: list of board objects
    """
    # POSS_ADDR = (0x48, 0x49, 0x4A, 0x4B)
    # boards = []
    # tmpmod = None
    # for addr in POSS_ADDR:
    #     try:
    #         tmpmod = pkgname.tstcall(addr)
    #     except RuntimeError as e:
    #         logger.debug(e)
    #         tmpmod = None
    #     if tmpmod:
    #         boards.append(tmpmod)
    # return boards
    raise NotImplementedError

def _load_simulators():
    """
    Private function to add simulated ADC boards
    :return:
    boards  list of adc board objects.
    """
    simpkgs = []
    boards = []
    tmpmod = None
    for sim in knownsimulators:
        try:
            tmpmod = import_module('Boards'+sim)
        except ImportError as e:
            logger.debug(e)
            tmpmod = None
        if (tmpmod):
            simpkgs.append(tmpmod)
        logging.log(logging.DEBUG,str(simpkgs))
    if len(simpkgs) >= 1:
        # All board pkgs must implement `find_boards().
        for drv in simpkgs:
            avail = drv.find_boards()
            logging.log(logging.DEBUG,str(avail))
            if avail:
                boards.append(avail)
    return boards


class Board:
    """
    Base class for all boards. Each board should be an extension of this class.
    """
    def __init__(self):
        """
        Should be overridden by each board and define at minimum:
        self.name = 'board name/adc name/type' Short an useful to end user
        self.vendor = 'Vendor/Manufacturer name`
        self.channels = tuple of available channel IDs
        self.Vdd = voltage provided by board to sensors
        """
        self.name = None
        self.vendor = None
        self.channels = None
        self.Vdd = None

    def getname(self):
        """
        :return: string value of the board name, a short label of board type.
        """
        return self.name

    def getchannels(self):
        """
        :return: tuple of ids for available channels
        """
        return self.channels

    def getvendor(self):
        """
        :return: string value of the vendor name
        """
        return self.vendor

    def getVdd(self):
        """
        :return: numerical value of the Vdd, voltage provided to sensors
        """
        return self.Vdd

    def getsensors(self):
        """
        This returns a list of objects that allow the software to translate
        the measured voltage into a sensor reading in appropriate units.
        Must be provided by the specific board implementation.
        :return: A list of valid sensor objects to use with this board. This
        should be a subset of all the sensors returned by the listSensors
        function in sensors.py.
        """
        raise NotImplementedError

    def V_oversampchan(self, chan, gain, avg_sec, **kwargs):
        """
        This function should return a tuple with average, minimum and maximum
        for a channel averaged over the period of time avg_sec. How the
        averaging is performed will depend on the board.
        :param chan: id of the channel to be measured
        :param gain: gain of the channel if adjustable
        :param avg_sec: float period of time over which to average
        :return: a tuple consisting of V_avg, V_min, V_max, time_stamp
            The time_stamp is the time the data was collected, usually the
            middle of the averaging period.
        """
        raise NotImplementedError

    def V_oversampchan_stats(self, chan, gain, avg_sec, **kwargs):
        """
        This function should return a tuple of statistical information for a
        channel averaged over the period of time avg_sec.
        :param chan: id of the channel to be measured
        :param gain: gain of the channel if adjustable
        :param avg_sec: float period of time over which to average
        :return: tuple consisting of V_avg, stdev, stdev_avg, time_stamp,
        where stdev_avg is the estimated standard deviation of the average
        not the standard deviation of the values sampled (stdev).
        """
        raise NotImplementedError

    def V_sampchan(self, chan, gain, **kwargs):
        """
        This function returns a single measurement and the time it was
        collected.
        :param chan: id of the channel to be measured
        :param gain: gain of the channel if adjustable
        :return: a tuple consisting of V, time_stamp, where V = the single
        voltage measurement and time_stamp the time it was collected.
        """
        raise NotImplementedError
