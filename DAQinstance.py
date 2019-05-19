#Tools for using a Jupyter notebook as a lab notebook that collects and
# displays data from an analog to digital converter in real time. The interface
# also allows for annotation, analysis and display of the data using common
# python tools. Common activities can be done using menus and buttons rather
# than typing python commands.
# J. Gutow <jgutow@new.rr.com> March 17, 2019
# license GPL V3 or greater.

######
#Environment setup
######
#Use os tools for file path and such
import os
# below is equivalent to %matplotlib notebook in a Jupyter cell
from IPython import get_ipython
ipython = get_ipython()
if ipython:
    ipython.magic("matplotlib notebook")
#these % magics are important inside the notebook

#imports below must work. Allow normal python error response.
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML
from IPython.display import Javascript as JS
import time
#Below allows asynchronous calls to get and plot the data in real time.
#Actually read the DAQ board on a different process.
import threading 
from multiprocessing import Process, Pipe

#this import is being done to see if an actual analog-to-digital converter is
# available. Used to decide if running in "Demo" mode or not.
MODE = 'Demo'
try:
    import Adafruit_ADS1x15
except (ImportError, RuntimeError) as e:
    MODE='Demo'
    display(JS('alert("Running in Demo mode. No ADC detected.")'))
else:
    MODE='ADS1115'
from DAQProc import DAQProc

#globals to put stuff in from threads.
data=[] #all data from DAQ tools avg_values
stdev=[] #all standard deviations
timestamp=[] #all timestamps

#global list to keep track of runs
runs = []

######
#Interactive elements definitions
######

#Locate JupyterPiDAQ package directory
mydir=os.path.dirname(__file__) #absolute path to directory containing this file.

#Add a "DAQ Menu" to the notebook.
tempJSfile = open(os.path.join(mydir,'javascript','JupyterPiDAQmnu.js'))
tempscript='<script type="text/javascript">'
tempscript+=tempJSfile.read()+'</script>'
tempJSfile.close()
display(HTML(tempscript))
display(JS('createCmdMenu()'))

