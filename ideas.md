# Random ideas and notes about direction

1. Events with manual triggering
   * Stabilization guage: display the slope on an indicator dial with a 
     range of +/- 10X noise level on first point (5 s moving average 
     updated every second?).
   * Digital display of last measurement updated at a minimum of 1 Hz.
   * Set delay time after manual collection click (0 seconds or more in 
     steps of 1 second).
   * Data added to standard self-updating plot.
   * User can choose X - axis.
   * User can choose to collect one or more channels (will have to pick a 
     channel for the slope and value display).
   * User can have more than one column of manual data input.

2. Copy settings from a previous run.
   * Drop down defaulting to 'NONE'.
   * On selection sets parameters to match (deep copy, so that changes made 
     to them will not impact previous run).

3. Consider storing list of all associated data and external files in the 
  notebook metadata. This could then be used to zip up an experiment that can 
  be transferred as one file to any other jupyter server.
   * May also be able to implement a way to reload the notebook with the 
     initial raw datasets loaded in.
   * Could possibly save things in a way that the state of dataframes could 
     be recovered. However, I am not sure we really want to do that. In a 
     research lab situation it is probalby best to make a new copy of the 
     notebook reload the data and reprocess it, rather than making changes 
     to an existing notebook. This maintains a better record of what was 
     done. Maybe a way to clearly continue, but force saving of a checkpoint?
   * This could save state as a bundle that could rebuild dataframes and 
     DAQinstances, but I do not see a way to cleanly reproduce the state of 
     any other variables.
   * From a usability standpoint this needs to work. Maybe initialization 
     reloads the most recent versions of the data sets.
   * Save bundle should be a .gz with data files an html representation and 
     the .ipynb. Maybe a .jpsl.gz file?
4. `.jpsl.gz` definition: file containing .ipynb, html representation of it,
   .csv of any plain dataframes and .html of any DAQinstances.
   * Should running initialization load everything in this or should they 
     just be available?