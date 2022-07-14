# Tools for using a Jupyter notebook as a lab notebook that collects and
# displays data from an analog to digital converter in real time. The interface
# also allows for annotation, analysis and display of the data using common
# python tools. Common activities can be done using menus and buttons rather
# than typing python commands.
# J. Gutow <gutow@uwosh.edu> July 2021
# license GPL V3 or greater.

######
# Environment setup
######
# Use os tools for file path and such
import os
import time
import logging

# Start Logging
import JPSLUtils

logname = 'DAQinstance_' + time.strftime('%y-%m-%d_%H%M%S',
                                         time.localtime()) + '.log'
logging.basicConfig(filename=logname, level=logging.INFO)

# below is equivalent to %matplotlib notebook in a Jupyter cell
from IPython import get_ipython

ipython = get_ipython()
print('Importing drivers and searching for available data acquisition '
      'hardware.',end='')

# imports below must work. Allow normal python error response.
import ipywidgets as widgets
from pandas_GUI import *
print ('.',end='')

from plotly import io as pio
pio.templates.default = "simple_white" #default plot format
from plotly import graph_objects as go
print ('.',end='')

import numpy as np
print ('.',end='')

import pandas as pd
print ('.',end='')

from IPython.display import display, HTML
from IPython.display import Javascript as JS

print ('.',end='')

# Below allows asynchronous calls to get and plot the data in real time.
# Actually read the DAQ board on a different process.
import threading
from multiprocessing import Process, Pipe

print('.',end='')

# The process that monitors the board
from jupyterpidaq.DAQProc import DAQProc

print('.',end='')

# Board definitions
from jupyterpidaq import Boards as boards

print('.',end='')

global availboards
availboards = boards.load_boards()

print('.',end='')

# GUI for settings
from jupyterpidaq.ChannelSettings import ChannelSettings

print('.',end='')

# Sensor definitions
from jupyterpidaq.Sensors import sensors

print('.',end='')

# JPSL Utilities
from JPSLMenus import *
from JPSLUtils import *

print('.',end='')

# globals to put stuff in from threads.
data = []  # all data from DAQ tools avg_values
stdev = []  # all standard deviations
timestamp = []  # all timestamps

# global list to keep track of runs
runs = []

######
# Interactive elements definitions
######

# Locate JupyterPiDAQ package directory
mydir = os.path.dirname(
    __file__)  # absolute path to directory containing this file.

# Add a "DAQ Menu" to the notebook.
tempJSfile = open(os.path.join(mydir, 'javascript', 'JupyterPiDAQmnu.js'))
tempscript = '<script type="text/javascript">'
tempscript += tempJSfile.read() + '</script>'
tempJSfile.close()
display(HTML(tempscript))
JPSLUtils.OTJS('createCmdMenu()')

print('Done with setup.')

# cleanup log file if it is empty
logging.shutdown()
try:
    if os.stat(logname).st_size == 0:
        os.remove(logname)
except FileNotFoundError:
    pass

