import gzip
from urllib.request import urlopen, Request
from urllib import request
import os


class Hydrosite():
    '''makes parent class hydrosite, child will be hydrositedata, and grandchild is hydrositedatamodel. '''
    def __init__(self, site):
        self.site=site
        self.sitecode=site[-8:]
        directory='usgs-huc8-'+self.sitecode
        if not os.path.exists(directory):
            os.makedirs(directory)

    
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
        requesturl = baseurl+theformat+'&'+self.site+'&'+self.start+'&'+self.end+'&'+parameter+'&'+'siteStatus=all'
        print(requesturl)
        #response=urlopen(Request(requesturl,headers={"Accept-Encoding": "gzip"})) 
        #return gzip.open(response, 'rb').read()


class Hydrositedatamodel(Hydrositedata):
    '''makes grandchild of hydrosite,child of hydrositedata'''
    def __init__(self, site, start, end, paramlist, modelfeatures):
        super().__init__(site,start,end,paramlist)
        self.modelfeatures=modelfeatures
        print('b')


    
