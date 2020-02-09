//Javascript for input_table to use in Jupyter notebook
//Jonathan Gutow <gutow@uwosh.edu> March 24, 2019
//license GPL V3 or greater.

//Get input table dimensions and build
function get_table_dim(){
    Jupyter.notebook.insert_cell_below();
    Jupyter.notebook.select_next(true);
    Jupyter.notebook.focus_cell();
    var currentcell = Jupyter.notebook.get_selected_cell();
    var htmlstr =`
    <div id="input_table_dim_dlg" style="border:thick;border-color:red;border-style:solid;">
      <div>Set table size remembering to include enough rows and columns for labels.</div>
      <table id="init_input_table_dim"><tr>
        <td> Rows:</td><td><input id="init_row_dim" type="text" size="7" value="2"
          onblur="record_input(this)"></input></td>
        <td>Columns:</td><td><input id="init_col_dim" type="text" size="7" value="2"
          onblur="record_input(this)"></input></td>
        <td><button onclick="create_table()">Create Table</button></td>
      </tr></table>
    </div>`
    currentcell.set_text('display(HTML("""'+htmlstr+'"""))');
    currentcell.execute();
}

//Update html on change of cell content.
function record_input(element){
    var tempval = ''+element.value;//force to string
    var tempsize = ''+element.size;
    if (tempsize==null){tempsize='7'};
    var tempclass = element.className;
    if (tempclass==null){tempclass=''};
    var tempid = element.id;
    if (tempid==null){tempid=''};
    var tempelem = document.createElement('input');
    tempelem.className =tempclass;
    tempelem.id=tempid;
    tempelem.setAttribute('size',tempsize);
    tempelem.setAttribute('value',tempval);
    tempelem.setAttribute('onblur','record_input(this)');
    element.replaceWith(tempelem);
}

// Convert table input element to fixed value.
function input_element_to_fixed(element){
    var tempval = element.value;
    var tempelem =document.createElement('span');
    tempelem.innerHTML = tempval;
    element.replaceWith(tempelem);
}

function lock_labels(tableID){
//Will need to use querySelectorAll(css)
    var parentTable = document.getElementById(tableID);
    var labelinputs = parentTable.querySelectorAll('.table_label');
    for(var i=0;i<labelinputs.length;i++){
        input_element_to_fixed(labelinputs[i]);
    }
    var lockbtn = parentTable.querySelector('.lock_btn');
    var tempelem = document.createElement('button');
    tempelem.classList.add('save_btn');
    var onclickstr = "save_input_table('"+tableID+"')"
    tempelem.setAttribute('onclick',onclickstr);
    tempelem.innerHTML='Save Updates';
    lockbtn.replaceWith(tempelem);
    save_input_table(tableID);
}
//Create the table using the info collected in the dimension table.
function create_table(){
    var nrows = document.getElementById("init_row_dim").value;
    var ncols = document.getElementById("init_col_dim").value;
    document.getElementById("input_table_dim_dlg").remove();
    //alert(nrows+', '+ncols)
    var d = new Date();
    var ID = 'it_'+(Math.round(d.getTime()));
    var labelClass = 'table_label';
    var tempstr='<table class="input_table" id="'+ID+'"><tbody>';
    for(var i = 0; i < nrows; i++){
        tempstr+=' <tr class="input_table r'+i+'">';
        for(var k = 0;k < ncols; k++){
            if (k==0 && i==0){
                tempstr+='  <td class="input_table r'+i+' c'+k+'">';
                tempstr+='<button class="lock_btn" onclick="lock_labels(\\\''+ID+'\\\')">';
                tempstr+='Lock Column and Row Labels</button></td>';
            }
            if (k==0 && i>0){
                tempstr+='<td class="input_table r'+i+' c'+k+'">';
                tempstr+='<input class="'+labelClass+'" type="text" size="7" value="'+(i-1)+'"';
                tempstr+=' style="font-weight:bold;"';
                tempstr+=' onblur="record_input(this)"></input></td>';
            }
            if (i==0 && k>0){
                tempstr+='<td class="input_table r'+i+' c'+k+'">';
                tempstr+='<input class="'+labelClass+'" type="text" size="15" value="Col_'+(k-1)+'"';
                tempstr+=' style="font-weight:bold;"';
                tempstr+=' onblur="record_input(this)"></input></td>';
            }
            if (k>0 && i>0){
                tempstr+='  <td class="input_table r'+i+' c'+k+'">';
                tempstr+='<input type="text" size="7"';
                tempstr+=' onblur="record_input(this)"></input></td>';
            }
        }
        tempstr+=' </tr>';
    }
    tempstr+='</tbody></table>';
    var currentcell = Jupyter.notebook.get_selected_cell();
    currentcell.set_text('display(HTML(\''+tempstr+'\'))');
    currentcell.execute();
}

//Save table by making the code cell create it. Actuated by button.
//***For this to work the following two imports need to be made into
//   the jupyter notebook by the python code that utilizes this function:
//   from IPython.display import HTML
//   from IPython.display import Javascript as JS

function save_input_table(tableID){
    var currentcell = Jupyter.notebook.get_selected_cell();
    var tablecnt = document.getElementById(tableID).innerHTML;
    var tablestr='display(HTML(\''
    tablestr+='<table class="input_table" id="'+tableID+'">';
    var re=/\n/g;
    var re2=/'/g;
    tablestr+=tablecnt.replace(re,' ').replace(re2,'\\\'')+'</table>';
    tablestr+='\'))';
    currentcell.set_text(tablestr);
    Jupyter.notebook.execute_selected_cells();
}