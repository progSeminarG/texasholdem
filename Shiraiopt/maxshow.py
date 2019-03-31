import numpy as np

name=[0]*5
mat=[0]*5
for i in range(5):
    name[i]="maxmat"+str(i)+".npy"
    mat[i]=np.load(name[i])
    print(mat[i])