#Data Aquistion Instance (a run).
class DAQinstance():
    def __init__(self, idno, title='None', nchannels=4):
        self.idno=idno
        self.title=str(title)
        self.averaging_time = 0.02 #seconds
        self.gain=[1,1,1,1]
        self.data=[]
        self.timestamp=[]
        self.stdev=[]
        self.pandadf=None
        self.nchannels=nchannels
        self.whichchannels = []
        self.channellbls=[]
        for i in range(self.nchannels):
            self.whichchannels.append(widgets.Checkbox(
                    value=False,
                    description='Channel '+str(i),
                    disabled=False
                ))
            if (i==0):
                self.channellbls.append(widgets.Text(
                    value='Channel '+str(i),
                    placeholder='Type something',
                    description='Title (units):',
                    disabled=False))
            else:
                self.channellbls.append(widgets.Text(
                    value='Channel '+str(i),
                    placeholder='Type something',
                    description='              ',
                    disabled=False))                
        self.ratemax = 3.0 #Hz
        self.rate = 1.0 #Hz
        self.deltamin = 1/self.ratemax
        self.delta = 1.0/self.rate
        self.setupbtn = widgets.Button(
            description='Set Parameters',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click to set collection parameters to displayed values.',
            icon='')
        self.collectbtn = widgets.Button(
            description='Start Collecting',
            disabled=False,
            button_style='success', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Start collecting data and plotting it. Will make new graph.',
            icon='')
        self.rateinp = widgets.BoundedFloatText(
            value=self.rate,
            min=0,
            max=self.ratemax,
            step=self.ratemax/1000.0,
            description='Rate (Hz):',
            disabled=False)
        self.timelbl=widgets.Text(
            value='Time (s)',
            placeholder='Type something',
            description='X-axis label (time):',
            disabled=False)
        self.runtitle=widgets.Text(
            value=self.title,
            placeholder='Type title/description',
            description='Run title',
            disabled=False)
        self.defaultparamtxt=''
        self.defaultcollecttxt='<span style="color:red;">If you see single dots displayed as two colors or distorted, '
        self.defaultcollecttxt+='expand graph slightly to force browser to redraw the graph.</span>'
        self.defaultcollecttxt+='<span style="color:blue;"> To accurately read point location zoom in a lot'
        self.defaultcollecttxt+=' (box button below graph).</span>'
        self.collecttxt=widgets.HTML(
            value=self.defaultcollecttxt,
            placeholder='',
            description='')
        tempgridcol=''
        tempgridperc=np.round(80/self.nchannels)
        for i in range(self.nchannels):
            tempgridcol+=str(tempgridperc)+'% '
        self.chnlgrid=widgets.GridBox(
            children=self.whichchannels+self.channellbls,
            layout=widgets.Layout(
                width='80%',
                grid_template_columns=tempgridcol,
                grid_template_rows='auto auto',
            ))
        #self.chnl_layout=widgets.HBox(self.whichchannels)
        #self.chnllbl_layout=widgets.HBox(self.channellbls)
        self.setup_layout=widgets.HBox([self.rateinp,self.timelbl,self.setupbtn])
        self.collect_layout=widgets.HBox([self.collectbtn,self.collecttxt])
    
    def setupclick(self,btn):
        #Could just use the values in widgets, but this forces intentional selection and locks them for the run.
        self.title=self.runtitle.value
        self.rate = self.rateinp.value
        self.delta=1/self.rate
        self.defaultparamtxt= '<div id="DAQRun_'+str(self.idno)+'_param">'
        self.defaultparamtxt+='<p style="font-weight:bold;">Parameters for run '+str(self.title)
        self.defaultparamtxt+=' (id#: '+str(self.idno)+') set to:</p>'
        self.defaultparamtxt+='<table><tr><td style="font-weight:bold;">Approx. Rate (Hz):</td><td>'+str(self.rate)+'</td>'
        self.defaultparamtxt+='<td style="font-weight:bold;">Approx. Delta (s):</td><td>'+str(self.delta)+'</td>'
        self.defaultparamtxt+='<td style="font-weight:bold;">X-label: </td><td>'+self.timelbl.value+'</td></tr></table>'
        # table of channel information
        self.defaultparamtxt+='<table id="chnlinfo" class="chnlinfo"><tr>'
        self.defaultparamtxt+='<td style="font-weight:bold;">Channel #</td>'
        for i in range(self.nchannels):
            if (self.whichchannels[i].value):
                self.defaultparamtxt+='<td>'+str(i)+'</td>'
        self.defaultparamtxt+='</tr><tr><td style="font-weight:bold;">Title</td>'
        for i in range(self.nchannels):
            if (self.whichchannels[i].value):
                self.defaultparamtxt+='<td>'+str(self.channellbls[i].value)+'</td>'        
        self.defaultparamtxt+='</tr></table>'
        self.defaultparamtxt+='</div>'
        self.runtitle.close()
        self.chnlgrid.close()
        self.setup_layout.close()
        display(HTML(self.defaultparamtxt))
        self.collectbtn.on_click(self.collectclick)
        display(self.collectbtn)

    def setup(self):
        self.setupbtn.on_click(self.setupclick)
        display(self.runtitle)
        #display(self.chnl_layout)
        #display(self.chnllbl_layout)
        display(self.chnlgrid)
        display(self.setup_layout)
        
    def collectclick(self,btn):
        if (btn.description=='Start Collecting'):
            btn.description='Stop Collecting'
            btn.button_style='danger'
            btn.tooltip='Stop the data collection'
            self.setupbtn.disabled=True #do not allow parameters to be reset after starting run.
            self.setupbtn.tooltip='Parameters locked. The run has started.'
            self.rateinp.disabled=True
            self.timelbl.disabled=True
            #self.ylbl.disabled=True
            for i in range(self.nchannels):
                self.whichchannels[i].disabled=True
                self.channellbls[i].disabled=True
            thread=threading.Thread(target=self.updatingplot,args=())
            thread.start()
        else:
            btn.description='Done'
            btn.button_style=''
            btn.tooltip=''
            time.sleep(3)# wait a few seconds for end of data collection
            self.data = data
            self.timestamp=timestamp
            self.stdev=stdev
            self.fillpandadf()
            #save data to csv file so can be loaded elsewhere.
            svname=self.title+'_'+time.strftime('%y-%m-%d_%H%M%S',time.localtime())+'.csv'
            self.pandadf.to_csv(svname)
            self.collectbtn.close()
            display(self.collecttxt)
            display(HTML('<span style="color:blue;font-weight:bold;">DATA SAVED TO:'+svname+'</span>'))
            
    def fillpandadf(self):
        datacolumns=[]
        temptimes=np.transpose(self.timestamp)
        tempdata=np.transpose(self.data)
        tempstdev=np.transpose(self.stdev)
        chncnt = 0
        for i in range(self.nchannels):
            if (self.whichchannels[i].value):
                chncnt+=1
        for i in range(chncnt):
            datacolumns.append(temptimes[i])
            datacolumns.append(tempdata[i])
            datacolumns.append(tempstdev[i])
        titles = []
        for i in range(len(self.channellbls)):
            if(self.whichchannels[i].value):
                titles.append(self.timelbl.value+'_'+self.channellbls[i].value)
                titles.append(self.channellbls[i].value)
                titles.append('stdev_'+self.channellbls[i].value)
        #print(str(titles))
        #print(str(datacolumns))
        self.pandadf=pd.DataFrame(np.transpose(datacolumns),columns=titles)
                       
    def updatingplot(self):
        '''
        Runs until when a check of self.collectbtn.description does not return 'Stop Collecting'.
            This would probably be more efficient if set a boolean.
        '''
        starttime=time.time()
        global data
        data =[]
        global timestamp
        timestamp=[]
        global stdev
        stdev=[]
        datalegend=[]
        timelegend=[]
        stdevlegend=[]
        PLTconn,DAQconn=Pipe()
        DAQCTL,PLTCTL=Pipe()
        whichchn=[]
        for i in range(self.nchannels):
            whichchn.append(self.whichchannels[i].value)
        #print(str(whichchn))
        DAQ=Process(target=DAQProc,args=(whichchn,self.gain,self.averaging_time,self.delta,DAQconn,DAQCTL,MODE))
        DAQ.start()
        for i in range(self.nchannels):
            if (self.whichchannels[i].value):
                tempstr=self.channellbls[i].value
                timelegend.append('time_'+tempstr)
                datalegend.append(tempstr)
                stdevlegend.append('stdev_'+tempstr)
        fig = plt.figure()
        ax = fig.add_subplot(111)
            
        pts=0
        oldpts=0
        while (self.collectbtn.description=='Stop Collecting'):            
            while PLTconn.poll():
                pkg = PLTconn.recv()
                #print(str(pkg))
                timestamp.append(pkg[0])
                data.append(pkg[1])
                stdev.append(pkg[2])
            PLTCTL.send('send')
            time.sleep(self.delta)
            pts = len(timestamp)
            if (pts>oldpts):
                oldpts = pts
                ax.clear()
                ax.set_xlabel(self.timelbl.value)
                ax.set_ylabel('Y')
                ax.plot(timestamp,data,'.-')
                ax.legend(datalegend)
                fig.canvas.draw()
                plt.pause(1)
            #print ('btn.description='+str(btn.description))
        endtime=time.time()
        PLTCTL.send('stop')
        time.sleep(0.5) #wait 0.5 second to collect remaining data
        PLTCTL.send('send')
        time.sleep(0.5)
        msg=''
        while (msg!='done'):
            while PLTconn.poll():
                pkg = PLTconn.recv()
                #print(str(pkg))
                timestamp.append(pkg[0])
                data.append(pkg[1])
                stdev.append(pkg[2])
            PLTCTL.send('send')
            time.sleep(0.2)
            if PLTCTL.poll():
                msg=PLTCTL.recv()
                #print (str(msg))
                if(msg!='done'):
                    print('Received unexpected message: '+str(msg))
        ax.clear()
        #self.data = data
        #self.timestamp=timestamp
        ax.set_xlabel(self.timelbl.value)
        ax.set_ylabel('Y')
        ax.plot(timestamp,data,'.-')
        ax.legend(datalegend)
        #fig.show()
        fig.canvas.draw()
        DAQ.join() #make sure garbage collection occurs when it stops.
        DAQconn.close()
        PLTconn.close()
        DAQCTL.close()
        PLTCTL.close()
        
