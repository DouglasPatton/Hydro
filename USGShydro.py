import gzip
from urllib.request import urlopen, Request
import sys
import os
import xml.etree.ElementTree as ET
import numpy as np
import datetime

class Hydrosite():
    '''make parent class hydrosite, child will be hydrositedata, and grandchild is hydrositedatamodel. '''
    def __init__(self, site):
        self.site=site
        self.sitecode=site[-8:]
        self.sitedirectory='data/usgs-huc8-'+self.sitecode 
        if not os.path.exists(self.sitedirectory):
            os.makedirs(self.sitedirectory)

    
class Hydrositedata(Hydrosite): 
    '''make child of Hydrosite that has its own child Hydrositedatamodel.
    Create attributes self.start and self.end the start and times.
    Create attribute self.paramlist, the list of requested time series
    Run method self.get_data, then self.extractfromxml, then self.timematchcheck    
    '''
    def __init__(self, site, start, end, paramlist):
        super().__init__(site)
        self.start=start
        self.end=end
        self.paramlist=paramlist
        self.get_data()
        self.extractfromxml()
        self.timematchcheck()
        self.timestepcheck()
       # self.tonumpy()
        
    def get_data(self):
        """create self.requesturl, a url based on site# and parameters.
        create self.datapath to check if data from self.requesturl has already been downloaded
        Use locally stored xml data if available or download the data if not.
        create self.data containing the unzipped gzip string data.
        create self.root that contains the root of the element tree .
        """
        baseurl='https://waterservices.usgs.gov/nwis/iv/?'
        theformat='format=waterml,2.0'
        parameter='parameterCd='+','.join(self.paramlist)
        urlsuffix=theformat+'&'+self.site+'&'+self.start+'&'+self.end+'&'+parameter+'&'+'siteStatus=all'
        self.requesturl=baseurl+urlsuffix
        self.datapath=os.path.join(self.sitedirectory,urlsuffix+'.xml')#put these details in a companion file and simplify file name
        if os.path.exists(self.datapath):
            self.data=ET.parse(self.datapath) #add try clause?
            self.root=self.data.getroot() 
        else:    
            response=urlopen(Request(self.requesturl,headers={"Accept-Encoding": "gzip"})) 
            self.data=gzip.open(response, 'rb').read()
            self.root=ET.fromstring(self.data)
            savefile=open(self.datapath,'w')
            savefile.write(ET.tostring(self.root).decode("utf-8"))
            savefile.close()
         
    def tonumpy(self):
        if self.allmatch==1:
            n=len(self.matchlog)
            k=len(self.matchlog[0]+1)
            self.data_array=np.empty([n,k])
            print(self.data_array.shape)
            for i in len(self.matchlog):
                self.data_array[i,:]=1
        else: import sys;sys.exit("error from allmatch==0")        
    
    def timestepcheck(self):
        """if the number of time periods is T then create attribute self.timestep, a list of T-1 time steps
        Then create attribute self.allstepeven and set it to 1 if all items in self.timestep are equal.
        add threshold?
        todo: handle allmatch==0
        """
        self.allstepseven=0
        t_format='%Y-%m-%dT%H:%M:%S%z'
        stepcount=len(self.matchlog)-1 #minus 1 because it is a difference
        timestep=[[0] for _ in range(stepcount)]
        if self.allmatch==1:
            for i in range(stepcount):
                timestep[i]=datetime.datetime.strptime(self.extracted[0][i+1][0],t_format)
            for i in range(stepcount):
                timestep[i]-=datetime.datetime.strptime(self.extracted[0][i][0],t_format)
            self.timestep=timestep
            self.allstepseven=all([j==timestep[0] for j in timestep])
        else: import sys;sys.exit("error from allmatch==0")
    
    def timematchcheck(self):
        """create an attribute self.matchlog that contains a column
        for comparing times for series 1 with series 2, then series 1 and series 3, and so on
        the rows of self.matchlog  are 1 if all series in that row have the same time and 0 
        if any are not a match.
        create attribute self.allmatch which is 1 if all values have a matching time and 0 if not.
        add feature: handle data that is not synchronized across each row
        """
        matchlog=[]
        self.allmatch=1
        for i in range(self.datatracker[0]):
            matchlog.append([])
            for j in range(len(self.datatracker)-1): #j-1 because we have 1 less comparison than series
                matchlog[i].append(1) #start all matches as true
                if self.extracted[0][i][0]==self.extracted[j+1][i][0]: #j+1 to avoid comparing first series to itself
                    matchlog[i][j]=matchlog[i][j]*1 #this will maintian the zero or 1 value
                else: 
                    matchlog[i][j]=0 #this will force the match value to zero if any times don't match.
                    self.allmatch=0
        self.matchlog=matchlog
        
            
    
        
    

    def extractfromxml(self):
        """this will take the time and values for each series from the xml to python lists with
        observations matched by time or else omitted from the new list. creates a new attribute
        called self.extracted with a column for each series and each row contains a (time,value) tuple.
        """
        """xmllint --format file1.xml in the linux terminal is used to view the structure of the xml document
        """
        namespace={'ns0':"http://www.opengis.net/waterml/2.0",
           'ns1':"http://www.opengis.net/gml/3.2",
           'ns3':"http://www.w3.org/1999/xlink",
           'ns4':"http://www.opengis.net/om/2.0"} 
        #add feature: automatically make the namespace dictionary automatic by pulling from begining of xml file
        extracted=[];j=-1;tracker=[]
        for elem in self.root.findall('ns0:observationMember',namespace):
            for elem2 in elem.findall('ns4:OM_Observation',namespace):
                tracker.append(0)
                extracted.append([])
                j+=1
                for elem3 in elem2.findall('ns4:result',namespace):
                    for elem4 in elem3.findall('ns0:MeasurementTimeseries',namespace):
                        for elem5 in elem4.findall('ns0:point',namespace):
                            for elem6 in elem5.findall('ns0:MeasurementTVP',namespace):
                                time=elem6.find('ns0:time',namespace)
                                val=elem6.find('ns0:value',namespace)
                                extracted[j].append((time.text,val.text))
                                tracker[j]+=1
        self.extracted=extracted
        self.datatracker=tracker #a list of counts of observations for each time,value pair
    

class Hydrositedatamodel(Hydrositedata):
    '''makes grandchild of hydrosite,child of hydrositedata'''
    def __init__(self, site, start, end, paramlist, modelfeatures):
        super().__init__(site,start,end,paramlist)
        self.modelfeatures=modelfeatures
        


    
