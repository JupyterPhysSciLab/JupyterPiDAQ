# Random ideas and notes about direction

1. Self deletion of settings. May require changing things a little. Could 
  bury settings that are transferable in a `config` object within each run. 
  That could make the copying code more succinct.
   * Current behavior is to call `run.setup()` and build the collection 
     widget in the same cell.
   * Setup should put some html with an id into this cell and then insert 
     into a new cell below it the code to get the collection widget running.
   * This new cell should also display the html of the run parameters.
   * Once the new cell is setup the first cell should run the new cell 
     followed by deleting the setup cell. This will prevent the shutdown 
     setup widgets from leaving garbage in the notebook.

2. Events with manual triggering
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

3. Copy settings from a previous run.
   * Drop down defaulting to 'NONE'.
   * On selection sets parameters to match (deep copy, so that changes made 
     to them will not impact previous run).

4. Consider storing list of all associated data and external files in the 
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