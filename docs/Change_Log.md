## Change Log
* 0.7.5
  * Added fitting to DAQ command menu.
  * Documentation Enhancements:
    * github.io website.
    * First pass as API docs.
    * Reorganized documentation.
    * MyBinder link now forces launch in classic notebook.
    * Added plans for adapter board to connect Vernier Sensors.
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
