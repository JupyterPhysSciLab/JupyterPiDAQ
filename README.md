## JupyterPiDAQ
[Introduction](#introduction) | [License](#license)

### [Website/Documentation](https://jupyterphysscilab.github.io/JupyterPiDAQ/)

### Introduction:
This software allows realtime collection and plotting of 
digitized data in  a Jupyter notebook. The package was initially developed
to provide an inexpensive laboratory system for teaching based on
the Raspberry Pi.  However, as the development has progressed the data
acquisition board drivers have been separated out of the user interface,
so that the software has potential to work on other computers running Jupyter
with A-to-D board specific connector code. Presently the compatible A-to-Ds are
for Raspberry Pis: 
* Adafruit compliant ADS1115 boards 
([example](https://www.amazon.com/KNACRO-4-Channel-Raspberry-ADS1115-Channel/dp/B07149WH7P),
also available from other vendors);
* The [&pi;-Plates DAQC2 plate](https://pi-plates.com/daqc2r1/). 
* A demo mode will run on any computer with a Jupyter notebook install and
Python 3.6+. You can try the demo mode without installing on your own 
  computer by launching an instance on the MyBinder servers:
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/JupyterPhysSciLab/JupyterPiDAQ.git/HEAD?urlpath=/tree/usage_examples)
  
The goal is for the user interface to be as close to self-explanatory as
 possible. However, documentation is being developed along with some example
  experiments.

##### Sensors:
Like many commercial educational packages the software knows about the
properties of some sensors, so can collect data directly in the units
appropriate for the sensor, in addition to the raw voltage signal returned
by the sensor. Not all sensors are compatible with all boards.
The developer(s) attempt to keep this list of known sensors up-to-date, but the
code may provide additional sensors not listed here:
* __ADS1115 compatible__ (board can provide 3.3 V of power/reference to
 sensors):
  * voltage reading (V, mV) from any sensor that puts out a voltage in the
   range +/-3.3 V.
  * built-in thermistor (V, mV, K, C, F).
  * Vernier SS temperature probe (V, mV, K, C, F).
* __DAQC2 compatible__ (board can provide 5.0 V of power/reference to sensors):
  * voltage reading (V, mV) from any sensor that puts out a voltage in the
   range +/- 12 V.
  * Vernier SS temperature probe (V, mV, K, C, F).
  * Vernier old and new pressure sensors (V, Pa, kPa, Bar, Torr, mmHg, atm)  
  * Vernier standard pH probe (V, mV, pH).
  * Vernier flat (tris compatible) pH probe (V, mV, pH).
  * Compatible with standard Vernier analog probes. Default calibrations
  being added as time and sensors become available.

You can also hook up your own sensors and manually convert the raw voltage
readings or write and submit a new sensor definition to the project.

### License:
[This software is distributed under the GNU V3 license](https://gnu.org/licenses).
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

Copyright - Jonathan Gutow, 2021, 2022.