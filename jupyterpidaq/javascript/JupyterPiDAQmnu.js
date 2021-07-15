var insertruncount = 0
var newrunstr = 'fig$ = go.FigureWidget() # Create figure to show data.\n'
newrunstr += 'newRun(fig$) # Initiate run setup.\n'
newrunstr += 'fig$ # Display the live figure.'

function insertnewRun(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
    insertruncount += 1
    var cmdstr = newrunstr.replaceAll('$',insertruncount)
    currentcell.set_text(cmdstr);
    currentcell.execute()
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
    var cmdstr = newrunstr.replaceAll('$',insertruncount)
    if(lastcell.get_text()==''){
        lastcell.set_text(cmdstr);
    }else{
        Jupyter.notebook.insert_cell_below();
        Jupyter.notebook.select_next(true);
        Jupyter.notebook.focus_cell();
        lastcell=Jupyter.notebook.get_cell(lastcellidx+1);
        lastcell.set_text(cmdstr);
    }
    lastcell.execute()
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
    currentcell.execute()
}

function newCalculatedColumn(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
     currentcell.set_text('newCalculatedColumn()');
    currentcell.execute()
}

function newPlot(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
     currentcell.set_text('newPlot()');
    currentcell.execute()
}

function createCmdMenu(){
    if(!document.getElementById('jupyterpiDAQcmdsmnu')){
        var newselect=document.createElement('select');
        newselect.id = 'jupyterpiDAQcmdsmnu';
        newselect.classList.add('form-control'); //class to match notebook formatting
        newselect.classList.add('select-xs'); //class to match notebook formatting
        newselect.onchange=function(){
            var lastvalue = this.value;
            this.value='DAQ Commands';
            if (lastvalue=='Insert New Run after selection...'){
                insertnewRun()
            }
            if (lastvalue=='Append New Run to end...'){
                addnewRun()
            }
            if (lastvalue=='Show data in table...'){
                showDataTable()
            }
            if (lastvalue=='Calculate new column...'){
                newCalculatedColumn()
            }
            if (lastvalue=='Insert new plot after selection...'){
                newPlot()
            }
        }
        var optiontxt = '<option title="Insert data aquisition related command.">DAQ Commands</option>';
        optiontxt+='<option title="Insert cell below selected and start new run.">Insert New Run after selection...</option>';
        optiontxt+='<option title="Add new run at end of notebook.">Append New Run to end...</option>';
        optiontxt+='<option title="Insert show data table command at end of current cell.">Show data in table...</option>';
        optiontxt+='<option title="Calculate new column below current cell.">Calculate new column...</option>';
        optiontxt+='<option title="New plot below current cell.">Insert new plot after selection...</option>';
        newselect.innerHTML=optiontxt;
        if(document.getElementById('maintoolbar-container')){ //classic Jupyter
            document.getElementById('maintoolbar-container').appendChild(newselect);
        }
        if(document.getElementsByClassName('jp-NotebookPanel-toolbar')){ //JLab
            document.getElementsByClassName('jp-NotebookPanel-toolbar')[0]
            .appendChild(newselect); // If there is more than one only add to
            //first.
        }
    }
}

function deleteCmdMenu(){
    if(document.getElementById('jupyterpiDAQcmdsmnu')){
        document.getElementById('jupyterpiDAQcmdsmnu').remove();
    }
}