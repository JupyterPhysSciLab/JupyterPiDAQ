# Definitions of known sensors for JupyterPiDAQ
# By Jonathan Gutow <gutow@uwosh.edu>
# June 2019
# license GPL3+

# class for each sensor and some utility functions

import math
import numpy as np
import logging

logger = logging.getLogger(__name__)


###
# Private Utility functions. WARNING: behavior may change
###

# Unit conversions

def _KtoC(K):
    """

    :param K: temperature in K
    :return: temperature in C
    """
    return K - 273.15


def _CtoF(C):
    """

    :param C: temperature in C
    :return: temperature in F
    """
    return C * 9.0 / 5.0 + 32.0


def _ntc_therm_RtoK(R, A, B, C):
    """
    Converts resistance of a negative temperature coefficient thermistor to
    temperature in Kelvin using the
    Steinhart Hart model.
    :param R: Resistance in Ohms
    :param A: Steinhart Hart A coefficient
    :param B: Steinhart Hart B coefficient
    :param C: Steinhart Hart C coefficient
    :return: Temperature in K
    """
    K = 1 / (A + B * math.log(R) + C * (math.log(R)) ** 3)
    logger.debug('K: ' + str(K))
    return K


###
# End of Private Utility Functions.
###

###
# Public Utility Functions
###

# Round values to reflect uncertainty/standard deviation

def to_reasonable_significant_figures(value, uncertainty):
    """
    This function will return value rounded to a reasonable number of
    significant figures based on the uncertainty. If you are doing this
    based on the standard return from the raw voltage or the sensor
    definitions in this file it is recommend that this be the standard
    deviation of the average, which will often provide about one more digit
    than the standard deviation. This will provide a guard digit for further
    computations.

    :param float value: the value to be rounded
    :param float uncertainty: the uncertainty.

    :returns float:

    Returns: rounded_value a floating point number.
    """
    decimals = 0
    if uncertainty == 0:
        decimals = 6
    else:
        if (uncertainty != float('inf')) and (uncertainty > 0):
            decimals = -int(np.floor(np.log10(uncertainty)))
    value = np.around(value, decimals=decimals)
    return value


def to_reasonable_significant_figures_fast(avg, std, avg_std):
    """
    This function will return values rounded to a reasonable number of
    significant figures based on the avg_std. This function requires fewer
    compares so is a little more efficient than calling
    to_reasonable_significant_figures(value, uncertainty) for avg, std,
    avg_std separately.

    :param float avg: the average value
    :param float std: the standard deviation
    :param float avg_std: the estimated standard deviation in avg
    :returns list:

    Returns: list of rounded values for each [avg, std, avg_std]
    """
    decimals = 0
    if avg_std == 0:
        decimals = 6
    else:
        if (avg_std != float('inf')) and (avg_std > 0):
            decimals = -int(np.floor(np.log10(avg_std)))
    avg = np.around(avg, decimals=decimals)
    std = np.around(std, decimals=decimals)
    avg_std = np.around(avg_std, decimals=decimals)
    return [avg, std, avg_std]


# Sensor list.
# TODO: Should be added to when each new sensor class is added.

def listSensors():
    """
    Provides a list of the sensor classes provided by this file. The list must
    be manually updated with each new class.
    :return: list of classnames
    """
    return ['RawAtoD',
            'BuiltInThermistor',
            'VernierSSTemp',
            'VernierGasP',
            ]
    # TODO: extend this list when each new sensor class is added. RawAtoD
    #  should always be first in the list.


###
# Sensor Classes
#
# Each class must extend the `Class RawAtoD`. See below:
###

