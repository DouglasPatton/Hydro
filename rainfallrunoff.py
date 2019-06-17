
import numpy as np
import tstools as tst
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
                print('betas:',np.exp(self.modeloutput.x))
                print('MSE:',self.modeloutput.fun)
        else: print('other')
        
    def distlagmodel(self):
        self.lagprecip=tst.lagmaker(self.data[:,1],self.maxlag,self.startlag)
        self.lagn=np.shape(self.lagprecip)[0]
        
        if self.modelfeatures['incl_AR1']=='yes':
            runlag1=self.data[(self.maxlag-1):(self.n-1),0][:,None]
            x=np.concatenate((runlag1,self.lagprecip),axis=1)
        else:x=self.lagprecip
        if self.modelfeatures['incl_constant']=='yes':
            x=np.concatenate((np.ones([self.lagn,1]),x),axis=1)
        
        betastart=np.ones(np.shape(x)[1])
        self.modeloutput=minimize(self.lagmodelMSE,betastart,args=(self.data[self.maxlag:,2],x),method='BFGS')
        self.modelpredict=x@np.exp(self.modeloutput.x)
        
        
    def lagmodelMSE(self,betas,y,x):
        return np.sum((y-x@np.exp(betas))**2)/np.shape(y)[0]
    
    
    
    
    
        
    
        
        
        
