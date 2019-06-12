import gzip
from urllib.request import urlopen, Request
import sys
import os
import xml.etree.ElementTree as ET
import numpy as np
import datetime
import geopandas as gpd
import pandas as pd
import matplotlib as plt
from shapely.geometry import Point,Polygon
import descartes

from bokeh.io import show, output_notebook; 
from bokeh.plotting import figure; 
from bokeh.models import ColumnDataSource
output_notebook()

class Hydrosite():
    '''make parent class hydrosite, child will be hydrositedata, and grandchild is hydrositedatamodel. '''
    def __init__(self, site):
        self.site='sites='+site
        self.sitecode=site[-8:]
        self.sitedirectory='data/usgs-huc8-'+self.sitecode 
        if not os.path.exists(self.sitedirectory):
            os.makedirs(self.sitedirectory)

    
class Hydrositedata(Hydrosite): 
    '''make child of Hydrosite that has its own child Hydrositedatamodel.
    Create attributes self.start and self.end the start and times.
    Create attribute self.paramlist, the list of requested time series
    Run method self.get_data, then self.extractfromxml, then self.timematchcheck 
    methods not called at runtime
    simpleplot() create a simple plot of rainfall vs runoff
    geoplot() plots the point and the drainage basin
    '''
    def __init__(self, site, start, end, paramlist):
        super().__init__(site)
        self.start='startDT='+start
        self.end='endDT='+end
        self.paramlist=paramlist
        self.get_data()
        self.extractfromxml()
        self.timematchcheck()
        self.timestepcheck()
        self.tonumpy()
        
        
    def extractfromxml(self):
        """Take the time and values for each series from the xml to python lists with
        observations matched by time or else omitted from the new list. creates a new attribute
        called self.extracted with a column for each series and each row contains a (time,value) tuple.
        Create Attributes:
        self.extracted contains a list of series and each series is a list of
        (time, value) tuples 
        self.datatracker a list of the length of each list of series
        self.obs_idlist contains basic meta-data for each series downloaded
        self.latlon contains a list of strings with latitude and longitude for each series
        """
        """Note: xmllint --format file.xml in the linux terminal is used to view the structure of a 
        downloaded xml document
        """
        namespace={'ns0':"http://www.opengis.net/waterml/2.0",
           'ns1':"http://www.opengis.net/gml/3.2",
           'ns3':"http://www.w3.org/1999/xlink",
           'ns4':"http://www.opengis.net/om/2.0",
           'ns5':"http://www.opengis.net/sampling/2.0" ,
           'ns6':"http://www.opengis.net/samplingSpatial/2.0",
           'ns7':"http://www.opengis.net/swe/2.0"} 
        #add feature: automatically make the namespace dictionary automatic by pulling from begining of xml file
        extracted=[];j=-1;tracker=[];obs_idlist=[]; latlon=[];latlon_crs=[]; sitemetadata=[]
        for elem in self.root.findall('ns0:observationMember',namespace):
            obs_idlist.append(elem.find('ns4:OM_Observation',namespace).attrib)
            for elem2 in elem.findall('ns4:OM_Observation',namespace):
                tracker.append(0)#initialize the next series
                extracted.append([])
                j+=1#j is indexing each series
                elem3=elem2.find('ns4:featureOfInterest',namespace)
                sitemetadata.append(elem3.attrib['{http://www.w3.org/1999/xlink}title'])
                elem_latlon=elem3.find('ns0:MonitoringPoint',namespace)\
                    .find('ns6:shape',namespace)\
                    .find('ns1:Point',namespace)\
                    .find('ns1:pos',namespace)
                latlon.append(elem_latlon.text)
                latlon_crs.append(elem_latlon.attrib['srsName'][-9:])
                for elem3 in elem2.findall('ns4:result',namespace):
                    for elem4 in elem3.findall('ns0:MeasurementTimeseries',namespace):
                        for elem5 in elem4.findall('ns0:point',namespace):
                            for elem6 in elem5.findall('ns0:MeasurementTVP',namespace):
                                time=elem6.find('ns0:time',namespace)
                                val=elem6.find('ns0:value',namespace)
                                extracted[j].append((time.text,val.text))
                                tracker[j]+=1
        self.sitemetadata=sitemetadata
        self.latlon=latlon
        self.latlon_crs=latlon_crs
        self.extracted=extracted
        self.datatracker=tracker #a list of counts of observations for each time,value pair
        self.obs_idlist=obs_idlist
        
    def geoplot(self):
        """creates a plot of the site location on a map with the drainage basin and eventually NLCD landcover
        """
        j=len(self.latlon)
        self.df=pd.DataFrame([[self.latlon[j][-11:],self.latlon[j][:11],self.latlon_crs[j],self.sitemetadata[j]] for j in range(j)],columns=["longitude","latitude","CRS","site_name"])
        
        
        
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
    
    def simpleplot(self):
        gageht=self.data_array[:,2]-np.amin(self.data_array[:,2])
        time=self.data_array[:,0]
        precip=self.data_array[:,1]
        p=figure(title='rainfall and gageheight over time', plot_width=900, plot_height=500)
        p.xaxis.axis_label = 'time(days)'
        p.scatter(time,precip,size=precip/np.amax(precip)*7+2,color='red',alpha=0.6,legend='precipitation')
        p.line(time,precip,color='red',alpha=0.6,legend='precipitation')
        p.scatter(time,gageht,size=2,color='blue',legend='gage height')
        p.line(time,gageht,color='blue',legend='gage height')
        p.legend.location = "top_left"
        p.yaxis.visible=False
        show(p)
    
    def timestepcheck(self):
        """if the number of time periods is T then create attribute self.timestep, a list of T-1 time steps
        Then create attribute self.allstepeven and set it to 1 if all items in self.timestep are equal.
        add threshold?
        todo: handle allmatch==0
        """
        self.allstepseven=0
        self.t_format='%Y-%m-%dT%H:%M:%S%z'
        stepcount=len(self.matchlog)-1 #minus 1 because it is a difference
        timestep=[[0] for _ in range(stepcount)]
        if self.allmatch==1:
            for i in range(stepcount):
                timestep[i]=datetime.datetime.strptime(self.extracted[0][i+1][0],self.t_format)
            for i in range(stepcount):
                timestep[i]-=datetime.datetime.strptime(self.extracted[0][i][0],self.t_format)
            self.timestep=timestep
            self.allstepseven=all([j==timestep[0] for j in timestep])
        else:sys.exit("error from allmatch==0")
        if self.allstepseven==1: print('all time steps are evenly spaced')
        else: print('not all time steps are evenly spaced')
    
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
                    print('not all series have matching times from start to end.')
                    print('view attribute *.matchlog to see discrepancies from first series')
        self.matchlog=matchlog
        if self.allmatch==1: print('all series have matching times from start to end')
        
            
             
    def tonumpy(self):
        """create self.data_array a numpy array with an observation on each row containing a time
        column measuring days since the first obseration followed by each series
        """
        if self.allmatch==1:
            n=len(self.matchlog)
            k=len(self.matchlog[0])+2 #+1 for time column, +1 more since matchlog is nx1 for 2 series
            print('The request has returned {} observations for {} series'.format(n,k-1))
            self.data_array=np.ones([n,k])
            startdate=datetime.datetime.strptime(self.extracted[0][0][0],self.t_format)
            startyear=startdate.year
            for i in range(n):
                timediffs=datetime.datetime.strptime(self.extracted[0][i][0],self.t_format)-startdate
                self.data_array[i,0]=timediffs.days+timediffs.seconds/60/60/24 #convert to days
                for j in range(k-1): #k-1 because time is set
                    try: self.data_array[i,j+1]=float(self.extracted[j][i][1])
                    except:self.data_array[i,j+1]=np.nan
        else: import sys;sys.exit("error from allmatch==0")        

        
    

    

class Hydrositedatamodel(Hydrositedata):
    '''makes grandchild of hydrosite,child of hydrositedata'''
    def __init__(self, site, start, end, paramlist, modelfeatures):
        super().__init__(site,start,end,paramlist)
        self.modelfeatures=modelfeatures
        


    
