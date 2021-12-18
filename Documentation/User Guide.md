[Introduction](#introdcution) | [Installation](installation.md) | 
[Usage](#usage) |
### Introduction
 This software allows realtime collection and plotting of 
digitized data in  a Jupyter notebook using either of the following two
interface boards on a Raspberry Pi:
* Adafruit compliant ADS1115 boards 
([example](https://www.amazon.com/KNACRO-4-Channel-Raspberry-ADS1115-Channel/dp/B07149WH7P),
also available from other vendors);
* The [&pi;-Plates DAQC2 plate](https://pi-plates.com/daqc2r1/). 
* A demo mode will run on any computer with a Jupyter notebook install and
Python 3.6+. You can try the demo mode without installing on your own 
  computer by launching an instance on the MyBinder servers:
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/JupyterPhysSciLab/JupyterPiDAQ.git/HEAD?filepath=usage_examples).
 Example notebooks can be found in the "usage_examples" folder.

### Usage
#### Starting JupyterPiDAQ
A working Jupyter notebook installation with JupyterPiDAQ installed is
required. If you need to install the software see the [Installation 
Instructions](Installation.md). There are two common ways this may be set 
up, that lead to slightly different steps for starting the software:
1. __A special kernel__ may be set up that can be used in any Jupyter notebook 
   install for the current user (see the end of the
   [Installation instruction](installation.md)). 
    1. In this case launch
   Jupyter, in which ever directory you want to work, using the 
   command: `jupyter notebook`.
    2. Open a new notebook and choose the kernel 
   for `JupyterPiDAQ`. The kernel name will depend upon what was chosen 
   during installation.
    3. Initialize the data acquisition 
       tools by putting the statement `from jupyterpidaq.DAQinstance import 
       *` into the first cell and clicking on the 'Run' button.
2. __Only for use within the directory structure of the virtual environment__ 
   that was set up for the software. 
    1. In this case you must navigate to the 
   directory of the virtual environment using the `cd` command before 
   starting the software.
    2. Then enter the virtual environment with the command `pipenv shell`. 
       This assumes you set up `pipenv` as described in the 
       [Installation instructions](installation.md).
    3. Launch Jupyter using the command: `jupyter notebook`.
    4. Open a new python notebook.
    5. Initialize the data acquisition 
       tools by putting the statement `from jupyterpidaq.DAQinstance import 
       *` into the first cell and clicking on the 'Run' button.