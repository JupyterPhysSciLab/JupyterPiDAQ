#Python to generate a table that the user can input data into in a Jupyter
# notebook. Requires input_table.js.
# Jonathan Gutow <gutow@uwosh.edu> March 24, 2019
# license GPL V3 or greater

from IPython.display import HTML
from IPython.display import Javascript as JS

import time

#load the supporting javascript
tempJSfile=open('input_table.js')
tempscript='<script type="text/javascript">'
tempscript+=tempJSfile.read()+'</script>'
tempJSfile.close()
display(HTML(tempscript))

class input_table():
    def __init__(self,columnlabels=['A','B','C'], rowlabels=['1','2','3'],mode='warn'):
        self.mode=mode #will be used for error reporting level
        self.ID='it_'+str(round(time.time()))
        if (self.mode=='debug'):
            print('Id='+self.ID)
        self.rowlbls=rowlabels
        self.collbls=columnlabels
        self.nrows=len(self.rowlbls)+1
        self.ncols=len(self.collbls)+1
        
    def set_rows(self,labels):
        self.rowlbls=labels
        self.nrows=len(self.rowlbls)+1
    
    def set_columns(self,labels):
        self.collbls=labels
        self.ncols=len(self.colbls)+1
        
    def htmlstr(self):
        tempstr='<table class="input_table" id="'+self.ID+'"><tbody>\n';
        for i in range (0,self.nrows):
            tempstr+=' <tr class="input_table r'+str(i)+'">\n'
            for k in range(0,self.ncols):
                if (k==0 and i==0):
                    tempstr+='  <td class="input_table r'+str(i)+' c'+str(k)+'">'
                    tempstr+='<button onclick="save_input_table(\''+self.ID+'\')">'
                    tempstr+='Save Updates</button></td>\n'                       
                if (k==0 and i>0):
                    tempstr+='  <td class="input_table r'+str(i)+' c'+str(k)+'">'
                    tempstr+=self.rowlbls[i-1]+'</td>\n'
                if (i==0 and k>0):
                    tempstr+='  <td class="input_table r'+str(i)+' c'+str(k)+'">'
                    tempstr+= self.collbls[k-1]+'</td>\n'                
                if (k>0 and i>0):
                    tempstr+='  <td class="input_table r'+str(i)+' c'+str(k)+'">'
                    tempstr+='<input type="text" size="7"'
                    tempstr+=' onblur="record_input(this)"></input></td>\n'
            tempstr+=' </tr>\n'
        tempstr+='</tbody></table>'
        return(tempstr)