class RawAtoD:
    """
    This is the base sensor class which all sensors should extend. See how to
    do this properly using one of the examples below.
    This class contains definitions for the raw AtoD return in volts. The
    digital values are not used as the AtoD may have a builtin pre-amp,
    so a given digital value has different meanings depending upon the pre-amp
    setting.
    """

    def __init__(self, Vdd):
        """
        This init should be called first in the init section of any class
        extending this class (e.g. `super().__init__(Vdd)`). Then set
        `self.name` and `self.vendor` to the proper values. Append units
        specific to the sensor to `self.units`. The parameter Vdd must be
        supplied upon initialization because the output voltage of some
        sensors depends on Vdd.

        :param float Vdd: the voltage supplied to the sensor by the A-to-D
         board in case the sensor output depends on this.
        """
        self.name = 'Volts at A-to-D'
        self.vendor = '--'
        self.units = ['V', 'mV']
        self.Vdd = Vdd
        pass

    def getname(self):
        """
        Provides a string name for the sensor
        :return: string containing the sensor name
        """
        return self.name

    def getvendor(self):
        """
        Provides a string name for the sensor vendor/manufacturer
        :return: string containing the vendor/manufacturer name
        """
        return self.vendor

    def getunits(self):
        """
        Provides the string names for the available units for this sensor.
        These string names are also the functions within this class that
        return the measurement in those units.
        :return: units a list of strings.
        """
        return self.units

    def V(self, v_avg, v_std, avg_std, avg_vdd):
        """
        It is not really necessary to call this function because it just
        returns the same values that are passed to it.
        It is provided for consistency with the way sensors units are defined.
        :param v_avg: v_avg: average voltage from A-to-D
        :param v_std: standard deviation of the A-to-D measurements
        :param avg_std: estimate of the standard deviation of v_avg
        :param float avg_vdd: simultaneously measured average Vdd.
        :return: [v_avg, v_std, avg_std]
        """
        return v_avg, v_std, avg_std

    def mV(self, v_avg, v_std, avg_std, avg_vdd):
        """
        Convert the raw AtoD voltage to mV.
        :param v_avg: v_avg: average voltage from A-to-D
        :param v_std: standard deviation of the A-to-D measurements
        :param avg_std: estimate of the standard deviation of v_avg
        :param float avg_vdd: simultaneously measured average Vdd.
        :return: [v_avg, v_std, avg_std] converted to mV
        """
        return 1000 * v_avg, 1000 * v_std, 1000 * avg_std


