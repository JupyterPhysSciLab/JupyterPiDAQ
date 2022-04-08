## Installation

Initial setup: [On Raspberry Pi](#raspberry-pi-initial-setup) | 
[On non-Pi Systems](#non-pi-based-system-initial-setup)

[Final Set up](#final-set-up)

### Raspberry Pi Initial Setup

Unless you only want to run in Demo mode make sure you have one of the 
compatible interface boards installed. The current options are:
* Adafruit compliant ADS1115 boards 
([example](https://www.amazon.com/KNACRO-4-Channel-Raspberry-ADS1115-Channel/dp/B07149WH7P),
also available from other vendors);
* The [&pi;-Plates DAQC2 plate](https://pi-plates.com/daqc2r1/).
* If you wish to use different interfaces  see the [Development
 Notes](https://jupyterphysscilab.github.io/JupyterPiDAQ/jupyterpidaq.html#development-notes)
  and the `Boards` subpackage of `jupyterpidaq` for examples and 
  information on how to define the code interface for a board.

OS specific: [Ubuntu on Pi](#*ubuntu-on-pi*) | 
[Raspberrian on Pi](#*raspberrian-on-pi*)

#### *Ubuntu on Pi*

By default in Ubuntu 20.04 for Pis the gpio and spi groups do not exist.
The i2c group does (not always).

1. Make sure that the following packages are installed `rpi.gpio-common 
python3-pigpio python3-gpiozero python3-rpi.gpio`.
2. You can avoid having to create a gpio group, by assigning users who need
    gpio access to the dialout group. Check that /dev/gpiomem is part of that 
   group and that the dialout group has rw access. If not you will need to set
    it.
3. Users also need to be members of the i2c group. If it does not exist create 
    it and then make that the group for /dev/i2c-1 with group rw permissions. 
   THIS MAY NOT BE NECESSARY. 
4. The spi group needs to be created (addgroup?).
5. Additionally the spi group needs to be given rw access to the spi devices
   at each boot. To do this create a one line rule in a file named 
   `/etc/udev/rules.d/50-spidev.rules` containing `SUBSYSTEM=="spidev", 
   GROUP="spi", MODE="0660"`. The file should have rw permission for root 
   and read permission for everyone else.
6. Make sure you have [pip](https://pip.pypa.io/en/stable/) installed for 
   python 3: `python3 -m pip --version` or `pip3 --version`. If you do not, 
   install using `apt 
   install python3-pip`.
7. 
#### *Raspberrian on Pi*

(TBD)

### Non-Pi based System Initial Setup

Make sure that Python >=3.6 is installed: `python3 -v`. If not follow 
instructions at [python.org](https://python.org). This software should run 
on any computer capable of supporting the necessary version of Python. 
Howevever, it will only run in demo mode if the computer does not support 
one of the compatible A-to-D boards.

#### *Generic Linux*

* If your system hardware 
has GPIO pins and a GPIO interface board, you should try following the 
instructions for a [Pi based system](#raspberry-pi-initial-setup) above. If 
you figure out how to make this work on other SBCs or systems with GPIO, 
please submit a pull request updating these instructions.
* If your system hardware does not support GPIO and one of the compatible 
  interface boards, the software will run in demo mode.

NOTE: If a binary distribution (whl or wheel) is not available for your
platform, some of the required packages may need to be compiled. If you get
compilation errors when installing try getting the python header and 
development files for your platform. To get them on most *nix platforms use the
command `$ sudo apt install python3-dev`.

#### *MacOS*

#### *Windows (Please, no.....)*

### Final Set Up

Make sure the user you will be running the software under is a member of the 
groups `dialout`, `spi` and if it exists`i2c`. It is recommended that you 
install JupyterPiDAQ in its own 
[virtual environment](https://docs.python.org/3/tutorial/venv.html?highlight=virtual%20environments).
The instructions below do just that using the original author's favorite 
virtual environment tool [pipenv](https://pipenv.pypa.io/en/latest/).

Log into your chosen user account:
1. Install [pipenv](https://pipenv.pypa.io/en/latest/): `pip3 install 
   --user pipenv`. You may
need to add `~/.local/bin` to your `PATH` to make `pipenv`
available in your command shell. More discussion: 
[The Hitchhiker's Guide to
Python](https://docs.python-guide.org/dev/virtualenvs/).
2. Create a directory for the virtual environment you will be installing
   into (example: `$ mkdir JupyterPiDAQ`).
3. Navigate into the directory `$ cd JupyterPiDAQ`.
4. Create the virtual environment and enter it `$ pipenv shell`. To get out of
   the environment you can issue the `$ exit` command on the command line.
5. While still in the shell install the latest JupyterPiDAQ and all its
 requirements
   `$ pip install -U JupyterPiDAQ`. This can take a long time, especially on a
   Raspberry Pi. On a Pi 3B+ (minimum requirement) it will probably not run
   without at least 1 GB of swap. See: [Build Jupyter on a Pi](
   https://cms.gutow.uwosh.edu/Gutow/useful-chemistry-links/software-tools-and-coding/computer-and-coding-how-tos/installing-jupyter-on-raspberrian)
   for a discussion of adding swap space on a Pi.
6. Still within the environment shell test
   this by starting jupyter `$ jupyter notebook`. Jupyter should launch in your browser.
    1. Open a new notebook using the default (Python 3) kernel.
    2. In the first cell import all from DAQinstance.py: 
       `from jupyterpidaq.DAQinstance import *`.
        When run this cell should load the DAQmenu at the end of the Jupyter
        notebook menu/icon bar. If you do not have an appropriate A-to-D
        board installed you will get a message and the software
        will default to demo mode, substituting a random number
        generator for the A-to-D. Because of the demo mode it is
        possible to run this on any computer, not just a Pi.
7. If you wish, you can make this environment available to an alternate Jupyter
install as a special kernel when you are the user.
    1. Make sure you are running in your virtual environment `$ pipenv shell` 
       in the directory for  virtual environment will do that.
    2. Issue the command to add this as a kernel to your personal space: 
    `$ python -m ipykernel install --user --name=<name-you-want-for-kernel>`.
    3. More information is available in the Jupyter/Ipython documentation. 
    A simple tutorial from Nikolai Jankiev (_Parametric Thoughts_) can be
     found [here](https://janakiev.com/til/jupyter-virtual-envs/). 