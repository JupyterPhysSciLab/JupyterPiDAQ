# Change Log
* 0.8.1 (May 2, 2023)
  * BUG FIX: Now always waits for all data to be transferred to plot before 
    writing backup to a file.
  * More rapid update of display when using LabQuests.
  * Docs now recommend launching `jupyter nbclassic` for old notebook interface.
* 0.8.0 (Apr. 20, 2023)
  * Replaced `NewRun()` command with `Run()` command. This version works in 
    Jupyter Lab and removes the need for the `DisplayRun()` command because 
    `Run()` will load an already collected dataset or start a new one.
  * Now, when multiple traces are assigned to the same channel of a board the 
    channel is only read one time. If the units are different the two 
    traces will be displayed with different units.
  * Can read data from [Vernier](https://www.vernier.com) LabQuest USB 
    analog-to-digital interfaces. Potential data rate is 10 kHz, currently 
    limited to 20 Hz.
  * Runs in [Jupyter](https://jupyter.org/) Lab (no menus yet) and Notebook 
    (menus still work).
  * Updated requirements to include jupyterlab and labquest packages.
* 0.7.9 (Mar. 9 2023)
  * Added `spidev` package to requirements because `pi-plates` requires it.
  * More robust exception handling when searching for boards/A-to-Ds.
* 0.7.8
  * Updated text for insertion into cells to make better use of escaping 
    updates in JPSLUtils >=0.7.0.
  * Removed some unnecessary print statements.
* 0.7.7
  * Updated requirements for upstream security fixes.
  * Conversion to pandas dataframe now works when trace 0 is not collected.
  * DAQ menu no longer created in trusted notebooks if the data acquisition 
    tools have not been initialized since the notebook was opened.
  * Reworked the data collection so that opening an old notebook without 
    running anything will not have any leftover inoperable or undefined 
    widgets.
  * Reordered the live trace display to match the order of the names at right.
  * Runs now saved to a human readable html file that includes the run 
    conditions.
  * As long as this html file is in the same directory as the notebook, the 
    run display can be recreated by running its cell after accidentally 
    clearing the cell output.
  * The cell displaying the results of a run is now protected against 
    deletion and editing.
* 0.7.6
  * Converted to fancy menus (could make hierarchical).
* 0.7.5
  * Added fitting to DAQ command menu.
  * Documentation Enhancements: github.io website; first pass as API docs; 
    reorganized documentation; MyBinder link now forces launch in classic 
    notebook; added plans for adapter board to connect Vernier Sensors.
* 0.7.4.1
  * Improved layout of data collection.
  * Better widget cleanup.
  * Readme fixes.
* 0.7.3 Pip install reliability fixes.
* 0.7.2 Suppress Javascript error when not in JLab.
* 0.7.1
  * Include Heat Capacity Lab example.
  * Make menu show up in JLab (still not functional).
  * Remove matplotlib baggage.
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