class BuiltInThermistor(RawAtoD):
    """
    This class contains the definitions for builtin thermistor.
    """

    def __init__(self, Vdd):
        super().__init__(Vdd)
        self.name = 'Built-in Thermistor'
        self.vendor = 'KNARCO'
        self.units = self.units + ['K', 'C', 'F']
        self.gains = [1]
        self.Vdd = Vdd
        # print('Done initializing builtinthermistor class.')
        pass

    ###
    # Sensor specific units. Notice the function names must match the string
    # used for the units.
    ###

    def K(self, v_avg, v_std, avg_std, avg_vdd):
        """
        The returned values are in K. It is assumed that the distribution is
        symmetric guassian even in K. This may not be true, but still gives
        a reasonable estimate of the standard deviation.
        :param v_avg: average voltage from sensor.
        :param v_std: standard deviation of voltage from sensor.
        :param avg_std: estimated standard deviation of the avg.
        :param float avg_vdd: simultaneously measured average Vdd.
        :return list:

        Returns: list [K_avg, K_std, K_avg_std]
         [average temperature in K,
         standard deviation of temperature in K,
         estimated standard deviation of the average temperature].
        """
        # Correct values based on measured reference voltage
        v_avg = v_avg * self.Vdd / avg_vdd
        v_std = v_std * self.Vdd / avg_vdd
        avg_std = avg_std * self.Vdd / avg_vdd
        # v_avg to K
        K_avg = self._VtoK(v_avg)
        # standard deviation of temperature
        v_max = v_avg + v_std
        v_min = v_avg - v_std
        K_max = self._VtoK(v_max)
        K_min = self._VtoK(v_min)
        K_std = (K_max - K_min) / 2.0
        # assuming a symmetric gaussian error even after transform from volts.
        # estimated standard deviation of the average temperature
        v_max = v_avg + avg_std
        v_min = v_avg - avg_std
        K_max = self._VtoK(v_max)
        K_min = self._VtoK(v_min)
        K_avg_std = (K_max - K_min) / 2.0
        # assuming a symmetric gaussian error even after transform from volts.
        return K_avg, K_std, K_avg_std

    def C(self, v_avg, v_std, avg_std, avg_vdd):
        """
        The returned values are in deg C. It is assumed that the distribution
        is symmetric guassian even in deg C. This may not be true, but still
        gives a reasonable estimate of the standard deviation.
        :param v_avg: average voltage from sensor.
        :param v_std: standard deviation of voltage from sensor.
        :param avg_std: estimated standard deviation of the avg.
        :param float avg_vdd: simultaneously measured average Vdd.
        :return list:

        Returns: list [C_avg, C_std, C_avg_std]
         [average temperature in C, standard deviation of temperature in C,
            estimated standard deviation of the average temperature].
        """
        K_avg, K_std, K_avg_std = self.K(v_avg, v_std, avg_std, avg_vdd)
        C_avg = _KtoC(K_avg)
        return C_avg, K_std, K_avg_std

    def F(self, v_avg, v_std, avg_std, avg_vdd):
        """
        The returned values are in deg F. It is assumed that the distribution
        is symmetric guassian even in deg F. This may not be true, but still
        gives a reasonable estimate of the standard deviation.
        :param float v_avg: average voltage from sensor.
        :param float v_std: standard deviation of voltage from sensor.
        :param float avg_std: estimated standard deviation of the avg.
        :param float avg_vdd: simultaneously measured average Vdd.
        :returns list:

        Returns: list [F_avg, F_std, F_avg_std]
         [average temperature in F, standard deviation of temperature in F,
         estimated standard deviation of the average temperature].
        """
        K_avg, K_std, K_avg_std = self.K(v_avg, v_std, avg_std, avg_vdd)
        F_avg = _CtoF(_KtoC(K_avg))
        F_std = K_std * 9.0 / 5.0
        F_avg_std = K_avg_std * 9.0 / 5.0
        return F_avg, F_std, F_avg_std

    def _VtoK(self, volts):
        """
        :param volts: voltage measurement
        :return: temperature in K.
        """
        # Steinhart Hart coefficients for this thermistor
        A = 0.0009667974157916105
        B = 0.00024132572130718138
        C = 2.077144181533216e-07
        # Need to stay in sensor range, if get bad voltage throw max or min
        # possible value alternative for pegging would be to set to 1.649999
        # which gives < absolute zero.
        if volts <= 0:
            volts = 1e-312  # gets about 0 K
        if volts >= 1.65:
            volts = 1.649998411  # gets very high T in K
        R = self.Vdd * 1.0e4 / volts - 2.0e4
        tempK = _ntc_therm_RtoK(R, A, B, C)
        return tempK


