# Class that manages getting settings for a channel to use in JupyterPiDAQ
# By Jonathan Gutow <jgutow@new.rr.com>
# June 2019
# license GPL3+

# Info on available sensor definitions and units of measurements. This import * looks bad, but the Sensor.py file
# contains an unknown number of sensor definition classes. We need them all to discover what they are.
from Sensors import *
from ipywidgets import widgets


class ChannelSettings():
    """
    This class takes care of interacting with the user to get settings for data collection on each channel. Should be
    initialized with an idno, so that it knows what number has been assigned to it.
    """

    def __init__(self, idno):
        """

        :param idno: int number iding this instance of ChannelSettings
        """
        if (idno == None):
            idno = 0
        self.idno = idno
        self.sensor = None
        self.toselectedunits = None
        self.isactive = False
        self.gain = 1
        self.sensornames = []
        self.defaultunits = []
        self.defaultsensorname = None
        for k in range(len(listSensors())):
            self.sensor = globals()[listSensors()[k]]()
            self.sensornames.append(self.sensor.getname())
            if k == 0:
                self.defaultunits = self.sensor.getunits()
                self.defaultsensorname = self.sensornames[0]
        self.sensor = None  # Set to nothing unless the channel is active.
        ###
        # Jupyter Interactive elements for setting channel parameters
        ###
        self.checkbox = widgets.Checkbox(
            value=self.isactive,
            description='Channel ' + str(self.idno),
            disabled=False)
        self.checkbox.observe(self.checkchanged, names='value')
        self.channellbl = widgets.Text(
            value='Chan' + str(self.idno),  # TODO: update to meaningful title on sensor change if left at default.
            placeholder='Type something',
            description='Title:',
            disabled=True)
        self.sensorchoice = widgets.Dropdown(
            options=self.sensornames,
            # value=self.defaultsensorname, # not needed defaults to the first choice in list
            description='Sensor:',
            disabled=True)
        self.sensorchoice.observe(self.sensorchanged, names='value')
        self.units = widgets.Dropdown(
            options=self.defaultunits,
            # value=self.defaultunits[0], # not needed defaults to the first choice in list
            description='Units:',
            disabled=True)
        self.units.observe(self.unitschanged, names='value')
        # TODO: select gain

    def activate(self):
        """
        This function makes this channel active. No return value unless an error is thrown by something called by this
        function.
        :return: None
        """
        self.sensor = globals()[listSensors()[self.sensorchoice.index]]()
        self.toselectedunits = getattr(self.sensor, self.units.value)
        self.checkbox.value = True  # in case the selection is not done by the user.
        self.channellbl.disabled = False
        self.sensorchoice.disabled = False
        self.units.disabled = False
        self.isactive = True
        pass

    def deactivate(self):
        """
        This function makes the channel inactive. No return value unless an error is thrown by something called by this
        function.
        :return: None
        """
        self.sensor = None
        self.toselectedunits = None
        self.checkbox.value = False  # in case the deactivation is not done by the user.
        self.channellbl.disabled = True
        self.sensorchoice.disabled = True
        self.units.disabled = True
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

    def sensorchanged(self, change):
        """
        Called  by the observe function of sensorchoice when the user changes the sensor choice.
        :param self:
        :param change: change object passed by the observe tool
        :return: None
        """
        # Get the new sensor choice and define the sensor object
        self.sensor = globals()[listSensors()[change['owner'].index]]()
        # Update the unit choices to match the sensor chosen
        self.units.options = self.sensor.getunits()
        # set the unit conversion function
        self.toselectedunits = getattr(self.sensor, self.units.value)
        pass

    def unitschanged(self, change):
        '''
        Called by the observe function for the units selector when units are changed
        :param self:
        :param change: change object passed by the observe tool
        :return:
        '''
        self.toselectedunits = getattr(self.sensor, self.units.value)
        pass

    def setup(self):
        """
        Sets up the GUI and the necessary monitoring.
        :return: None
        """
        self.headbox = widgets.HBox([self.checkbox, self.channellbl])
        self.parambox = widgets.HBox([self.sensorchoice, self.units])
        self.settings = widgets.VBox([self.headbox, self.parambox])
        display(self.settings)
        pass

    def hideGUI(self):
        self.settings.close()
        #Not sure any of the below is necessary. The DOM could use some cleanup. This may require supporting JS.
        self.headbox.close()
        self.parambox.close()
        self.sensorchoice.close()
        self.units.close()
        self.checkbox.close()
        self.channellbl.close()

