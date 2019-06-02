import gzip
from urllib.request import urlopen, Request

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
        print('a')
        
    def get_data(self):
        baseurl='https://waterservices.usgs.gov/nwis/iv/?'
        theformat='format=waterml,2.0'
        parameter='parameterCd='+','.join(self.paramlist)
        urlsuffix=theformat+'&'+self.site+'&'+self.start+'&'+self.end+'&'+parameter+'&'+'siteStatus=all'
        self.requesturl=baseurl+urlsuffix
        self.datapath=os.path.join(self.sitedirectory,urlsuffix+'.xml')
        #print(requesturl)
        if os.path.exists(self.datapath):
            self.data=ET.parse(self.datapath) #add try clause?
            self.root=self.data.getroot() 
        else:    
            response=urlopen(Request(self.requesturl,headers={"Accept-Encoding": "gzip"})) 
            self.data=gzip.open(response, 'rb').read()
            self.root=ET.fromstring(self.data)
            #working on save problems:
            savefile=open(self.datapath,'w')
            savefile.write(ET.tostring(self.root).decode("utf-8"))
            savefile.close()
            #self.root.xml.write(self.datapath)

class Hydrositedatamodel(Hydrositedata):
    '''makes grandchild of hydrosite,child of hydrositedata'''
    def __init__(self, site, start, end, paramlist, modelfeatures):
        super().__init__(site,start,end,paramlist)
        self.modelfeatures=modelfeatures
        print('b')


    
