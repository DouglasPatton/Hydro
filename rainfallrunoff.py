
import numpy as np
from scipy.optimize import minimize

class RRtimeseries():
    '''take in column of dates, rainfall, and runoff and builds distributed lag model'''
    def __init__(self,data,modelfeatures):
        self.data=data
        self.n=np.shape(data)[0]
        self.modelfeatures=modelfeatures
        if modelfeatures['RRmodeltype']=='distributed_lag':
            if modelfeatures['local']=='no':
                self.maxlag=modelfeatures['maxlag']
                self.startlag=modelfeatures['startlag']
                self.distlagmodel()
        else: print('other')
        
    def distlagmodel(self):
        self.lagprecip=self.lagmaker(self.data[:,1],self.maxlag,self.startlag)
        if self.modelfeatures['AR1']=='yes':
            self.lagn=np.shape(self.lagprecip)[0]
            runlag1=self.data[(self.maxlag-1):(self.n-1),0][:,None]
            print('***',runlag1.shape,self.lagprecip.shape)
            X=np.concatenate((runlag1,self.lagprecip),axis=1)
            print(np.shape(X))
            #return minimize(lagmodelMSE,wt_try0,args=(runY,rainX),method='Nelder-Mead')
        
    def lagmodelMSE(Betas,Y,X):
        pass
    
    
        
    def lagmaker(self,tseries,maxlag,startlag):  
        lagtseries=np.empty([self.n+maxlag-startlag,maxlag-startlag+1]) #+1 b/c 0...maxlag
        for i in range(maxlag-startlag+1):
            lagtseries[(i+startlag):self.n+i+startlag,i]=tseries
        return lagtseries[maxlag:self.n,:]
        
        
        
