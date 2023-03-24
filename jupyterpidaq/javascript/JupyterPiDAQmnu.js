// TODO: isolate under a name such as juputerPiDAQ.
var insertruncount = 0
var newrunstr = '# EDIT THE COMMAND BELOW BY PROVIDING A RUN NAME.\n'
newrunstr += '# The name should be surrounded by double quotes ("run_name").\n'
newrunstr += '# using _ instead of spaces will avoid problems, especially on '
newrunstr += 'Windows machines.\n'
newrunstr += 'Run("REPLACE_ME_WITH_NAME_FOR_RUN") # Initiate run or load a '
newrunstr += 'completed run.'

function insertnewRun(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
    insertruncount += 1
    var cmdstr = newrunstr
    currentcell.set_text(cmdstr);
    //currentcell.execute();
}

function addnewRun(){
    //find the last cell in notebook
    var lastcellidx = Jupyter.notebook.ncells()-1;
    var lastcell=Jupyter.notebook.get_cell(lastcellidx);
    Jupyter.notebook.select(lastcellidx);
    //If the cell is empty put command in it. Otherwise
    //add another cell at the end of the worksheet. Then
    //put the command in the new lastcell.
    insertruncount += 1
    var cmdstr = newrunstr
    if(lastcell.get_text()==''){
        lastcell.set_text(cmdstr);
    }else{
        Jupyter.notebook.insert_cell_below();
        Jupyter.notebook.select_next(true);
        Jupyter.notebook.focus_cell();
        lastcell=Jupyter.notebook.get_cell(lastcellidx+1);
        lastcell.set_text(cmdstr);
    }
    //lastcell.execute();
}

function showDataTable(){
    //find the currently active cell
    var currentcell = Jupyter.notebook.get_selected_cell();
    //Because we could destroy date created by having run
    //this cell previously do not use this cell if it contains
    //anything
    if (currentcell.get_text()==''){
        currentcell.set_text('showDataTable()');
    }else{
        Jupyter.notebook.insert_cell_below();
        Jupyter.notebook.select_next(true);
        Jupyter.notebook.focus_cell();
        currentcell = Jupyter.notebook.get_selected_cell();
        currentcell.set_text('showDataTable()');
    }
    currentcell.execute();
}

function newCalculatedColumn(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
     currentcell.set_text('newCalculatedColumn()');
    currentcell.execute();
}

function newPlot(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
     currentcell.set_text('newPlot()');
    currentcell.execute();
}

function newFit(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
     currentcell.set_text('newFit()');
    currentcell.execute();
}
function protect_selected_cells(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        celllist[i].metadata.editable=false;
        }
}

function createCmdMenu(){
    if(!document.getElementById('DAQ_commands')){
        var instrun = {'type':'action',
                            'title':'Insert New Run after selection...',
                            'data':"insertnewRun();"
                          };
        var appendrun = {'type':'action',
                         'title':'Append New Run to end...',
                         'data':"addnewRun();"
                          };
        var showdata = {'type':'action',
                        'title':'Show data in table...',
                        'data':"showDataTable();"
                        };
        var calccol = {'type':'action',
                       'title':'Calculate new column...',
                       'data':"newCalculatedColumn();"
                        };
        var istplt = {'type':'action',
                       'title':'Insert new plot after selection...',
                       'data':"newPlot();"
                        };
        var istfit = {'type':'action',
                       'title':'Insert new fit after selection...',
                       'data':"newFit();"
                        };
        var menu = {'type':'menu',
                    'title':'DAQ commands',
                    'data':[instrun, appendrun, showdata, calccol, istplt,
                    istfit]
                    };
        JPSLMenus.build(menu);
    }
}

function deleteCmdMenu(){
    if(document.getElementById('DAQ_commands')){
        document.getElementById('DAQ_commands').remove();
    }
}