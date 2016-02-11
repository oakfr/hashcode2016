import numpy as np
import os
import sys
import random
from scipy.optimize import linprog

def show (M):
    for r in range(M.shape[0]):
        str = ''
        for c in range(M.shape[1]):
            if M[r,c]:
                str += '#'
            else:
                str += '.'
        print(str)

def check_sol_file (in_file):
    with open(in_file,'r') as fp:
        n = int(fp.readline())
        print(n)

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

def greedy_solution(M,R,C):

    S = np.copy(M)
    commands = []
    changed = True
    while np.sum(S)>0 and changed:
        changed = False

        # search for columns
        for c in range(C):
            (z,p,ia) = rle(S[:,c])
            z = z[ia==1]
            p = p[ia==1]
            if z.size==0 or np.amax(z)<3:
                continue
            r1 = p[np.argmax(z)]
            r2 = r1+np.amax(z)-1
            c1 = c
            c2 = c
            cmd = (r1,c1,r2,c2,1)
            S[r1:r2+1,c1:c2+1]=0
            commands.append(cmd)
            changed = True
            break
        # search for rows
        for r in range(R):
            (z,p,ia) = rle(S[r,:])
            z = z[ia==1]
            p = p[ia==1]
            if z.size==0 or np.amax(z)<3:
                continue
            c1 = p[np.argmax(z)]
            c2 = c1+np.amax(z)-1
            r1 = r
            r2 = r
            cmd = (r1,c1,r2,c2,1)
            S[r1:r2+1,c1:c2+1]=0
            commands.append(cmd)
            changed = True
            break
        # finish with single cells
        ind = np.array(list(np.where(S>0))).transpose()
        for i in range(ind.shape[0]):
            cmd = (ind[i][0],ind[i][1],ind[i][0],ind[i][1],1)
            commands.append(cmd)
            S[ind[i][0],ind[i][1]]=0
    return commands

def get_score(M,R,C,commands):
    assert(check_sol(M,R,C,commands))
    S = np.zeros((R,C))
    for cmd in commands:
        S[cmd[0]:cmd[2]+1,cmd[1]:cmd[3]+1]=1
    d = np.sum((S>0) & (M>0))
    return R*C - len(commands)

def check_sol(M,R,C,commands):
    S = np.zeros((R,C))
    n_erase = 0
    for cmd in commands:
        if cmd[4]>0:
            S[cmd[0]:cmd[2]+1,cmd[1]:cmd[3]+1]=1
        else:
            assert((cmd[0]==cmd[2]) and (cmd[1]==cmd[3]))
            S[cmd[0]:cmd[2]+1,cmd[1]:cmd[3]+1]=0
            n_erase += 1
    d1 = np.sum((S>0) & (M>0))
    d2 = np.sum(S>0)
#    show(S)
    if d1 != d2:
        print('*** Failure***.  # diffs : %d' % np.sum(np.abs(S-M)))
    return d1==d2


def print_solution(commands,out_file):
    with open(out_file,'w') as fp:
        fp.write('%d\n' % len(commands))
        for cmd in commands:
            if cmd[4]==-1:
                assert((cmd[0]==cmd[2]) and (cmd[1]==cmd[3]))
                fp.write('ERASE_CELL %d %d' % (cmd[0],cmd[1]))
            else:
                if (cmd[0]==cmd[2]) or (cmd[1]==cmd[3]):
                    fp.write('PAINT_LINE %d %d %d %d\n' % (cmd[0],cmd[1],cmd[2],cmd[3]))
                else:
                    assert(cmd[2]-cmd[0]==cmd[3]-cmd[1])
                    s = (cmd[2]-cmd[0])/2
                    c0 = cmd[0]+s
                    r0 = cmd[1]+s
                    fp.write('PAINT_SQUARE %d %d %d' % (r0,c0,s))


def list_commands(R,C):
    commands = []

    # paint_square
    for r in range(1,R-1):
        for c in range(1,C-1):
            for s in range(1,max([R,C])):
                if ((r-s)<0) or ((r+s)>R-1) or ((c-s)<0) or ((c+s)>C-1):
                    continue
                commands.append((r-s,c-s,r+s,c+s,1))
    # paint line
    for r in range(R):
        for c1 in range(C):
            for c2 in range(c1,C):
                commands.append((r,c1,r,c2,1))
    for c in range(C):
        for r1 in range(R):
            for r2 in range(r1,R):
                commands.append((r1,c,r2,c,1))

    # erase commands
    for r in range(R):
        for c in range(C):
            commands.append((r,c,r,c,-1))

    return commands

def is_in (a,b):
    return (a[0]>=b[0]) and (a[2]<=b[2]) and (a[1]>=b[1]) and (a[3]<=b[3])

def iterate_sol (M,R,C,greedy_sol,all_commands):

    stepr = min([5,int(R-1)])
    stepc = min([5,int(C-1)])

    # pick a random rectangle
    r1 = random.randint(0,R-stepr-1)
    r2 = r1+stepr
    c1 = random.randint(0,C-stepc-1)
    c2 = c1+stepc
    print((r1,r2,c1,c2))
    #r1 = 2
    #r2 = 10
    #c1 = 2
    #c2 = 10
    nr = r2-r1+1
    nc = c2-c1+1

    # remove all commands inside the target
    new_greedy_cmds = []
    for cmd in greedy_cmds:
        if not is_in(cmd,[r1,c1,r2,c2]):
            new_greedy_cmds.append(cmd)
    print('Command set from %d to %d' % (len(greedy_cmds),len(new_greedy_cmds)))

    # list possible commands inside the target
    possible_cmds = []
    for cmd in all_commands:
        if is_in (cmd, [r1,c1,r2,c2]):
            possible_cmds.append(cmd)
    print('%d possible commands' % len(possible_cmds))

    # build matching matrix
    A = np.zeros((nr*nc,len(possible_cmds)))
    B = np.zeros(nr*nc)

    print('building %d x %d matrix' % (A.shape[0],A.shape[1]))

    id = 0
    for r in range(r1,r2+1):
        for c in range(c1,c2+1):
            for j in range(A.shape[1]):
                A[id,j] = is_in ([r,c,r,c],possible_cmds[j]) * possible_cmds[j][4]
            B[id] = M[r,c]
            id += 1

    C = np.zeros(A.shape[1])+1

    res = linprog(C, None, None, A, B, bounds=(0,1))

    if res.success:
        resx = np.round(res.x)
        for (xv,idx) in zip(resx,range(len(resx))):
            if xv == 1:
                new_greedy_cmds.append(possible_cmds[idx])

    return new_greedy_cmds


if __name__ == "__main__":

    in_files = ['logo.in','learn_and_teach.in','right_angle.in']
    in_files = ['logo.in']
    for in_file in in_files:

        (M,R,C) = read_data(in_file)

        print('building greedy solution')
        greedy_cmds = greedy_solution(M,R,C)

        print(check_sol(M,R,C,greedy_cmds))

        score = get_score(M,R,C,greedy_cmds)
        print(score)

        # improve
        for k in range(1000):
            greedy_cmds = iterate_sol(M,R,C,greedy_cmds,list_commands(R,C))

            print(check_sol(M,R,C,greedy_cmds))

            score = get_score(M,R,C,greedy_cmds)
            print(score)

            out_file = 'output/out_%d_%s' % (score,in_file)
            print_solution(greedy_cmds,out_file)

            print('check output file')
            check_sol_file(out_file)

    #commands = list_commands (R,C)

