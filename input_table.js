//Javascript for input_table to use in Jupyter notebook
//Jonathan Gutow <gutow@uwosh.edu> March 24, 2019
//license GPL V3 or greater.

//Update html on change of cell content.
 function record_input(element){
    var tempval = element.value;
    var tempsize = element.size;
    if (tempsize==null){tempsize=7};
    var tempclass = element.className;
    if (tempclass==null){tempclass=''};
    var parent = element.parentElement;
    var htmlstr = '<input class="'+tempclass+'" type="text" size="'+tempsize+'"';
    htmlstr+='" value="'+tempval+'" onblur="record_input(this)"></input>';
    parent.innerHTML=htmlstr;
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
    var re=/\n/g
    var re2=/'/g
    tablestr+=tablecnt.replace(re,' ').replace(re2,'\\\'')+'</table>';
    tablestr+='\'))';
    currentcell.set_text(tablestr);
    Jupyter.notebook.execute_selected_cells();
}