
import numpy as np
class RRtimeseries():
    '''take in column of dates, rainfall, and runoff and builds distributed lag model'''
    def __init__(self,data,modelfeatures):
        self.data=data
        self.n=np.shape(data)[0]
        self.modelfeatures=modelfeatures
        if modelfeatures['RRmodeltype']=='distributed_lag':
            if modelfeatures['local']=='no':
                self.maxlag=modelfeatures['maxlag']
                self.distlagmodel()
        else: print('other')
        
    def distlagmodel(self):
        self.lagprecip=self.lagmaker(self.data[:,1],self.maxlag)
        
        
        
    def lagmaker(self,precip_series,maxlag,startlag=0):  
        lagprecip=np.ones(self.n+maxlag-startlag,maxlag-startlag+1) #+1 b/c 0...maxlag
        for i in range(maxlag-startlag+1):
            lagprecip[(i+startlag):self.n,i]=precip_series
        self.lagprecip=lagprecip[maxlag:(self.n+maxlag),:]
        
