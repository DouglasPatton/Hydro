import gzip
from urllib.request import urlopen, Request
import sys
import os
import xml.etree.ElementTree as ET

class Hydrosite():
    '''makes parent class hydrosite, child will be hydrositedata, and grandchild is hydrositedatamodel. '''
    def __init__(self, site):
        self.site=site
        self.sitecode=site[-8:]
        self.sitedirectory='data/usgs-huc8-'+self.sitecode 
        if not os.path.exists(self.sitedirectory):
            os.makedirs(self.sitedirectory)

    
class Hydrositedata(Hydrosite): 
    '''makes child of Hydrosite that has its own child Hydrositedatamodel'''
    def __init__(self, site, start, end, paramlist):
        super().__init__(site)
        self.start=start
        self.end=end
        self.paramlist=paramlist
        print('about to get data')
        self.get_data()
        self.extractfromxml()
        self.timematchcheck()
        
    def get_data(self):
        print('getting data')
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
           
    def timematchcheck(self):
        """creates an attribute self.matchlog that contains a column
        for comparing times for series 1 with series 2, then series 1 and series 3, and so on
        the rows of self.matchlog  are 1 if all series in that row have the same time and 0 
        if any are not a match
        """
        matchlog=[]
        for i in range(self.datatracker[0]):
            matchlog.append([])
            for j in range(len(self.datatracker)-1): #-j1 because we have 1 less comparison than series
                matchlog[i].append(1)
                if self.extracted[0][i][0]==self.extracted[j+1][i][0]: #+1
                    matchlog[i][j]=matchlog[i][j]*1
                else: 
                    matchlog[i][j]=0
        self.matchlog=matchlog
        
            
    #def mergetonumpyarray(self):
        
    

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
                print(elem2.tag)
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
        


    
