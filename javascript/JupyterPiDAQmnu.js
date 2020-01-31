function insertnewRun(){
    //Insert a cell below the current selection
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
    currentcell.set_text('newRun()');
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
    if(lastcell.get_text()==''){
        lastcell.set_text('newRun()');  
    }else{
        Jupyter.notebook.insert_cell_below();
        Jupyter.notebook.select_next(true);
        Jupyter.notebook.focus_cell();
        lastcell=Jupyter.notebook.get_cell(lastcellidx+1);
        lastcell.set_text('newRun()');
    }
    lastcell.execute()
}

function showDataTable(){
    //find the currently active cell
    var currentcell = Jupyter.notebook.get_selected_cell();
    //append the command to the end of the cell
    var currentcelltxt=currentcell.get_text();
    if (currentcelltxt!=''){
        currentcelltxt+='\n'
    }
    currentcelltxt+='showDataTable()';
    currentcell.set_text(currentcelltxt);
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
            if (lastvalue=='Show a data table...'){
                showDataTable()
            }
        }
        var optiontxt = '<option title="Insert data aquisition related command.">DAQ Commands</option>';
        optiontxt+='<option title="Insert cell below selected and start new run.">Insert New Run after selection...</option>'
        optiontxt+='<option title="Add new run at end of notebook.">Append New Run to end...</option>';
        optiontxt+='<option title="Insert show data table command at end of current cell.">Show a data table...</option>';
        newselect.innerHTML=optiontxt;
        document.getElementById('maintoolbar-container').appendChild(newselect);
    }
}