class VernierSSTemp(RawAtoD):
    """
    This class contains the definitions for Vernier Stainless Steel Temperature
    Probe. A 20K thermistor.
    """

    def __init__(self, Vdd):
        super().__init__(Vdd)
        self.name = 'Vernier SS Temperature Probe'
        self.vendor = 'Vernier'
        self.units = self.units + ['K', 'C', 'F']
        self.Vdd = Vdd
        pass

    ###
    # Sensor specific units. Notice the function names must match the
    # string used for the units.
    ###

    def K(self, v_avg, v_std, avg_std, avg_vdd):
        """
        The returned values are in K. It is assumed that the distribution is
        symmetric guassian even in K. This may not be true, but still gives
        a reasonable estimate of the standard deviation.
        :param float v_avg: average voltage from sensor.
        :param float v_std: standard deviation of voltage from sensor.
        :param float avg_std: estimated standard deviation of the avg.
        :param float avg_vdd: simultaneously measured average Vdd.
        :returns list:

        Returns list [K_avg, K_std, K_avg_std]
         [average temperature in K, standard deviation of temperature in K,
         estimated standard deviation of the average temperature].
        """
        logger.debug(
            'voltages in: ' + str(v_avg) + ' ' + str(v_std) + ' ' + str(
                avg_std))
        # Correct values based on measured reference voltage
        v_avg = v_avg * self.Vdd / avg_vdd
        v_std = v_std * self.Vdd / avg_vdd
        avg_std = avg_std * self.Vdd / avg_vdd
        # v_avg to K
        K_avg = self._VtoK(v_avg)
        # standard deviation of temperature
        v_max = v_avg + v_std
        v_min = v_avg - v_std
        K_max = self._VtoK(v_min)
        K_min = self._VtoK(v_max)
        K_std = (K_max - K_min) / 2.0
        # assuming a symmetric gaussian error even after transform from volts.
        # estimated standard deviation of the average temperature
        v_max = v_avg + avg_std
        v_min = v_avg - avg_std
        K_max = self._VtoK(v_min)
        K_min = self._VtoK(v_max)
        K_avg_std = (K_max - K_min) / 2.0
        # assuming a symmetric gaussian error even after transform from volts.
        logger.debug(
            'K out: ' + str(K_avg) + ' ' + str(K_std) + ' ' + str(K_avg_std))
        return K_avg, K_std, K_avg_std

    def C(self, v_avg, v_std, avg_std, avg_vdd):
        """
        The returned values are in deg C. It is assumed that the distribution
        is symmetric guassian even in deg C. This may not be true, but still
        gives a reasonable estimate of the standard deviation.

        :param float v_avg: average voltage from sensor.
        :param float v_std: standard deviation of voltage from sensor.
        :param float avg_std: estimated standard deviation of the avg.
        :param float avg_vdd: simultaneously measured average Vdd.
        :return tuple:

        Returns: C_avg, C_std, C_avg_std
         average temperature in C, standard deviation of temperature in C,
         estimated standard deviation of the average temperature.
        """
        K_avg, K_std, K_avg_std = self.K(v_avg, v_std, avg_std, avg_vdd)
        C_avg = _KtoC(K_avg)
        return C_avg, K_std, K_avg_std

    def F(self, v_avg, v_std, avg_std, avg_vdd):
        """
        The returned values are in deg F. It is assumed that the
        distribution is symmetric guassian even in deg F. This may not be
        true, but still gives a reasonable estimate of the standard
        deviation.

        :param float v_avg: average voltage from sensor.
        :param float v_std: standard deviation of voltage from sensor.
        :param float avg_std: estimated standard deviation of the avg.
        :param float avg_vdd: simultaneously measured average Vdd.

        :return list:

        Returns: F_avg, F_std, F_avg_std
         average temperature in F, standard deviation of
         temperature in F, estimated standard deviation of the average
         temperature.
        """
        K_avg, K_std, K_avg_std = self.K(v_avg, v_std, avg_std, avg_vdd)
        F_avg = _CtoF(_KtoC(K_avg))
        F_std = K_std * 9.0 / 5.0
        F_avg_std = K_avg_std * 9.0 / 5.0
        return F_avg, F_std, F_avg_std

    def _VtoK(self, volts):
        """
        :param volts: voltage measurement
        :return: temperature in K.
        """
        # Steinhart Hart coefficients for this thermistor
        A = 0.00102119
        B = 0.000222468
        C = 1.33342e-07
        # Need to stay in sensor range, if get bad voltage throw max or min
        # possible value alternative for pegging would be to set to 1.649999
        # which gives < absolute zero.
        if (
                volts <= 0):
            # TODO: fix over and underflow for vernier thermistor sensors.
            volts = 1e-312  # gets high T
        if volts >= self.Vdd:
            volts = self.Vdd - 1e-10  # gets low T in K
        R = volts * 1.5e4 / (self.Vdd - volts)
        logger.debug('volts: ' + str(volts) + ' R: ' + str(R))
        tempK = _ntc_therm_RtoK(R, A, B, C)
        return tempK


