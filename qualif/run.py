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



def _dist(a,b):
    return (a[0]-b[0])**2+(a[1]-b[1])**2

def _fetch_product (wh,NP,product_rank):
    for k in product_rank:
        if wh[3+k[0]]>0:
            return(k[0])
    return -1

def read_data (in_file):
    with open(in_file,'r') as fp:
        d = [int(x) for x in fp.readline().strip().split(' ')]
        R = d[0]
        C = d[1]
        D = d[2]
        T = d[3]
        P = d[4]
        d = [int(x) for x in fp.readline().strip().split(' ')]
        NP = d[0]
        W = [int(x) for x in fp.readline().strip().split(' ')]
        d = [int(x) for x in fp.readline().strip().split(' ')]
        NW = d[0]

        # parse houses
        WHS = []
        for h in range(NW):
            d = [int(x) for x in fp.readline().strip().split(' ')]
            w = np.zeros(2+NP)
            w[0] = d[0]
            w[1] = d[1]
            w[2:] = [int(x) for x in fp.readline().strip().split(' ')]
            WHS.append(w)

        # drone start position
        DS = WHS[0][:2]
        print(DS)

        # parse orders
        d = [int(x) for x in fp.readline().strip().split(' ')]
        NO = d[0]
        ORS = []
        for no in range(NO):
            d = [int(x) for x in fp.readline().strip().split(' ')]
            o = np.zeros(3+NP)
            o[0] = d[0]
            o[1] = d[1]
            d = [int(x) for x in fp.readline().strip().split(' ')]
            o[2] = d[0]
            d = [int(x) for x in fp.readline().strip().split(' ')]
            for k in d:
                o[3+k] += 1
            ORS.append(o)
        
    return (R,C,D,T,P,NP,W,NW,WHS,NO,ORS,DS)

def process_drone (DC,R,C,D,T,P,NP,W,NW,WHS,NO,ORS,DS,product_rank):

    droneid = random.randint(0,D-1)
    
    # find nearest non-empty warehouse
    best_dist=0
    whi = -1
    for (w,i) in zip(WHS,range(NW)):
        if np.sum(w[2:])==0:
            continue
        d = _dist(w[:2],DS)
        if whi == -1 or d < best_dist:
            best_dist = d
            whi = i
    print('best warehouse %d' % whi)
    
    if whi == -1:
        return None

    # fill the drone
    cur_p = P
    loads = []
    while True:
        k = _fetch_product (WHS[whi],NP,product_rank) 
        if k == -1:
            break
        if cur_p - W[k] < 0:
            break
        cur_p -= W[k]
        WHS[whi][2:k]-=1
        print('drone %d loaded 1 item of %d (weights %d)' % (droneid,k,W[k]))
        loads.append([droneid,whi,1,k,0])

    print('# loads: %d'% len(loads))

    # deliver
    unloads = []
    delivers = []
    for k in range(len(loads)):
        ltype = loads[k][3]
        delivered=False
        for io in range(NO):
            o = ORS[io]
            if o[3+ltype]>0:
                ORS[io][3+ltype]-=1
                delivers.append([droneid,io,ltype,1,1])
                print('drone %d delivered item of type %d to order %d' % (droneid,ltype,io))
                delivered=True
                break
        if not delivered:
            # unload if nobody wants it
            unloads.append([droneid,whi,ltype,1,2])
            print('droneid %d unloading item of type %d to wh %d' % (droneid,ltype,whi))

    # make sure we don't go over time for that drone
    nops = len(loads)+len(unloads)+len(delivers)
    if DC[droneid]+nops>T:
        return None

    DC[droneid] += nops

    return (DC,WHS,ORS,loads,unloads,delivers)

def write_solution (out_file, commands):
    nops = len(commands)
    
    with open(out_file,'w') as fp:
        fp.write('%d\n' % nops)
        for i in range(nops):
            cmd = commands[i]
            if cmd[4]==0:
                fp.write('%d L %d %d %d\n' % (cmd[0],cmd[1],cmd[3],cmd[2]))
            elif cmd[4]==2:
                fp.write('%d U %d %d %d\n' % (cmd[0],cmd[1],cmd[3],cmd[2]))
            elif cmd[4]==1:
                fp.write('%d D %d %d %d\n' % (cmd[0],cmd[1],cmd[2],cmd[3]))
            else:
                assert(False)

def compute_rank (ORS,NP,NO):
    products = []
    for p in range(NP):
        count=0
        for o in range(NO):
            count += ORS[o][3+p]
        products.append([p,count])
    product_rank = sorted(products,key=lambda x:-x[1])
    return product_rank

if __name__ == "__main__":
       
    # there!
    in_files = ['busy_day.in', 'mother_of_all_warehouses.in', 'redundancy.in']
    in_files = ['mother_of_all_warehouses.in']

    random.seed(123456)

    for in_file in in_files:

        (R,C,D,T,P,NP,W,NW,WHS,NO,ORS,DS) = read_data (in_file)

        DC = np.zeros(D)

        all_commands = None
        
        num_iter = 30
        for b in range(num_iter):

            # rank products
            product_rank = compute_rank(ORS,NP,NO)

            res = process_drone (DC,R,C,D,T,P,NP,W,NW,WHS,NO,ORS,DS,product_rank)
            if res is not None:
                (DC,WHS,ORS,loads,unloads,delivers) = res
                #print(loads)
                #print(unloads)
                #print(delivers)
                if len(loads)>0:
                    if all_commands == None:
                        all_commands = loads
                    else:
                        all_commands = np.vstack((all_commands,loads))
                if len(unloads)>0:
                    if all_commands == None:
                      all_commands = unloads
                    else:
                        all_commands = np.vstack((all_commands,unloads))
                if len(delivers)>0:
                    if all_commands == None:
                        all_commands = delivers
                    else:
                        all_commands = np.vstack((all_commands,delivers))
            #all_unloads = np.concatenate((all_unloads,unloads))
            #all_delivers = np.concatenate((all_delivers,delivers))

        print(all_commands)

        print('writing solution')
        out_file = 'output/out_%s.txt' % in_file
        write_solution (out_file, all_commands)