def newRun():
    '''Set up a new data collection run and add it to the list of runs.'''
    data=[]
    timestamp=[]
    stdev=[]
    nrun=len(runs)+1
    runs.append(DAQinstance(nrun,title='Run-'+str(nrun)))
    runs[nrun-1].setup()
    
def showSelectedRunTable(change):
    global runsdrp
    whichrun=int(runsdrp.value)-1
    runsdrp.close()
    tbldiv='<div style="height:10em;">'+str(runs[whichrun].title)
    tbldiv+=str(runs[whichrun].pandadf.to_html())+'</div>'
    display(HTML(tbldiv))
    
def showDataTable():
    '''Provides a menu to select which run. Then displays the run in a 
       10 em high scrolling table. Selection menu is removed after choice
       is made.
    '''
    #get list of runs
    runlst=['Choose Run']
    for i in range(len(runs)):
        runlst.append(str(i+1))
    #buid selection menu
    global runsdrp
    runsdrp=widgets.Dropdown(
        options=runlst,
        value=runlst[0],
        description='Select Run #:',
        disabled=False,
        )
    runsdrp.observe(showSelectedRunTable,names='value')
    display(runsdrp)
    #will display selected run and delete menu upon selection.

def newCalculatedColumn():
    '''Simple GUI for generating an expression for a column calculated from other
       columns in a data set. The new column can be added to a single run or all
       runs.'''
    print("Sorry, not yet implemented.")