class VernierGasP(RawAtoD):
    """
    This class contains the definitions for Vernier absolute gas pressure
    sensor, GPS-BTA.
    """

    def __init__(self, Vdd):
        super().__init__(Vdd)
        self.name = 'Vernier Absolute Gas Pressure Sensor'
        self.vendor = 'Vernier'
        self.units = self.units + ['Pa', 'kPa', 'Bar', 'Torr', 'mmHg', 'atm']
        self.Vdd = Vdd
        pass

    ###
    # Sensor specific units. Notice the function names must match the
    # string used for the units.
    ###

    def Pa(self, v_avg, v_std, avg_std, avg_vdd):
        """

        :param float v_avg: average raw voltage
        :param float v_std: standard deviation of the raw voltage
        :param float avg_std: estimated standard deviation of v_avg
        :param float avg_vdd: the Vdd measured simultaneously with v_avg (not
        used)
        :return list:

        Returns: P_avg, P_std, P_avg_std all in Pascals
        """
        P_avg = 51710 * v_avg - 25860
        P_std = 51710 * v_std
        P_avg_std = 51710 * avg_std
        return P_avg, P_std, P_avg_std

    def kPa(self, v_avg, v_std, avg_std, avg_vdd):
        """

        :param float v_avg: average raw voltage
        :param float v_std: standard deviation of the raw voltage
        :param float avg_std: estimated standard deviation of v_avg
        :param float avg_vdd: the Vdd measured simultaneously with v_avg (not
        used)
        :return list:

        Returns: P_avg, P_std, P_avg_std all in kiloPascals
        """
        P_avg = 51.710 * v_avg - 25.860
        P_std = 51.710 * v_std
        P_avg_std = 51.710 * avg_std
        return P_avg, P_std, P_avg_std

    def Bar(self, v_avg, v_std, avg_std, avg_vdd):
        """

        :param float v_avg: average raw voltage
        :param float v_std: standard deviation of the raw voltage
        :param float avg_std: estimated standard deviation of v_avg
        :param float avg_vdd: the Vdd measured simultaneously with v_avg (not
        used)
        :return list:

        Returns: P_avg, P_std, P_avg_std all in Bars
        """
        P_avg = .51710 * v_avg - .25860
        P_std = .51710 * v_std
        P_avg_std = .51710 * avg_std
        return P_avg, P_std, P_avg_std

    def Torr(self, v_avg, v_std, avg_std, avg_vdd):
        """

        :param float v_avg: average raw voltage
        :param float v_std: standard deviation of the voltage measurements
        :param float avg_std: estimate of the standard deviation of the average
        :param float avg_vdd: the Vdd measured simultaneously with v_avg (
        not used)
        :return list:

        Returns: P_avg, P_std, P_avg_std all in Torr
        """
        P_avg, P_std, P_avg_std = self.Pa(v_avg, v_std, avg_std, avg_vdd)
        P_avg = P_avg * 760.0 / 101325
        P_std = P_std * 760.0 / 101325
        P_avg_std = P_avg_std * 760.0 / 101325
        return P_avg, P_std, P_avg_std

    def mmHg(self, v_avg, v_std, avg_std, avg_vdd):
        """

        :param float v_avg: average raw voltage
        :param float v_std: standard deviation of the voltage measurements
        :param float avg_std: estimate of the standard deviation of the average
        :param float avg_vdd: the Vdd measured simultaneously with v_avg (
        not used)
        :return list:

        Returns: P_avg, P_std, P_avg_std all in mmHg
        """
        return self.Torr(v_avg, v_std, avg_std, avg_vdd)

    def atm(self, v_avg, v_std, avg_std, avg_vdd):
        """

        :param float v_avg: average raw voltage
        :param float v_std: standard deviation of the voltage measurements
        :param float avg_std: estimate of the standard deviation of the average
        :param float avg_vdd: the Vdd measured simultaneously with v_avg (
        not used)
        :return list:

        Returns: P_avg, P_std, P_avg_std all in atm
        """
        P_avg, P_std, P_avg_std = self.Pa(v_avg, v_std, avg_std, avg_vdd)
        P_avg = P_avg / 101325
        P_std = P_std / 101325
        P_avg_std = P_avg_std / 101325
        return P_avg, P_std, P_avg_std