# Data Aquistion Instance (a run).
class DAQinstance():
    def __init__(self, idno, livefig, title='None', ntraces=4, **kwargs):
        """
        Data Aquistion Instance (a run).

        :param idno : id number you wish to use to keep track
        :param livefig: plotly FigureWidget to use for live display
        :param title: optional name
        :param ntraces: number of traces (default = 4) more than 4 easily
            overwhelms a pi4.
        :param kwargs:
            :ignore_skew: bool (default: True) if True only a single average
            collection time will be recorded for each time in a multichannel
            data collection. If False a separate set of time will be
            recorded for each channel.
        """
        self.ignore_skew = kwargs.pop('ignore_skew',True)
        self.idno = idno
        self.livefig = livefig
        self.title = str(title)
        self.svname = ''
        self.averaging_time = 0.1  # seconds adjusted based on collection rate
        self.gain = [1] * ntraces
        self.data = []
        self.timestamp = []
        self.stdev = []
        self.pandadf = None
        self.ntraces = ntraces
        self.separate_plots = True
        self.traces = []
        # index map from returned data to trace,
        self.tracemap = []
        self.tracelbls = []
        self.units = []
        for i in range(self.ntraces):
            self.traces.append(ChannelSettings(i, availboards))
        self.ratemax = 20.0  # Hz
        self.rate = 1.0  # Hz
        self.deltamin = 1 / self.ratemax
        self.delta = 1.0 / self.rate
        self.setupbtn = widgets.Button(
            description='Set Parameters',
            disabled=False,
            button_style='info',
            # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click to set collection parameters to displayed values.',
            icon='')
        self.collectbtn = widgets.Button(
            description='Start Collecting',
            disabled=False,
            button_style='success',
            # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Start collecting data and plotting it. '
                    'Will make new graph.',
            icon='')
        self.separate_traces_checkbox = widgets.Checkbox(
            value = self.separate_plots,
            description = 'Display multiple traces as stacked graphs. ' \
                        'Uncheck to display all on the same graph.',
            layout = widgets.Layout(width='80%'),
            disabled = False)
        self.rateinp = widgets.BoundedFloatText(
            value=self.rate,
            min=0,
            max=self.ratemax,
            step=self.ratemax / 1000.0,
            description='Rate (Hz):',
            disabled=False)
        self.timelbl = widgets.Text(
            value='Time(s)',
            placeholder='Type something',
            description='X-axis label (time):',
            disabled=False)
        self.runtitle = widgets.Text(
            value=self.title,
            placeholder='Type title/description',
            description='Run title',
            disabled=False)
        self.defaultparamtxt = ''
        self.defaultcollecttxt = '<span style="color:blue;"> To accurately '
        self.defaultcollecttxt += 'read point location on graph you can zoom '
        self.defaultcollecttxt += 'in. Drag to zoom. Additional controls show '
        self.defaultcollecttxt += 'above plot when you hover over it.</span>'
        self.collecttxt = widgets.HTML(
            value=self.defaultcollecttxt,
            placeholder='',
            description='')
        self.setup_layout_bottom = widgets.HBox(
            [self.rateinp, self.timelbl, self.setupbtn])
        self.setup_layout = widgets.VBox([self.separate_traces_checkbox,
                                          self.setup_layout_bottom])
        self.collect_layout = widgets.HBox([self.collectbtn, self.collecttxt])
        
    def _make_defaultparamtxt(self):
        """
        Uses AdvancedHTMLParser (mimics javascript) to generate valid HTML for
        the default parameter text.
        :return: valid html string for the default parameter text.
        """
        from AdvancedHTMLParser import AdvancedTag as domel
        run_info=domel('div')
        run_info.setAttribute('id','DAQRun_' + str(self.idno) + '_info')
        run_info.setAttribute('class','run_info')
        run_id = domel('table')
        run_id.setAttribute('id','run_id')
        run_id.setAttribute('border', '1')
        tr = domel('tr')
        tr.appendInnerHTML('<th>Title</th><th>Id #</th>')
        run_id.appendChild(tr)
        tr = domel('tr')
        tr.appendInnerHTML('<td>' + str(self.title) + '</td>' \
                            '<td>' + str(self.idno) + '</td>')
        run_id.appendChild(tr)
        run_info.appendChild(run_id)
        # table of run parameters
        run_param = domel('table')
        run_param.setAttribute('border','1')
        run_param.setAttribute('id','run_param')
        tr = domel('tr')
        tr.setAttribute('style','text-align:center;')
        tr.appendInnerHTML('<th>Approx. Rate (Hz)</th>' \
                                '<th>Approx. Delta (s)</th>' \
                                '<th>X-label </th>' \
                                '<th>X-cols</th>' \
                                '<th>Y-cols</th>' \
                                '<th>err-cols<sup ' \
                                'style="color:blue;">a</sup></th>' \
                                '<th>One Plot</th>' )
        run_param.appendChild(tr)
        run_info.appendChild(run_param)
        tr = domel('tr')
        tr.setAttribute('style','text-align:center;')
        tr.appendInnerHTML('<td>' + str(self.rate) + '</td>' \
                            '<td>' + str(self.delta) + '</td>' \
                            '<td>' + self.timelbl.value + '</td>')
        xlist = '['
        ylist = '['
        errlist = '['
        if self.ignore_skew:
            xlist += '0]'
            tempcount = 0
            for k in self.traces:
                if k.isactive:
                    ylist += str(2 * tempcount + 1) + ','
                    errlist += str(2 * tempcount + 2) + ','
                    tempcount += 1
            ylist = ylist[:-1] + ']'
            errlist = errlist[:-1] + ']'
        else:
            tempcount = 0
            for k in self.traces:
                if k.isactive:
                    xlist += str(3 * tempcount) + ','
                    ylist += str(3 * tempcount + 1) + ','
                    errlist += str(3 * tempcount + 2) + ','
                    tempcount += 1
            xlist = xlist[:-1] + ']'
            ylist = ylist[:-1] + ']'
            errlist = errlist[:-1] + ']'
        tr.appendInnerHTML('<td>' + xlist + '</td><td>' + ylist + '</td>')
        td = domel('td')
        td.appendText(errlist)
        tr.appendChild(td)
        td = domel('td')
        td.appendText(str(not (self.separate_plots)))
        tr.appendChild(td)
        run_param.appendChild(tr)
        footer = domel('tfoot')
        tr = domel('tr')
        td = domel('td')
        td.setAttribute('colspan','7')
        td.appendInnerHTML('<sup style="color:blue;">a</sup>The ' \
                            'standard deviation of the number in the ' \
                            'column immediately to the left based on the ' \
                            'variation in signal during the averaging time ' \
                            'for the data point.')
        tr.appendChild(td)
        footer.appendChild(tr)
        run_param.appendChild(footer)
        # table of trace information
        traceinfo = domel('table')
        traceinfo.setAttribute('class','traceinfo')
        traceinfo.setAttribute('id','traceinfo')
        traceinfo.setAttribute('border','1')
        tr = domel('tr')
        tr.setAttribute('style','text-align:center;')
        tr.appendInnerHTML('<th>Trace #</th><th>Title</th><th>Units</th>' \
                            '<th>Board</th><th>Channel</th><th>Sensor</th>' \
                            '<th>Gain</th>')
        traceinfo.appendChild(tr)
        for i in range(self.ntraces):
            if (self.traces[i].isactive):
                self.tracemap.append(i)
                tr = domel('tr')
                tr.setAttribute('style', 'text-align:center;')
                tr.appendInnerHTML('<td>' + str(i) + '</td>' \
                            '<td>' + self.traces[i].tracelbl.value + '</td>' \
                            '<td>' + self.traces[i].units.value + '</td>' \
                            '<td>' + str(self.traces[i].boardchoice.value) + \
                            ' ' + self.traces[i].board.name + '</td>' \
                            '<td>' + str(self.traces[i].channel) + '</td>' \
                        '<td >' + self.traces[i].sensorchoice.value + '</td>' \
                            '<td>' + str(self.traces[i].gains.value) + '</td>')
                traceinfo.appendChild(tr)
        run_info.appendChild(traceinfo)
        return run_info.asHTML()
    
    def _load_from_html(self, file):
        """
        Loads data and parameters for a completed run from a saved html file.
        :param file: filename or path.
        :return:
        """
        import pandas as pd
        from JPSLUtils import find_pandas_dataframe_names
        from AdvancedHTMLParser import AdvancedHTMLParser as parser
        from plotly import graph_objects as go
        whichrun = pd.read_html(file, attrs={'id': 'run_id'})[0]
        run_title = whichrun['Title'][0]
        run_id = whichrun['Id #'][0]
        svname = pd.read_html(file, attrs={'id': 'file_info'})[0]['Saved ' \
                                                                  'as'][0]
        self.pandadf = pd.read_html(file, attrs={'class': 'dataframe'},
                                    index_col=0)[0]
        self.title = run_title
        self.svname = svname
        run_param = \
        pd.read_html(file, attrs={'id': 'run_param'}, skiprows=[2])[0]
        self.rate = run_param['Approx. Rate (Hz)'][0]
        self.delta = run_param['Approx. Delta (s)'][0]
        # reassiging timelbl to a value from a widget
        self.timelbl = run_param['X-label'][0]
        self.separate_plots = not (run_param['One Plot'][0])
        xcols = list(map(int,run_param['X-cols'][0].replace('[',
                                        '').replace(']','').split(',')))
        ycols = list(map(int,run_param['Y-cols'][0].replace('[',
                                        '').replace(']','').split(',')))
        errcols = list(map(int,run_param['err-colsa'][0].replace('[',
                                        '').replace(']', '').split(',')))
        htmldatafile = parser(file)
        self.defaultparamtxt = htmldatafile.getElementsByClassName(
            'run_info')[0].asHTML()
        traceinfo = pd.read_html(file, attrs={'id': 'traceinfo'})[0]
        for k in traceinfo.index:
            # Do not refill the widgets. This truncates and changes the
            # definitions of some things from widgets to values.
            self.traces[k].isactive = True
            self.traces[k].tracelbl= traceinfo['Title'][k]
            self.traces[k].units = traceinfo['Units'][k]
            boardchoice, boardname = (traceinfo['Board'][k]).split(' ',1)
            self.traces[k].boardchoice = boardchoice
            self.traces[k].board = boardname
            self.traces[k].channel = traceinfo['Channel'][k]
            self.traces[k].gains= traceinfo['Gain'][k]
            self.traces[k].sensor = traceinfo['Sensor'][k]
        # Plot
        if self.separate_plots:
            self.livefig.set_subplots(rows=len(ycols), cols=1,
                                                  shared_xaxes=True)
            self.livefig.update_xaxes(
                title=self.timelbl, row=len(ycols), col=1)
        else:
            self.livefig.update_xaxes(title=self.timelbl)
            self.livefig.update_yaxes(title="Values")
        for i in range(len(ycols)):
            namestr = self.pandadf.columns[ycols[i]]
            xcol = None
            if len(xcols) == 1:
                xcol = xcols[0]
            else:
                xcol = xcols[i]
            scat = go.Scatter(
                y=self.pandadf.iloc[0:, ycols[i]],
                x=self.pandadf.iloc[0:,xcol], name=namestr)
            if self.separate_plots:
                self.livefig.update_yaxes(title=self.traces[i].units,
                    row=i+1, col=1)
                self.livefig.add_trace(scat, row=i+1, col=1)
            else:
                self.livefig.add_trace(scat)
        pass

    def setupclick(self, btn):
        # Could just use the values in widgets, but this forces intentional
        # selection and locks them for the run.
        from copy import copy
        self.title = copy(self.runtitle.value)
        self.rate = copy(self.rateinp.value)
        self.delta = 1 / self.rate
        self.separate_plots = copy(self.separate_traces_checkbox.value)
        self.defaultparamtxt = self._make_defaultparamtxt()
        self.runtitle.close()
        del self.runtitle
        self.setup_layout.close()
        del self.setup_layout
        JPSLUtils.new_cell_immediately_below()
        cmdstr = 'doRun(runs[' + str(self.idno - 1) + '])'
        cmdstr += '\\nruns[' + str(self.idno - 1) + '].livefig'
        JPSLUtils.insert_text_into_next_cell(cmdstr)
        JPSLUtils.select_containing_cell("RunSetUp")
        JPSLUtils.select_cell_immediately_below()
        JPSLUtils.OTJS('Jupyter.notebook.get_selected_cell().execute()')
        pass

    def setup(self):
        display(HTML("<h3 id ='RunSetUp' "
                     "style='text-align:center;'>Set Run Parameters</h3>"))
        self.setupbtn.on_click(self.setupclick)
        display(self.runtitle)
        for i in range(self.ntraces):
            self.traces[i].setup()
        display(self.setup_layout)
        pass

    def collectclick(self, btn):
        if (btn.description == 'Start Collecting'):
            btn.description = 'Stop Collecting'
            btn.button_style = 'danger'
            btn.tooltip = 'Stop the data collection'
            # do not allow parameters to be reset after starting run.
            self.setupbtn.disabled = True
            self.setupbtn.tooltip = 'Parameters locked. The run has started.'
            self.rateinp.disabled = True
            self.timelbl.disabled = True
            thread = threading.Thread(target=self.updatingplot, args=())
            thread.start()
            # self.updatingplot() hangs up user interface
        else:
            btn.description = 'Done'
            btn.button_style = ''
            btn.tooltip = ''
            time.sleep(3)  # wait a few seconds for end of data collection
            self.data = data
            self.timestamp = timestamp
            self.stdev = stdev
            self.fillpandadf()
            # save data to html file so it is human readable and can be loaded
            # elsewhere.
            self.svname = self.title + '_' + time.strftime('%y-%m-%d_%H%M%S',
                                        time.localtime()) + '.html'
            svhtml = '<!DOCTYPE html>' \
                     '<html><body>'+ self.defaultparamtxt + \
                     '<table id="file_info" border="1"><tr><th>Saved as ' \
                     '</th></tr><tr><td>' +  \
                     self.svname+'</td></tr></table>' \
                     '<h2>DATA</h2>'+ \
                     self.pandadf.to_html() + '</body></html>'
            f = open(self.svname,'w')
            f.write(svhtml)
            f.close()
            self.collectbtn.close()
            del self.collectbtn
            #display(self.collecttxt)
            display(HTML(
                '<span style="color:blue;font-weight:bold;">DATA SAVED TO:' +
                self.svname + '</span>'))
            JPSLUtils.select_containing_cell('LiveRun_'+str(self.idno))
            JPSLUtils.new_cell_immediately_below()
            cmdstr = 'from jupyterpidaq.DAQinstance import * ' \
                    '# Does nothing if already imported.\n' \
                    'displayRun(' + str(self.idno)+', \"' \
                    + self.svname + '\") # display the data'
            JPSLUtils.insert_text_into_next_cell(cmdstr)
            JPSLUtils.select_containing_cell('LiveRun_'+str(self.idno))
            JPSLUtils.select_cell_immediately_below()
            JPSLUtils.OTJS('Jupyter.notebook.get_selected_cell().execute()')

    def fillpandadf(self):
        datacolumns = []
        temptimes = np.transpose(self.timestamp)
        tempdata = np.transpose(self.data)
        tempstdev = np.transpose(self.stdev)
        chncnt = 0
        for i in range(self.ntraces):
            if (self.traces[i].isactive):
                chncnt += 1
        for i in range(chncnt):
            if self.ignore_skew and i > 0:
                pass
            else:
                datacolumns.append(temptimes[i])
            datacolumns.append(tempdata[i])
            datacolumns.append(tempstdev[i])
        titles = []
        # Column labels.
        chncnt = 0
        for i in range(self.ntraces):
            if (self.traces[i].isactive):
                chncnt += 1
                if self.ignore_skew:
                    if chncnt == 1:
                        titles.append(self.timelbl.value)
                    pass
                else:
                    titles.append(self.traces[
                                  i].tracelbl.value + '_' + self.timelbl.value)
                titles.append(
                    self.traces[i].tracelbl.value + '(' + self.traces[
                        i].units.value + ')')
                titles.append(
                    self.traces[i].tracelbl.value + '_' + 'stdev')
        #print(str(titles))
        #print(str(datacolumns))
        self.pandadf = pd.DataFrame(np.transpose(datacolumns), columns=titles)

    def updatingplot(self):
        """
        Runs until a check of self.collectbtn.description does not return
        'Stop Collecting'. This would probably be more efficient if set a
        boolean.
        """
        starttime = time.time()
        global data
        data = []
        global timestamp
        timestamp = []
        global stdev
        stdev = []
        datalegend = []
        timelegend = []
        stdevlegend = []
        PLTconn, DAQconn = Pipe()
        DAQCTL, PLTCTL = Pipe()
        whichchn = []
        gains = []
        toplotx = []
        toploty = []
        nactive = 0
        for k in self.traces:
            if k.isactive:
                nactive += 1
        if self.separate_plots:
            self.livefig.set_subplots(rows = nactive, cols = 1,
                                      shared_xaxes= True)
            self.livefig.update_xaxes(title = self.timelbl.value,
                                      row = nactive, col = 1)
        else:
            self.livefig.update_yaxes(title = "Values")
            self.livefig.update_xaxes(title = self.timelbl.value)
        active_count = 0
        for i in range(self.ntraces):
            if (self.traces[i].isactive):
                active_count += 1
                whichchn.append({'board':self.traces[i].board,
                                'chnl':self.traces[i].channel})
                gains.append(self.traces[i].toselectedgain)
                tempstr = self.traces[i].tracelbl.value + '(' + \
                          self.traces[i].units.value + ')'
                timelegend.append('time_' + tempstr)
                datalegend.append(tempstr)
                stdevlegend.append('stdev_' + tempstr)
                if self.separate_plots:
                    scat = go.Scatter(y=[],x=[], name=tempstr)
                    self.livefig.add_trace(scat, row = active_count,
                                           col = 1)
                    self.livefig.update_yaxes(title = self.traces[
                        i].units.value, row = active_count, col = 1)
                else:
                    self.livefig.add_scatter(y=[],x=[], name=tempstr)
                toplotx.append([])
                toploty.append([])
                
        #print('whichchn: '+str(whichchn))
        #print('gains: '+str(gains))
        # Use up to 30% of the time for averaging if channels were spaced
        # evenly between data collection times (with DACQ2 they appear
        # more synchronous than that).
        self.averaging_time = self.delta/nactive/3
        DAQ = Process(target=DAQProc,
                      args=(
                      whichchn, gains, self.averaging_time, self.delta,
                      DAQconn, DAQCTL))
        DAQ.start()
        lastupdatetime = time.time()

        pts = 0
        oldpts = 0
        #print('about to enter while loop',end='')
        while (self.collectbtn.description == 'Stop Collecting'):
            #print('.',end='')
            while PLTconn.poll():
                pkg = PLTconn.recv()
                self.lastpkgstr = str(pkg)
                #print(self.lastpkgstr)
                # convert voltage to requested units.
                tmptime = 0
                if self.ignore_skew:
                    tmptime = sum(pkg[0]) / len(pkg[0])
                for i in range(len(pkg[0])):
                    avg = pkg[1][i]
                    std = pkg[2][i]
                    avg_std = pkg[3][i]
                    avg_vdd = pkg[4][i]
                    avg, std, avg_std = self.traces[
                        self.tracemap[i]].toselectedunits(avg, std, avg_std, avg_vdd)
                    avg, std, avg_std = sensors.to_reasonable_significant_figures_fast(
                        avg, std, avg_std)
                    pkg[1][i] = avg
                    pkg[2][i] = std
                    pkg[3][i] = avg_std
                    if self.ignore_skew:
                        toplotx[i].append(tmptime)
                    else:
                        toplotx[i].append(pkg[0][i])
                    toploty[i].append(avg)
                timestamp.append(pkg[0])
                data.append(pkg[1])
                stdev.append(pkg[3])
            currenttime = time.time()
            mindelay = 1.0
            if self.separate_traces_checkbox.value:
                mindelay = nactive*1.0
            else:
                mindelay = nactive*0.5
            if (currenttime - lastupdatetime)>(mindelay+len(toplotx[0])*len(
                    toplotx)/1000):
                lastupdatetime = currenttime
                for k in range(len(self.livefig.data)):
                    self.livefig.data[k].x=toplotx[k]
                    self.livefig.data[k].y=toploty[k]
            #time.sleep(1)
            PLTCTL.send('send')
            time.sleep(self.delta)
            # print ('btn.description='+str(btn.description))
        endtime = time.time()
        PLTCTL.send('stop')
        time.sleep(0.5)  # wait 0.5 second to collect remaining data
        PLTCTL.send('send')
        time.sleep(0.5)
        msg = ''
        while (msg != 'done'):
            while PLTconn.poll():
                pkg = PLTconn.recv()
                # print(str(pkg))
                # convert voltage to requested units.
                for i in range(len(pkg[0])):
                    avg = pkg[1][i]
                    std = pkg[2][i]
                    avg_std = pkg[3][i]
                    avg_vdd = pkg[4][i]
                    avg, std, avg_std = self.traces[
                        self.tracemap[i]].toselectedunits(avg, std, avg_std, avg_vdd)
                    avg, std, avg_std = sensors.to_reasonable_significant_figures_fast(
                        avg, std, avg_std)
                    pkg[1][i] = avg
                    pkg[2][i] = std
                    pkg[3][i] = avg_std
                    if self.ignore_skew:
                        tmptime = sum(pkg[0])/len(pkg[0])
                        toplotx[i].append(tmptime)
                    else:
                        toplotx[i].append(pkg[0][i])
                    toploty[i].append(avg)
                    #print(pkg[0][i])
                    #print(avg)
                timestamp.append(pkg[0])
                data.append(pkg[1])
                stdev.append(pkg[3])
            PLTCTL.send('send')
            time.sleep(0.2)
            if PLTCTL.poll():
                msg = PLTCTL.recv()
                # print (str(msg))
                if (msg != 'done'):
                    print('Received unexpected message: ' + str(msg))
        for k in range(len(self.livefig.data)):
            self.livefig.data[k].x = toplotx[k]
            self.livefig.data[k].y = toploty[k]
        DAQ.join()  # make sure garbage collection occurs when it stops.
        DAQconn.close()
        PLTconn.close()
        DAQCTL.close()
        PLTCTL.close()


