# Class that manages getting settings for a channel to use in JupyterPiDAQ
# By Jonathan Gutow <gutow@uwosh.edu>
# June 2020
# license GPL3+

from ipywidgets import widgets, Layout

from Sensors import sensors


class ChannelSettings:
    """
    This class takes care of interacting with the user to get settings for data
    collection on each channel. Should be initialized with an idno, so that
    it knows what number has been assigned to it.
    """

    def __init__(self, idno, availboards):
        """

        :param idno: int number iding this instance of ChannelSettings
        """
        if idno == None:
            idno = 0
        self.idno = idno
        self.boardchannel = None
        self.boards = availboards
        self.boardnames = []
        for k in range(len(self.boards)):
            self.boardnames.append((str(k)+' '+self.boards[k].getname(),k))
        self.board = self.boards[0]
        self.channel = self.board.channels[0]
        self.toselectedunits = None
        self.isactive = False
        self.availablegains = self.board.getgains()
        self.toselectedgain = self.availablegains[0]
        self.sensornames = []
        for name in self.board.getsensors():
            self.sensornames.append(name)
        self.sensor = getattr(sensors,self.board.getsensors()[0])(self.board.getVdd())
        self.defaultunits = self.sensor.getunits()
        self.defaultsensorname = self.sensornames[0]
        self.sensor = None  # Set to nothing unless the channel is active.
        ###
        # Jupyter Interactive elements for setting channel parameters
        ###
        self.checkbox = widgets.Checkbox(
            value=self.isactive,
            description='Trace ' + str(self.idno),
            disabled=False)
        self.checkbox.observe(self.checkchanged, names='value')
        self.tracelbl = widgets.Text(
            value='Trace_' + str(self.idno),
            # TODO: update to meaningful title on sensor change if left at
            #  default.
            placeholder='Type something',
            description='Title:',
            disabled=True)
        self.boardchoice = widgets.Dropdown(
            options=self.boardnames,
            description='Board:',
            disabled=True)
        self.boardchoice.observe(self.boardchanged, names='value')
        self.channelchoice = widgets.Dropdown(
            options=self.board.channels,
            description='Channel:',
            disabled=True)
        self.channelchoice.observe(self.channelchanged, names='value')
        self.sensorchoice = widgets.Dropdown(
            options=self.sensornames,
            # value=self.defaultsensorname, # not needed defaults to the first
            # choice in list
            description='Sensor:',
            disabled=True)
        self.sensorchoice.observe(self.sensorchanged, names='value')
        self.units = widgets.Dropdown(
            options=self.defaultunits,
            # value=self.defaultunits[0], # not needed defaults to the first
            # choice in list
            description='Units:',
            disabled=True)
        self.units.observe(self.unitschanged, names='value')
        # TODO: select gain
        self.gains = widgets.Dropdown(
            options=self.availablegains,
            description='gains:',
            disabled=True)
        self.toselectedgain = self.gains.value
        self.gains.observe(self.gainschanged, names='value')

    def activate(self):
        """
        This function makes this channel active. No return value unless an e
        rror is thrown by something called by this function.
        :return: None
        """
        self.sensor = getattr(sensors,self.board.getsensors()[0])(self.board.getVdd())
        self.toselectedunits = getattr(self.sensor, self.units.value)
        self.checkbox.value = True  # in case the selection is not done by the
        # user.
        self.tracelbl.disabled = False
        self.boardchoice.disabled = False
        self.channelchoice.disabled = False
        self.sensorchoice.disabled = False
        self.units.disabled = False
        self.gains.disabled = False
        self.isactive = True
        pass

    def deactivate(self):
        """
        This function makes the channel inactive. No return value unless an
        error is thrown by something called by this function.
        :return: None
        """
        self.sensor = None
        self.toselectedunits = None
        self.checkbox.value = False  # in case the deactivation is not done by
        # the user.
        self.tracelbl.disabled = True
        self.boardchoice.disabled = True
        self.channelchoice.disabled = True
        self.sensorchoice.disabled = True
        self.units.disabled = True
        self.gains.disabled = True
        self.isactive = False
        pass

    def checkchanged(self, change):
        """
        This function is called when the checkbox changes.
        :param self:
        :param change: change object passed by the observe tool
        :return: None
        """
        if (change.new):  # if True
            self.activate()
        else:
            self.deactivate()
        pass

    def boardchanged(self, change):
        """
        This function responds to a change in board choice.
        :param change: change object passed by the observe tool
        :return:
        """
        # Get the new board
        self.board = self.boards[change['owner'].value]
        # Update available channels
        self.channelchoice.options = self.board.getchannels()
        # Trigger update to allowed gains
        self.availablegains = self.board.getgains()
        self.gains.options = self.board.getgains()
        self.toselectedgain = self.availablegains[0]
        # Trigger an update to the sensor list
        self.sensornames = []
        for name in self.board.getsensors():
            self.sensornames.append(name)
        self.sensorchoice.options = self.sensornames
        self.sensor = getattr(sensors,self.board.getsensors()[0])(self.board.getVdd())
        self.defaultunits = self.sensor.getunits()
        self.units.options = self.defaultunits
        self.defaultsensorname = self.sensornames[0]
        self.toselectedunits = getattr(self.sensor, self.defaultunits[0])
        pass

    def channelchanged(self, change):
        """
        This function responds to a change in board choice.
        :param change: change object passed by the observe tool
        :return:
        """
        # set new channel
        self.channel = change['owner'].value
        pass

    def sensorchanged(self, change):
        """
        Called  by the observe function of sensorchoice when the user changes
        the sensor choice.
        :param self:
        :param change: change object passed by the observe tool
        :return: None
        """
        #print(str(change['new'])+',' + str(self.sensorchoice.value))
        # Get the new sensor choice and define the sensor object
        self.sensor = getattr(sensors,change['owner'].value)(self.board.getVdd())
        # Update the unit choices to match the sensor chosen
        self.units.options = self.sensor.getunits()
        # set the unit conversion function
        self.toselectedunits = getattr(self.sensor, self.units.value)
        pass

    def unitschanged(self, change):
        """
        Called by the observe function for the units selector when units are
        changed
        :param self:
        :param change: change object passed by the observe tool
        :return:
        """
        self.toselectedunits = getattr(self.sensor, self.units.value)
        pass

    def gainschanged(self, change):
        """
        Called by the observe function for the gains selector when the gain is
        changed.
        :param self:
        :param change: change object passed by the observe tool
        :return:
        """
        self.toselectedgain = self.gains.value
        pass

    def setup(self):
        """
        Sets up the GUI and the necessary monitoring.
        :return: None
        """
        self.headbox = widgets.HBox([self.checkbox, self.tracelbl])
        self.parambox1 = widgets.HBox(
            [self.boardchoice, self.channelchoice, self.sensorchoice])
        self.parambox2= widgets.HBox([self.units, self.gains])
        self.settings = widgets.VBox([self.headbox, self.parambox1, self.parambox2],
                                    layout=Layout(border='solid'))
        from IPython.core.display import display
        display(self.settings)
        pass

    def hideGUI(self):
        self.settings.close()
        # Not sure any of the below is necessary. The DOM could use some
        # cleanup. This may require supporting JS.
        self.headbox.close()
        self.parambox1.close()
        self.parambox2.close()
        self.sensorchoice.close()
        self.units.close()
        self.checkbox.close()
        self.tracelbl.close()
