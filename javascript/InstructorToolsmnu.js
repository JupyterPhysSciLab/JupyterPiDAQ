function createInstructorToolsMenu(){
    if(!document.getElementById('InstructorToolsmnu')){
        var newselect=document.createElement('select');
        newselect.id = 'InstructorToolsmnu';
        newselect.classList.add('form-control'); //class to match notebook formatting
        newselect.classList.add('select-xs'); //class to match notebook formatting
        newselect.onchange=function(){
            var lastvalue = this.value;
            this.value='Instructor Tools';
            if (lastvalue=='Insert Data Table...'){
                get_table_dim();
            }
            if (lastvalue=='Protect Selected Cells'){
                protect_selected_cells();
            }
            if (lastvalue=='Deprotect Selected Cells'){
                deprotect_selected_cells();
            }
            if (lastvalue=='Indicate Protected Cells'){
                mark_protected_cells();
            }
            if (lastvalue=='Deactivate this menu'){
                deleteInstructorToolsMenu();
            }
        }
        var optiontxt = '<option title="Insert an Instructor Tool.">Instructor Tools</option>';
        optiontxt+='<option title="Insert cell below selected and create a data entry table.">Insert Data Table...</option>';
        optiontxt+='<option title="Prevent editting of selected cells.">Protect Selected Cells</option>';
        optiontxt+='<option title="Allow editting of selected cells.">Deprotect Selected Cells</option>';
        optiontxt+='<option title="Temporarily highlight protected cells in pink.">Indicate Protected Cells</option>';
        optiontxt+='<option>----</option>';
        optiontxt+='<option title="Remove/deactivate this menu. Use python command `from InstructorTools import *` to reactivate">'
        optiontxt+='Deactivate this menu</option>';
        newselect.innerHTML=optiontxt;
        document.getElementById('maintoolbar-container').appendChild(newselect);
    }
}

function deleteInstructorToolsMenu(){
    if(document.getElementById('InstructorToolsmnu')){
        document.getElementById('InstructorToolsmnu').remove();
    }
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if(celllist[i].get_text().indexOf('from InstructorTools import *') !== -1){
            //delete the cell
            var cellindex=Jupyter.notebook.find_cell_index(celllist[i]);
            //alert('cellindex: '+cellindex)
            Jupyter.notebook.delete_cell(cellindex);
        }
        if(celllist[i].get_text().indexOf('instmenu_act()') !== -1){
            //delete the cell
            var cellindex=Jupyter.notebook.find_cell_index(celllist[i]);
            //alert('cellindex: '+cellindex)
            Jupyter.notebook.delete_cell(cellindex);
        }
    }
}

function protect_selected_cells(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        celllist[i].metadata.editable=false;
        celllist[i].element.children()[0].setAttribute("style","background-color:pink;");
        }
}

function deprotect_selected_cells(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        celllist[i].metadata.editable=true;
        celllist[i].element.children()[0].removeAttribute("style");
    }
}

function mark_protected_cells(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.editable==false){
        celllist[i].element.children()[0].setAttribute("style","background-color:pink;");
        } else {
        celllist[i].element.children()[0].removeAttribute("style");
        }
    }
}