import random
import numpy as np
import os

name=[0]*5
pname=[0]*5
mat=[0]*5
plusmat=[0]*5
for i in range(5):
    name[i] = "mat" + str(i) + ".npy"
    pname[i] = "plusmat" + str(i) + ".npy"

mat[0]=np.zeros((10,10))
mat[1]=np.zeros((10,10))
mat[2]=np.zeros((10,10))
mat[3]=np.zeros((10,10))
mat[4]=np.zeros((10,3))

plusmat[0]=np.zeros((10,10))
plusmat[1]=np.zeros((10,10))
plusmat[2]=np.zeros((10,10))
plusmat[3]=np.zeros((10,10))
plusmat[4]=np.zeros((10,3))

for i in range(5):
    np.save(name[i],mat[i])
    np.save(pname[i],plusmat[i])

presc=100
np.save('presc.npy',presc)
