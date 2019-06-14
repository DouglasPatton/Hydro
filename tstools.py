import numpy as np

def lagmaker(tseries,maxlag,startlag):  
    n=np.shape(tseries)[0]
    lagtseries=np.empty([n+maxlag-startlag,maxlag-startlag+1]) #+1 b/c 0...maxlag
    for i in range(maxlag-startlag+1):
        lagtseries[(i+startlag):(n+i+startlag),i]=tseries
    return lagtseries[maxlag:n,:]
