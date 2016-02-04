import os
import numpy as np
import itertools
import pickle

R = 180
C = 60
H = 3
A = 12

def get_hams (M,a):
    return np.sum(M[a[0][0]:a[0][1],a[1][0]:a[1][1]])

def get_area (M,c):
    return (c[0][1]-c[0][0]+1)*(c[1][1]-c[1][0]+1)

def comp_score (M,cuts):
    score = 0
    for c in cuts:
        v = get_area(M,c)
        h = get_hams(M,c)
        assert(v<=A)
        assert(v>=H)
        score += v
    return score

def get_cuts(M):
    cuts = []
    rl = np.arange(0,R,3)
    rr = rl+2
    rz = list(zip(rl,rr))
    cl = np.arange(0,C,4)
    cr = cl+3
    cz = list(zip(cl,cr))
    xz = itertools.product(rz,cz)
    for c in xz:
        if get_hams(M,c) >= H:
            cuts.append(c)
    return cuts

def list_fmts (M):
    fmts = []
    for c in range(1,12):
        for r in range(1,12):
            if c*r >= 3 and c*r <= A:
                fmts.append((r,c))
    fmts = list(set(fmts))
    return fmts

def is_in (a,b):
    return (a[0][0]>=b[0][0]) and (a[0][0]<=b[0][1]) and \
        (a[0][1]>=b[0][0]) and (a[0][1]<=b[0][1]) and \
        (a[1][0]>=b[1][0]) and (a[1][0]<=b[1][1]) and \
        (a[1][1]>=b[1][0]) and (a[1][0]<=b[1][1])

def list_good_cuts (M,fmts):
    if os.path.isfile('gcuts.bin'):
        return pickle.load(open('gcuts.bin','rb'))

    cuts = []
    for fmt in fmts:
        for c in range(C):
            for r in range(R):
                #print('%d %d %d x %d' % (c,r,fmt[0],fmt[1]))
                a = ((r,c),(r+fmt[0]-1,c+fmt[1]-1))
                if is_in (a,((0,R),(0,C))) and get_hams(M,a)>=3:
                    cuts.append(a)
    pickle.dump(cuts,open('gcuts.bin','wb'))
    return(cuts)

def init_solution (M, g_cuts):
    ng = len(g_cuts)
    is_kept = np.zeros((ng,1))


def read_data (in_file):
    with open(in_file,'r') as fp:
        d = fp.readline().split(' ')
        vs = []
        for x in fp.readlines():
            v = x.strip().replace('H','1').replace('T','0')
            v = list(map(int,v))
            vs.append(v)
        M = np.vstack(tuple(vs))
        print(M)
    return M

if __name__ == "__main__":

    M = read_data ('test_round.in')

    #cuts = get_cuts(M)
    #score = comp_score(M,cuts)

    # list good cuts
    g_cuts = list_good_cuts(M,list_fmts(M))

    # find init solution
    init_solution (M, g_cuts)

    #print(score)