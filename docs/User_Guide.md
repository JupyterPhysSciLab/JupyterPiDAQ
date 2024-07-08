# User Guide

[Introduction](#introduction) | 
[Usage](#usage)

## Introduction

This software allows GUI (Graphical User Interface) driven live collection, 
plotting and analysis of digitized data inside a Jupyter notebook using the 
following A-to-D interfaces:

**on a Raspberry Pi:**
* Adafruit compliant ADS1115 boards 
([example](https://www.amazon.com/KNACRO-4-Channel-Raspberry-ADS1115-Channel/dp/B07149WH7P),
also available from other vendors);
* The [&pi;-Plates DAQC2 plate](https://pi-plates.com/daqc2r1/).

**on MacOS and Windows:**
* [Vernier](https://www.vernier.com) LabQuest USB A-to-Ds.

**demo mode on anything Jupyter runs on**
* A demo mode will run on any computer with a Jupyter notebook install and
Python 3.6+. Example notebooks can be found in the "usage_examples" folder.

## Usage

[Launch the software](#starting-jupyterpidaq) | 
[Initialize data acquisiton tools](#initialize-the-data-acquisition-tools) | 
[Collect data](#collecting-data) |
[Displaying a Data Table](#in-a-table) | 
[Plotting data](#plotting-data) | 
[Analyzing data](#analyzing-data) 

### Starting JupyterPiDAQ

A working Jupyter notebook or Jupyter lab installation with JupyterPiDAQ 
installed is required. If you need to install the software see the [Installation 
Instructions](https://jupyterphysscilab.github.io/JupyterPiDAQ/jupyterpidaq.html#installation). There are two common ways this may be set 
up, that lead to slightly different steps for starting the software:
1. *A special kernel* may be set up that can be used in any Jupyter notebook 
   install for the current user (see the very end of the
   [Installation Instructions](https://jupyterphysscilab.github.io/JupyterPiDAQ/jupyterpidaq.html#installation)). 
   * In this case launch
   Jupyter, in whichever directory you want to work, using the 
   command: `jupyter nbclassic` (for the old notebook interface) or `jupyter 
     lab` (for the newer lab interface).
   * Open a new notebook and choose the kernel 
   for `JupyterPiDAQ`. The kernel name will depend upon what was chosen 
   during installation.
2. **Only for use within the directory structure of the virtual environment** 
   that was set up for the software. 
   * In this case you must navigate to the 
   directory of the virtual environment using the `cd` command before 
   starting the software.
   * Then enter the virtual environment with the command `pipenv shell`. 
       This assumes you set up `pipenv` as described in the 
       [Installation instructions](https://jupyterphysscilab.github.io/JupyterPiDAQ/jupyterpidaq.html#installation).
   * Launch Jupyter using the command: `jupyter nbclassic` (for the old 
     notebook interface) or `jupyter lab` (for the newer lab interface).
   * Open a new python notebook.

### Initialize the Data Acquisition Tools

Initialize the data acquisition tools by putting the statement `from 
jupyterpidaq.DAQinstance import *` into the first cell and clicking on the 
'Run' button. The package loads supporting packages (numpy, pandas, plotly,
etc...) and searches for compatible hardware. On a Raspberry Pi this takes a
number of seconds. If no compatible A-to-D boards are found, demo mode is used.
In demo mode the A-to-D board is simulated by a random number generator.

When setup is done a new menu appears at the end of the menubar (figure 1).

![DAQ Menu](DAQmenu.png)

**Figure 1**: The menu created once the data acquisition software is 
initialized. Currently NOT available in Jupyter Lab.

The menu options insert jupyter widget based GUIs for starting a run,
displaying the data as tables or plots, composing an expression to calculate
a new column in a DataFrame, or fitting data.

### Collecting data
**Using the Menu**

From the "DAQ Commands" menu select "Insert New Run After Selection..." or 
"Append New Run to End...". The first will insert the code to set up 
data collection for a run in the cell below the currently selected cell. 
The second will append this to the end of the notebook. When the cell is 
run it will generate 
a GUI that looks like the figure 2, below. Fill in the information to define 
what you wish to do (see below figure 2 for more details).

**Using a Command**

In the cell you wish to collect the data enter the command 
`Run("desired_dataset_name")`, where you replace desired_dataset_name with the 
string you want for this run. Replacing spaces with _ will prevent issues, 
especially on Windows. After entering the command, run the cell. This will 
generate the GUI shown in figure 2.

<img src="newrun.png" alt="New Run Figure" style="width:100%;">

**Figure 2**: Image of the GUI for setting up a data collection run.
1. Give the run a title/name using the first textbox.
2. You can collect up to four (4) data traces at once. Two different data 
   traces can display the same analog-to-digital channel, but in different 
   units (e.g. you could record both the raw voltage and temperature from a 
   thermistor). Each trace is activated by selecting its checkbox.
3. Once a trace is activated you can give it a title and must select: the 
   data acquisition board, channel, sensor, units and gain from the 
   available drop-down menus.
4. Once all your traces are set up decide whether they should be displayed in 
   multiple stacked graphs or all on the same graph. Uncheck the box to 
   display all on one graph.
5. Select the data collection rate (20 Hz is currently the maximum rate, but 
   on a Raspberry Pi you may not be able to sustain more than 5 Hz).
6. When everything is set the way you wish, click on the "Set Parameters" 
   button. The collection parameters will be displayed and a button to 
   start the data collection will appear. You may have to scroll back up to 
   the display as Jupyter sometimes jumps too far down when a cell is updated.
7. The "start" button will convert to a "stop" button once data collection 
   is started. The data graph(s) will update at roughly 1 Hz, so you can 
   monitor the progress of the data collection.
8. Click the "stop" button to end data collection. It can take 
   a while to stop if the data collection has got ahead of the graphic 
   display of the data.
9. Once collection is stopped you will see a plot or plots of the completed 
   data collection and the name of the .html file the raw data has been 
   backed up to.
10. Should you accidentally clear the output of a completed collection cell,
    rerunning it will regenerate the display as long as you have not moved 
    the raw data backup file.

### Displaying data

#### In a table

Selecting the "Show data in table..." option in the "DAQ Command" menu will 
insert a cell immediately below the currently selected cell displaying a 
widget in which you can select which data set to display. The command 
equivalent is `showDataTable()`.

#### Plotting data

Selecting the "Insert new plot after selection..." option in the menu will
insert two cells immediately below the currently selected cell. The first cell
will be used to generate a GUI to lead you through creation of the code to
generate the plot. The second cell is where the plot creation code is 
generated. The first tab of this GUI looks like figure 3. The command 
equivalent is `newPlot()`.

![Plot GUI](plot_GUI.png)

**Figure 3**: Image of the first tab in the four tab (4 step) Pandas Plot 
Composer. More information in the [Pandas_GUI
documentation](https://jupyterphysscilab.github.io/jupyter_Pandas_GUI/).

It is best to do the tabs in order. The notices in red will try to 
warn you of errors or oversights. The "Instructions" accordian can be 
expanded to get more specific information about how to use each tab.

You can get more sophisticated control of 
your plot by editing the code produced by this GUI. See the [Plotly 
FigureWidget Instructions](https://plotly.com/python/figurewidget/) and the 
example Jupyter notebooks referenced there for more information.

The GUI destroys itself once you complete step 4.

### Analyzing data

#### Calculating a new column

Selecting "Calculate new column..." from the menu will add two cells
immediately below the selected cell. The first cell will create the GUI to
lead you through creation of the code to calculate the new column. The second
cell is where the code is built. The first tab of the GUI looks like 
figure 4. The command equivalent is `newCalculatedColumn()`.

![New Column GUI](new_col_GUI.png)

**Figure 4**: Image of the first tab in the four tab (4 step) Pandas New 
Calculated Column Composer. More information in the [Pandas_GUI
documentation](https://jupyterphysscilab.github.io/jupyter_Pandas_GUI/).

Do the tabs in order. You can perform more complex manipulations than built 
into the GUI by editing the code generated by this GUI.

The GUI destroys itself once you complete step 4.

#### Fitting data

A GUI for defining simple fits (linear, polynomial, exponential decay, sine 
and Gaussian) can be launched by selecting "Insert new Fit after selection..
." from the menu. This will create the GUI to lead you through selecting 
and fitting the data. The code is created in the cell immediately below the 
GUI. The command equivalent is `newFit()`.

![Fit Pandas GUI](fit_gaussian_tab1.png)

**Figure 5**: Image of the first tab in the Pandas Fit Composer.
More information in the [Pandas_GUI
documentation](https://jupyterphysscilab.github.io/jupyter_Pandas_GUI/).