def newRun(livefig):
    """
    Set up a new data collection run and add it to the list of runs.
    """
    nrun = len(runs) + 1
    runs.append(DAQinstance(nrun, livefig, title='Run-' + str(nrun)))
    runs[nrun - 1].setup()
    pass

def doRun(whichrun):
    display(HTML('<span id="LiveRun_'+str(whichrun.idno)+'"></span>'))
    display(HTML(whichrun.defaultparamtxt))
    if hasattr(whichrun, "collectbtn"):
        # only show if hasn't already collected data
        whichrun.collectbtn.on_click(whichrun.collectclick)
        display(whichrun.collectbtn)
    display(HTML(whichrun.defaultcollecttxt))
    JPSLUtils.select_containing_cell("RunSetUp")
    JPSLUtils.delete_selected_cell()
    pass

def displayRun(runidx,file):
    """
    Displays a run. It can fall back to loading from a file if the outputarea
    is accidentally cleared.
    :param runidx: index+1 for the run in the runs array. Thus, the run id #.
    :param file: name of the file the run is saved to
    :return: A string warning if things are not initialized properly.
    """
    from IPython import get_ipython
    from JPSLUtils import find_pandas_dataframe_names, find_figure_names
    idxnum = runidx - 1
    run_id_table = pd.read_html(file, attrs={'id': 'run_id'})[0]
    run_title = run_id_table['Title'][0]
    run_id = run_id_table['Id #'][0]
    svname = pd.read_html(file, attrs={'id': 'file_info'})[0]['Saved as'][0]
    global_dict = get_ipython().user_ns
    runs = None
    if 'runs' in global_dict and 'DAQinstance' in global_dict:
        runs = global_dict['runs']
    else:
        return ('Initialization of JupyterPiDAQ required')
    exists = None
    if len(runs)>=runidx:
        if isinstance(runs[idxnum].livefig,go.FigureWidget) and runs[
            idxnum].idno == run_id and runs[idxnum].svname ==svname:
            exists = True
        else:
            exists = False
    if exists:
        display(HTML(runs[idxnum].defaultparamtxt))
        display(HTML('<h3>Saved as: '+runs[idxnum].svname+'</h3>'))
        runs[idxnum].livefig.show()
        display(HTML(runs[idxnum].defaultcollecttxt))
        JPSLUtils.select_containing_cell("LiveRun_"+str(runidx))
        JPSLUtils.delete_selected_cell()
    else:
        # Fall back on loading the data from the default save file.
        # Note: the file must be available.
        nrunfigs = 0
        for k in find_figure_names():
            if k.startswith('run_fig'):
                nrunfigs+=1
        runfigname = 'run_fig'+str(nrunfigs+1)
        global_dict[runfigname] = go.FigureWidget()
        fig = global_dict[runfigname]
        runs.append(DAQinstance(run_id, fig, title=run_title))
        idxnum = len(runs)-1
        runs[idxnum]._load_from_html(file)
        display(HTML(runs[idxnum].defaultparamtxt))
        display(HTML('<h3>Saved as: ' + runs[idxnum].svname + '</h3>'))
        runs[idxnum].livefig.show()
        display(HTML(runs[idxnum].defaultcollecttxt))
    # protect the cell
    JPSLUtils.OTJS('protect_selected_cells();')
    pass

