
import numpy as np
class RRtimeseries():
    '''take in column of dates, rainfall, and runoff and builds distributed lag model'''
    def __init__(self,data,modelfeatures):
        self.data=data
        self.modelfeatures=modelfeatures
        if modelfeatures['RRmodeltype']=='distributed_lag':
            if modelfeatures['local']=='no':
                maxlag=modelfeatures['maxlag']
                self.distlagmodel()
        else: print('other')
        
    def distlagmodel(self):
        n,k=data.shape()
        
        self.lagprecip=self.lagmaker(data[:,1],maxlags)
        
        
        
    def lagmaker(self,dataseries,maxlag):  
        lagprecip=np.ones(n+maxlag,maxlag+1) #+1 b/c 0...maxlag
        for i in range(maxlag+1):
            lagprecip[[i:n],i]=data[:,1]
        self.lagprecip=lagprecip[maxlag:(n+maxlag),:]
        
