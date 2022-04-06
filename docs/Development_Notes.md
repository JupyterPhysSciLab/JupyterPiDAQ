## Development Notes

### Adding New Sensor Code

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

### Running Tests

1. Install updated pytest in the virtual environment:
   ```
   pipenv shell
   pip install -U pytest
   ```
1. Run tests ignoring the manual tests in the `dev_testing` directory:
   `python -m pytest --ignore='dev_testing'`.
   
### Building PyPi package

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

### Releasing on PyPi

Proceed only if testing of the build is successful.

1. Double check the version number in setup.py.
2. Rebuild the release: `python -m setup sdist bdist_wheel`.
3. Upload it: `python -m twine upload dist/*`
4. Make sure it works by installing it in a clean virtual environment. This
   is the same as on test.pypi.org except without `-i https://test.pypy...`. If
   it does not work, pull the release.

### Building Documentation

1. Install or update pdoc into the virtual environment `pip install -U pdoc`.
2. Make edits to the `.md` files within the docs folder that are to be 
   included in the first page (see `__init__.py` of the jupyterpidaq package).
3. At the root level run `pdoc --logo docs/JupyterPiDAQ-logo.svg --logo-link 
   https://jupyterphysscilab.github.io/JupyterPiDAQ/ --footer-text 
   "JupyterPiDAQ vX.X.X" -html -o docs jupyterpidaq` Unless you are on a 
   Raspbery Pi this will throw an error about `import RPi.GPIO`. Just ignore.