import random
import numpy as np
import os

mat=[0]*5
mat[0]=np.zeros((9,10))
mat[1]=np.zeros((10,10))
mat[2]=np.zeros((10,10))
mat[3]=np.zeros((10,10))
mat[4]=np.zeros((10,3))

plusmat=[0]*5
plusmat[0]=np.zeros((9,10))
plusmat[1]=np.zeros((10,10))
plusmat[2]=np.zeros((10,10))
plusmat[3]=np.zeros((10,10))
plusmat[4]=np.zeros((10,3))

np.save('mat.npy',mat)
print(np.load('mat.npy'))

np.save('plusmat.npy',plusmat)
print(np.load('plusmat.npy'))


presc=100
np.save('presc.npy',presc)
print(np.load('presc.npy'))
