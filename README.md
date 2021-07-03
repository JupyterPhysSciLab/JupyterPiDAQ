## JupyterPiDAQ
[Introduction](#introduction) | [Installation](#installation) | 
[Change Log](#change-log) | [License](#license)
### Introduction:
This software allows live collection and plotting of 
analog data in  a Jupyter notebook. The package was initially developed
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
Python 3.6+. You can try the demo mode in binder
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/JupyterPhysSciLab/JupyterPiDAQ.git/HEAD).

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
  * Vernier pressure old and new pressure sensors (V, Pa, kPa, Bar, Torr, 
    mmHg, atm)  
  * Vernier standard pH probe (V, mV, pH).
  * Vernier flat (tris compatible) pH probe (V, mV, pH).
  * Compatible with standard Vernier analog probes. Default calibrations
  being added as time and sensors become available.

You can also hook up your own sensors and manually convert the raw voltage
readings or write and submit a new sensor definition to the project.

_Initial Author_: Jonathan Gutow <gutow@uwosh.edu>

_License_: GPL V3+

### Installation

Installation is meant to be done into a virtual environment
from the PyPi repository. There are two modes "Production" 
for end users and "Development" for those who want to
improve the package.

NOTE: If a binary distribution (whl or wheel) is not available for your
platform, some of the required packages may need to be compiled. If you get
compilation errors when installing try getting the python header and 
development files for your platform. To get them on most *nix platforms use the
command `$ sudo apt install python3-dev`.

_Production_

1. If not installed, install pipenv:`$ pip3 install --user pipenv`. You may
need to add `~/.local/bin` to your `PATH` to make `pipenv`
available in your command shell. More discussion: 
[The Hitchhiker's Guide to
Python](https://docs.python-guide.org/dev/virtualenvs/).
1. Create a directory for the virtual environment you will be installing
   into (example: `$ mkdir JupyterPiDAQ`).
1. Navigate into the directory `$ cd JupyterPiDAQ`.
1. Create the virtual environment and enter it `$ pipenv shell`. To get out of
   the environment you can issue the `$ exit` command on the command line.
1. While still in the shell install the latest JupyterPiDAQ and all its
 requirements
   `$ pip install -U JupyterPiDAQ`. This can take a long time, especially on a
   Raspberry Pi. On a Pi 3B+ (minimum requirement) it will probably not run
   without at least 1 GB of swap. See: [Build Jupyter on a Pi](
   https://www.uwosh.edu/facstaff/gutow/computer-and-programming-how-tos/installing-jupyter-on-raspberrian)
   for a discussion of adding swap space on a Pi.
1. Still within the environment shell test
   this by starting jupyter `$ jupyter notebook`. Jupyter should launch in your browser.
    1. Open a new notebook using the default (Python 3) kernel.
    1. In the first cell import all from DAQinstance.py: 
       `from jupyterpidaq.DAQinstance import *`.
        When run this cell should load the DAQmenu at the end of the Jupyter
        notebook menu/icon bar. If you do not have an appropriate A-to-D
        board installed you will get a message and the software
        will default to demo mode, substituting a random number
        generator for the A-to-D. Because of the demo mode it is
        possible to run this on any computer, not just a Pi.
        
_Development_

Basic requirements: Python 3.6+, associated
pip and a Jupyter notebook.
See: [python.org](https://python.org) and
[Jupyter.org](https://jupyter.org).

1. If not installed, install pipenv:`$ pip3 install --user pipenv`. You may
need to add `~/.local/bin` to your `PATH` to make `pipenv`
available in your command shell. More discussion: 
[The Hitchhiker's Guide to Python](https://docs.python-guide.org/dev/virtualenvs/).
1. Navigate to the directory where this package will be
or has been downloaded to. Use `pipenv`to install an 
["editable" package](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) 
inside the directory as described below:
    1. Start a shell in the environment `$ pipenv shell`.
    1. Install using pip.
        1. If you downloaded the git repository named "JupyterPiDAQ"
        and have used that directory to build your virtual
        environment: `$ pip install -e ../JupyterPiDAQ/`.
        1. If you are downloading from PyPi
        `$ pip install -e JupyterPiDAQ`
        1. Either should install all the additional packages this
        package depends upon. On a Raspberry Pi this will take
        a long time. It probably will not run without at least 1 GB of swap. See: 
        [Build Jupyter on a Pi
        ](https://www.uwosh.edu/facstaff/gutow/computer-and-programming-how-tos/installing-jupyter-on-raspberrian).
    1. Still within the environment shell test
       this by starting jupyter `$ jupyter notebook`. Jupyter should launch in
       your browser.
        1. Open a new notebook using the default (Python 3) kernel.
        1. In the first cell import all from DAQinstance.py: 
        `from jupyterpidaq.DAQinstance import *`.
        When run this cell should load the DAQmenu at the end of the
        Jupyter notebook menu/icon bar. If you do not have an appropriate A-to-D
        board installed you will get a message and the software
        will default to demo mode, substituting a random number
        generator for the A-to-D. Because of the demo mode it is
        possible to run this on any computer, not just a Pi.
1. If you wish, you can make this environment available to an alternate Jupyter
install as a special kernel when you are the user.
    1. Make sure you are running in your virtual environment `$ pipenv shell` 
       in the directory for  virtual environment will do that.
    1. Issue the command to add this as a kernel to your personal space: 
    `$ python -m ipykernel install --user --name=<name-you-want-for-kernel>`.
    1. More information is available in the Jupyter/Ipython documentation. 
    A simple tutorial from Nikolai Jankiev (_Parametric Thoughts_) can be
     found [here](https://janakiev.com/til/jupyter-virtual-envs/). 

### Change Log
 * 0.7.0
    * Switched to plotly widget for plotting.
    * Added Vernier pressure sensor calibrations (old and new).
    * Jupyter widgets based new calculated column GUI.
    * Jupyter widgets based new plot GUI.
    * Default to providing only one time for channels collected nearly 
      simultaneously.
    * As reported values are averages, switched to reporting the estimated 
      standard deviation of the average rather than the deviation of all the 
      readings used to create the average.
 * 0.6.0 
   * Initial release.
   * Live data collection.
   * Recognized sensors: ADS1115 boards (voltage, built-in thermistor, 
     Vernier SS temperature probe), DAQC2 boards (voltage,Vernier SS 
     temperature probe, Vernier standard pH probe, Vernier flat pH probe). 
     
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

Copyright - Jonathan Gutow, 2021.