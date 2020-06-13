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

# TODO: Update this list of available options as they are created.
knownboardpkgs = ('JPhysSciLab-board-ADS115',
                  'JPhysSciLab-board-DACQ2')
knownsimulators = ('ADCsim', 'ADCsim_line')

def load_boards():
    """

    :return:
    boards   list of adc board objects.
    """
    # Load available board driver packages
    boardpkgs = []
    for pkg in knownboardpkgs:
        tmpmod = None
        try:
            tmpmod = import_module(pkg)
        except ImportError as e:
            logger.debug(e)
            tmpmod = None
        if (tmpmod):
            boardpkgs.append(tmpmod)

    # Check for available boards
    boards = []
    if len(boardpkgs) >= 1:
    # TODO: call routine that searches for each type of board and returns
    #  every active board as an object.
        if len(boards) == 0:
            # We found no boards
            print ('No ADC boards found. Using simulated boards...')
            boards = _load_simulators()
    else:
        # No board driver packages so load simulators and return.
        print('No ADC boards found. Using simulated boards...')
        boards = _load_simulators()
    return boards

def _load_simulators():
    """
    Private function to add simulated ADC boards
    :return:
    boards  list of adc board objects.
    """
    boards = []
    tmpmod = None
    for sim in knownsimulators:
        try:
            tmpmod = import_module(sim)
        except ImportError as e:
            logger.debug(e)
            tmpmod = None
        if (tmpmod):
            boards.append(tmpmod)
    return boards