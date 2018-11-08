import random
import numpy as np
import os

mat=[0]*5
mat[0]=np.zeros((9,10))
mat[1]=np.zeros((10,10))
mat[2]=np.zeros((10,10))
mat[3]=np.zeros((10,10))
mat[4]=np.zeros((10,3))

np.save('mat.npy',mat)
np.save('mat2.npy',mat)
print(np.load('mat.npy'))

presc=100
np.save('presc.npy',presc)
np.save('presc2.npy',presc)
print(np.load('presc.npy'))
