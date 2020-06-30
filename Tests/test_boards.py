from Boards import boards
from Sensors import sensors


def test_load_boards():
    # test all functionality of board loading and
    # all functionality of each board that is loaded
    # on this machine.
    availboards = boards.load_boards()
    assert (len(availboards) > 0)
    for board in availboards:
        # Basic board class attributes
        assert (isinstance(board, boards.Board))
        assert (isinstance(board.name, str))
        assert (isinstance(board.vendor, str))
        assert (isinstance(board.channels, tuple))
        assert (isinstance(board.gains, list))
        assert (isinstance(board.Vdd, float))
        assert (board.getname() == board.name)
        assert (board.getvendor() == board.vendor)
        assert (board.getchannels() == board.channels)
        assert (board.getgains() == board.gains)
        assert (board.getVdd() == board.Vdd)
        # Check for valid sensors
        availsensors = board.getsensors()
        assert (isinstance(availsensors, list))
        for sensor in availsensors:
            assert (hasattr(sensors, sensor))
        # Check board functionality
        for chan in board.getchannels():
            for gain in board.getgains():
                assert (len(board.V_oversampchan(chan, gain, 0.2)) == 5)
                for k in range(0,3):
                    assert (isinstance(board.V_oversampchan(chan, gain,
                                                            0.2)[k], float))
                # max value should be greater than minimum
                measurement = board.V_oversampchan(chan, gain, 0.2)
                assert (measurement[1] < measurement[2])
                assert (len(board.V_oversampchan_stats(chan, gain, 0.2)) == 5)
                for k in range(0,3):
                    assert (isinstance(board.V_oversampchan_stats(chan, gain,
                                                                  0.2)[k],
                                       float))
                # average should have a lower standard deviation than
                # the values used to get the average.
                measurement = board.V_oversampchan_stats(chan, gain, 0.2)
                assert (measurement[2] < measurement[1])
                assert (len(board.V_sampchan(chan, gain)) == 3)
                for k in range(0,1):
                    assert (isinstance(board.V_sampchan(chan, gain)[k], float))
    pass


def test_board_drivers():
    # TODO: test functionality of board drivers that can be tested
    #  without a board actually being available.
    pass


def test_sim_boards():
    # test all functionality of simulated boards and loading
    # them.
    availboards = boards._load_simulators()
    assert (len(availboards) > 0)
    for board in availboards:
        # Basic board class attributes
        assert (isinstance(board, boards.Board))
        assert (isinstance(board.name, str))
        assert (isinstance(board.vendor, str))
        assert (isinstance(board.channels, tuple))
        assert (isinstance(board.gains, list))
        assert (isinstance(board.Vdd, float))
        assert (board.getname() == board.name)
        assert (board.getvendor() == board.vendor)
        assert (board.getchannels() == board.channels)
        assert (board.getgains() == board.gains)
        assert (board.getVdd() == board.Vdd)
        # Check for valid sensors
        availsensors = board.getsensors()
        assert (isinstance(availsensors, list))
        for sensor in availsensors:
            assert (hasattr(sensors, sensor))
        # Check board functionality
        for chan in board.getchannels():
            for gain in board.getgains():
                assert (len(board.V_oversampchan(chan, gain, 0.2)) == 5)
                for k in range(0,3):
                    assert (isinstance(board.V_oversampchan(chan, gain,
                                                            0.2)[k], float))
                # max value should be greater than minimum
                measurement = board.V_oversampchan(chan, gain, 0.2)
                assert (measurement[1] < measurement[2])
                assert (len(board.V_oversampchan_stats(chan, gain, 0.2)) == 5)
                for k in range(0,3):
                    assert (isinstance(board.V_oversampchan_stats(chan, gain,
                                                                  0.2)[k],
                                       float))
                # average should have a lower standard deviation than
                # the values used to get the average.
                measurement = board.V_oversampchan_stats(chan, gain, 0.2)
                assert (measurement[2] < measurement[1])
                assert (len(board.V_sampchan(chan, gain)) == 3)
                for k in range(0,1):
                    assert (isinstance(board.V_sampchan(chan, gain)[k], float))
    pass
