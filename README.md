**JupyterPiDAQ**

This software allows live collection and plotting of 
analog data in Jupyter on a Raspberry Pi.  For now the 
only compatible A-to-D is the ADS1115 piHAT.
So far this has been tested on a RPi 3B+. A demo mode will
run on any computer with a Jupyter notebook install and
Python 3.6+.

_Author_: Jonathan Gutow <jgutow@new.rr.com>

_License_: GPL V3+

**Installation**

Installation is meant to be done into a virtual environment
from the PyPi repository. There are two modes "Production" 
for end users and "Development" for those who want to
improve the package.

_Production_

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
        1. If you are downloading from PyPi (not yet available)
        `$ pip install -e JupyterPiDAQ`
        1. Either should install all the additional packages this
        package depends upon. On a Raspberry Pi this will take
        a long time. It probably will not run without at least 1 GB of swap. See: 
[Build Jupyter on a Pi](https://www.uwosh.edu/facstaff/gutow/computer-and-programming-how-tos/installing-jupyter-on-raspberrian).
    1. Still within the environment shell test
    this by starting jupyter `$ jupyter notebook`. Jupyter should launch in your browser.
        1. Open a new notebook using the default (Python 3) kernel.
        1. In the first cell import all from DAQinstance.py: `from DAQinstance import *`.
        When run this cell should load the DAQmenu at the end of the Jupyter notebook 
        menu/icon bar. If you do not have an appropriate A-to-D
        board installed you will get a message and the software
        will default to demo mode, substituting a random number
        generator for the A-to-D. Because of the demo mode it is
        possible to run this on any computer, not just a Pi.
1. If you wish, you can make this environment available to an alternate Jupyter
install as a special kernel when you are the user.
    1. Make sure you are running in your virtual environment `$ pipenv shell` in the directory for  virtual
    environment will do that.
    1. Issue the command to add this as a kernel to your personal space: 
    `$ python -m ipykernel install --user --name=<name-you-want-for-kernel>`.
    1. More information is available in the Jupyter/Ipython documentation. A simple tutorial from Nikolai Jankiev
    (_Parametric Thoughts_) can be found [here](https://janakiev.com/til/jupyter-virtual-envs/). 
1. Installation as a PyCharm project is also possible. The git repository should contain the PyCharm project info.

