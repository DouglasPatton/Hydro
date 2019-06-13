
import numpy as np
class RRtimeseries():
    '''take in column of dates, rainfall, and runoff and builds distributed lag model'''
    def __init__(self,data,modelfeatures):
        self.data=data
        self.modelfeatures=modelfeatures
        
        
    #def lagmaker(self):    
        
