#Python to generate a table that the user can input data into in a Jupyter
# notebook. Requires input_table.js.
# Jonathan Gutow <gutow@uwosh.edu> Feb. 3, 2020
# license GPL V3 or greater

from IPython.display import HTML

import os

#Locate input_table package directory
mydir=os.path.dirname(__file__) #absolute path to directory containing this file.

#load the supporting javascript
tempJSfile=open(os.path.join(mydir,'javascript','input_table.js'))
tempscript='<script type="text/javascript">'
tempscript+=tempJSfile.read()+'</script>'
tempJSfile.close()
display(HTML(tempscript))