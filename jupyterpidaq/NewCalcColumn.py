"""
GUI for generating the code for a new calculated column in a Pandas Dataframe.
"""
from ipywidgets import widgets, Layout

class NewCalcColumn():
    def __init__(self, runs):
        self.runs = runs
        self.whichrun = None
        runlst = [('Choose Run', -1)]
        for i in range(len(runs)):
            runlst.append((str(i + 1) + ': ' + runs[i].title, i))
        self.runsdrp = widgets.Dropdown(
            options=runlst,
            value=-1,
            description='Select Run #:',
            disabled=False,
        )
        self.runsdrp.observe(self.runchanged,names = 'value')
        self.columns = None
        self.columnsdrp = widgets.Dropdown(
            options =  self.columns,
            description = 'Select column to add to expression.',
            disabled = False,
        )
        self.columnsdrp.observe(insert_column,names='value')
        self.expression = widgets.Text(
            value = '',
            placeholder = 'Command to create column will be built here.',
            description = '',
            disabled = False,
        )

    def runchanged(self, change):
        self.whichrun = self.runsdrp.value
        self.columns = self.runs[whichrun].pandadf.columns
        self.columsdrp.options = self.columns
        pass

    def insert_column(self,change):
        self.expression