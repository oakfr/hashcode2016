import numpy as np
import os
import sys

def show (M):
    for r in range(M.shape[0]):
        str = ''
        for c in range(M.shape[1]):
            if M[r,c]:
                str += '#'
            else:
                str += '.'
        print(str)

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
            cmd = (r1,c1,r2,c2)
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
            cmd = (r1,c1,r2,c2)
            S[r1:r2+1,c1:c2+1]=0
            commands.append(cmd)
            changed = True
            break
        # finish with single cells
        #ind = np.array(list(np.where(S>0))).transpose()
        #for i in range(ind.shape[0]):
        #    cmd = [ind[i][0],ind[i][1],ind[i][0],ind[i][1]]
        #    commands.append(cmd)
        #    S[ind[i][0],ind[i][1]]=0
    return commands

def get_score(M,R,C,commands):
    S = np.zeros((R,C))
    for cmd in commands:
        S[cmd[0]:cmd[2]+1,cmd[1]:cmd[3]+1]=1
    d = np.sum((S>0) & (M>0))
    return d

def check_sol(M,R,C,commands):
    S = np.zeros((R,C))
    for cmd in commands:
        S[cmd[0]:cmd[2]+1,cmd[1]:cmd[3]+1]=1
    d1 = np.sum((S>0) & (M>0))
    d2 = np.sum(S>0)
    show(S)
    return d1==d2

def print_solution(commands,out_file):
    with open(out_file,'w') as fp:
        fp.write('%d\n' % len(commands))
        for cmd in commands:
            if (cmd[0]==cmd[2]) or (cmd[1]==cmd[3]):
                fp.write('PAINT_LINE %d %d %d %d\n' % (cmd[0],cmd[1],cmd[2],cmd[3]))

def list_commands(R,C):
    p_commands = []
    e_commands = []

    # paint_square
    for r in range(1,R-1):
        for c in range(1,C-1):
            for s in range(max([R,C])):
                if ((r-s)<0) or ((r+s)>R-1) or ((c-s)<0) or ((c+s)>C-1):
                    continue
                p_commands.append((r-s,r+s,c-s,c+s))
    # paint line
    for r in range(R):
        for c1 in range(C):
            for c2 in range(c1,C):
                p_commands.append((r,r,c1,c2))
    for c in range():
        for r1 in range(R):
            for r2 in range(r1,R):
                p_commands.append((r1,r2,c,c))

    # erase commands
    for r in range(R):
        for c in range(C):
            e_commands.append((r,c))

    return p_commands

if __name__ == "__main__":

    in_files = ['logo.in','learn_and_teach.in','right_angle.in']
    in_files = ['logo.in']
    for in_file in in_files:

        (M,R,C) = read_data(in_file)

        print('building greedy solution')
        commands = greedy_solution(M,R,C)

        score = get_score(M,R,C,commands)

        print(check_sol(M,R,C,commands))

        out_file = 'out_%s' % in_file
        print_solution(commands,out_file)

    #commands = list_commands (R,C)

