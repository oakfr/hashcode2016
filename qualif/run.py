import numpy as np
import os
import sys
import random
from scipy.optimize import linprog
import multiprocessing

def read_data (in_file):
    with open(in_file,'r') as fp:
        d = [int(x) for x in fp.readline().split(' ')]
        R = d[0]
        C = d[1]
        M = np.zeros((R,C))
        for (r,l) in zip(np.arange(R),fp.readlines()):
            M[r,:] = [int(x) for x in l.strip().replace('.','0').replace('#','1')]
    return (M,R,C)

def rle (ia):
    n=ia.size
    y = np.array(ia[1:] != ia[:-1])
    i = np.append(np.where(y),[n-1])
    z = np.diff(np.append([-1], i))
    p = np.cumsum(np.append([0],z))[:-1]
    return(z,p,ia[i])


if __name__ == "__main__":
        
    jobs = []

    num_threads = 32
    for p in range(num_threads):

        process = multiprocessing.Process(target=full_iteration, args=[])
        process.start()
        jobs.append(process)

    # wait for everyone
    for proc in jobs:
        proc.join()