def update_runsdrp():
    # get list of runs
    runlst = [('Choose Run', -1)]
    for i in range(len(runs)):
        runlst.append((str(i + 1) + ': ' + runs[i].title, i))
    # buid selection menu
    global runsdrp
    runsdrp = widgets.Dropdown(
        options=runlst,
        value=-1,
        description='Select Run #:',
        disabled=False,
    )
    pass

def showSelectedRunTable(change):
    global runsdrp
    whichrun = runsdrp.value
    runsdrp.close()
    tbldiv = '<div style="height:10em;">' + str(runs[whichrun].title)
    tbldiv += str(runs[whichrun].pandadf.to_html()) + '</div>'
    display(HTML(tbldiv))

def showDataTable():
    """
    Provides a menu to select which run. Then displays the run in a
    10 em high scrolling table. Selection menu is removed after choice
    is made.
    """
    update_runsdrp()
    global runsdrp
    runsdrp.observe(showSelectedRunTable, names='value')
    display(runsdrp)
    # will display selected run and delete menu upon selection.

def newCalculatedColumn():
    """
    Uses jupyter-pandas-GUI.new_pandas_column_GUI to provide a GUI expression
    composer. This method finds the datasets and launches the GUI.
    """
    df_info = []
    for i in range(len(runs)):
        df_info.append([runs[i].pandadf, 'runs['+str(i)+'].pandadf',
                        str(runs[i].title)])
    new_pandas_column_GUI(df_info)
    pass

def newPlot():
    """
    Uses jupyter-pandas-GUI.plot_pandas_GUI to provide a GUI expression
    composer. This method finds the datasets and launches the GUI.
    """
    df_info = []
    for i in range(len(runs)):
        if isinstance(runs[i].pandadf,pd.DataFrame):
            df_info.append([runs[i].pandadf, 'runs['+str(i)+'].pandadf',
                            str(runs[i].title)])
    plot_pandas_GUI(df_info)
    pass

def newFit():
    """
    Uses jupyter-pandas-GUI.fit_pandas_GUI to provide a GUI expression
    composer. This method finds the datasets and launches the GUI.
    """
    df_info = []
    for i in range(len(runs)):
        if isinstance(runs[i].pandadf,pd.DataFrame):
            df_info.append([runs[i].pandadf, 'runs['+str(i)+'].pandadf',
                            str(runs[i].title)])
    fit_pandas_GUI(df_info)
    pass