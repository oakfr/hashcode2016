import numpy as np

def init_map (n_rows, n_cols, dead_slots):

    M = np.zeros((n_rows,n_cols)).astype(int)
    for dead_slot in dead_slots:
        M[dead_slot[0],dead_slot[1]]=1
    return M

def print_map (M):
    for i in range(M.shape[0]):
        str = '[%03d] ' % i
        for j in range(M.shape[1]):
            str += '%d' % M[i,j]
            if (j+1)%10==0:
                str += ' '
        print(str)

def update_map (M, servers):
    for s in servers:
        if s[2] != -1 and s[3] != -1:
            assert(M[s[2],s[3]:s[3]+s[0]]==0).all()
            M[s[2],s[3]:s[3]+s[0]]=1
    return M

def avail_slot (M,row,size):
    for k in range(M.shape[1]-size):
        if (M[row,k:k+size]==0).all():
            return k
    return -1

def read_data(in_file):
    with open(in_file) as fp:
        lines = fp.readlines()
    d = lines[0].split(' ')
    n_rows = int(d[0])
    n_cols = int(d[1])
    n_unav = int(d[2])
    n_pools = int(d[3])
    n_servers = int(d[4])

    # unavailable slots
    dead_slots = []
    for i in range(1,n_unav):
        d = lines[i].split(' ')
        dead_slots.append((int(d[0]),int(d[1])))

    # servers (size, capacity, row, col, pool)
    servers = []
    for i in range(1+n_unav,len(lines)):
        d = lines[i].split(' ')
        servers.append([int(d[0]),int(d[1]),-1,-1,-1])

    return (n_rows,n_cols,n_pools,dead_slots,servers)

def read_solution (in_file, servers):
    with open(in_file,'r') as fp:
        lines = fp.readlines()

    for (i,line) in zip(range(len(lines)),lines):
        if line.find('x') is not -1:
            continue
        d = line.split(' ')
        servers[i][2] = int(d[0])
        servers[i][3] = int(d[1])
        servers[i][4] = int(d[2])

    return servers

def score_pool (servers, n_rows, i_pool):
    pool_cap_per_row = np.zeros(n_rows)
    for s in servers:
        capacity = s[1]
        row = s[2]
        pool = s[4]
        if pool == i_pool:
            pool_cap_per_row[row] += capacity
    score = int(np.sum(pool_cap_per_row) - np.amax(pool_cap_per_row))
    return score

def score (servers, n_pools, n_rows):
    return np.amin([score_pool(servers,n_rows,pool) for pool in range(n_pools)])

def alloc_servers (M, servers):
    target_row = 0
    target_pool = 0
    n_rows = M.shape[0]
    n_cols = M.shape[1]
    for s in servers:
        r = avail_slot(M,target_row,s[0])
        for k in range(n_rows):
            target_row = (target_row+1)%n_rows



if __name__ == "__main__":

    # read data
    (n_rows,n_cols,n_pools,dead_slots,servers) = read_data('dc.in')

    # init map
    M = init_map (n_rows,n_cols,dead_slots)

    # allocation
    servers = read_solution('res_0000000418', servers)

    # score
    score = score(servers, n_pools, n_rows)
    print(score)

    # update map
    M = update_map (M, servers)

    #print_map (M)

