# Development Notes

## [Code Repository](https://github.com/JupyterPhysSciLab/JupyterPiDAQ)

## Setting up Development Environment

Basic requirements: Python 3.6+, associated
pip and a Jupyter notebook.
See: [python.org](https://python.org) and
[Jupyter.org](https://jupyter.org).

1. If not installed, install pipenv:`pip3 install --user pipenv`. You may
need to add `~/.local/bin` to your `PATH` to make `pipenv`
available in your command shell. More discussion: 
[The Hitchhiker's Guide to Python](https://docs.python-guide.org/dev/virtualenvs/).
1. Navigate to the directory where this package will be
or has been downloaded to. Use `pipenv`to install an 
["editable" package](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) 
inside the directory as described below:
    1. Start a shell in the environment `pipenv shell`.
    1. Install using pip.
        1. If you downloaded the git repository named "JupyterPiDAQ"
        and have used that directory to build your virtual
        environment: `pip install -e ../JupyterPiDAQ/`.
        1. If you are downloading from PyPi
        `pip install -e JupyterPiDAQ`
        1. Either should install all the additional packages this
        package depends upon. On a Raspberry Pi this will take
        a long time. It probably will not run without at least 1 GB of swap. See: 
        [Build Jupyter on a Pi
        ](https://www.uwosh.edu/facstaff/gutow/computer-and-programming-how-tos/installing-jupyter-on-raspberrian).
    1. Still within the environment shell test this by starting jupyter 
       `jupyter nbclassic` or `jupyter lab`. Jupyter should launch in your 
       browser.
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
    1. Make sure you are running in your virtual environment `pipenv shell` 
       in the directory for  virtual environment will do that.
    1. Issue the command to add this as a kernel to your personal space: 
    `python -m ipykernel install --user --name=<name-you-want-for-kernel>`.
    1. More information is available in the Jupyter/Ipython documentation. 
    A simple tutorial from Nikolai Jankiev (_Parametric Thoughts_) can be
     found [here](https://janakiev.com/til/jupyter-virtual-envs/). 

## Adding New Sensor Code

1. Copy an existing sensor class paste it into the end of
sensors.py and rename it.
2. Update/delete functions for each valid unit within the new
class as necessary.
3. Update the sensor name, vendor and available units in the
`__init__` function.
4. Add the new sensor classname to the list of available sensors
in `listSensors` at about line 120 of sensors.py.
5. Add the new sensor classname to `getsensors` of ADCsim.py,
ADCsim_line.py and any board (e.g. DAQC2.py) with which the sensor
can be used. *Do not guess if a sensor works with a particular
board. Test it!*

## Running Tests

1. Install updated pytest in the virtual environment:
   ```
   pipenv shell
   pip install -U pytest
   ```
2. Run tests ignoring the manual tests in the `dev_testing` directory:
   `python -m pytest --ignore='dev_testing'`.

## Building Documentation

1. Install or update pdoc into the virtual environment `pip install -U pdoc`.
2. Make edits to the `.md` files within the docs folder that are to be 
   included in the first page (see `__init__.py` of the jupyterpidaq package).
3. At the root level run `pdoc 
--logo https://jupyterphysscilab.github.io/JupyterPiDAQ/JupyterPiDAQ-logo.svg --logo-link 
   https://jupyterphysscilab.github.io/JupyterPiDAQ/ --footer-text 
   "JupyterPiDAQ vX.X.X" -html -o docs jupyterpidaq` Unless you are on a 
   Raspbery Pi this will throw an error about `import`. Just ignore.
  
## Building PyPi package

1. Make sure to update the version number in setup.py first.
1. Install updated  setuptools and twine in the virtual environment:
   ```
   pipenv shell
   pip install -U setuptools wheel twine
   ```
1. Build the distribution `python -m setup sdist bdist_wheel`.
1. Test it on `test.pypi.org`.
    1. Upload it (you will need an account on test.pypi.org):
       `python -m twine upload --repository testpypi dist/*`.
    1. Create a new virtual environment and test install into it:
        ```
        exit # to get out of the current environment
        cd <somewhere>
        mkdir <new virtual environment>
        cd <new directory>
        pipenv shell #creates the new environment and enters it.
        pip install -i https://test.pypi.org/..... # copy actual link from the
                                                   # repository on test.pypi.
        ```
       There are often install issues because sometimes only older versions of
       some of the required packages are available on test.pypi.org. If this
       is the only problem change the version to end in `rc0` for release
       candidate and try it on the regular pypi.org as described below for
       releasing on PyPi.
    1. After install test by running a jupyter notebook in the virtual 
       environment.

## Releasing on PyPi

Proceed only if testing of the build is successful.

1. Double check the version number in setup.py.
2. Rebuild the release: `python -m setup sdist bdist_wheel`.
3. Upload it: `python -m twine upload dist/*`
4. Make sure it works by installing it in a clean virtual environment. This
   is the same as on test.pypi.org except without `-i https://test.pypy...`. If
   it does not work, pull the release.
