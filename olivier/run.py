import sys
import copy
import math


def distance(r1, c1, r2, c2):
    if (r1==r2) and (c1==c2):
        return 0
    return math.ceil (math.sqrt ((r1-r2)**2+(c1-c2)**2))


class Warehouse:
    def __init__ (self, id, r, c, items):
        self.id = id
        self.r = r
        self.c = c
        self.items = items

    def __str__ (self):
        s='[warehouse %d] %d %d %s\n' % (self.id, self.r, self.c, ' , '.join(['%d:%d'%(i,e) for i,e in enumerate(w.items) if e!=0]))

class Order:
    def __init__ (self, id, r, c, items):
        self.id = id
        self.r = r
        self.c = c
        self.items = items

class Drone:
    def __init__ (self, id, r, c, n_types):
        self.id = id
        self.r = r
        self.c = c
        self.busy = False
        self.time = 0
        self.items = [0]*n_types

class Game:
    def __init__ (self, maxr, maxc, duration, maxload, ntypes, drones, orders, warehouses):
        self.maxr = maxr
        self.maxc = maxc
        self.duration = duration
        self.maxload = maxload
        self.drones = drones
        self.orders = orders
        self.warehouses = warehouses
        self.commands = []
        self.n_types = ntypes

    def __str__ (self):
        s = 'grid %dx%d\n' % (self.maxr,self.maxc)
        s+= 'drones:\n'
        for d in self.drones:
            s+='\t[drone %d] %d,%d\n' %(d.id,d.r,d.c)
        s+='orders\n'
        for o in self.orders:
            s+='\t[order %d] %d %d %s\n' % (o.id, o.r, o.c, ' , '.join(['%d'%i for i,e in enumerate(o.items) if e != 0]))
        s+='warehouses\n'
        for w in self.warehouses:
            s+='\t[warehouse %d] %d %d %s\n' % (w.id, w.r, w.c, ' , '.join(['%d:%d'%(i,e) for i,e in enumerate(w.items) if e!=0]))
        return s

    def allocate_orders_to_warehouses (self):
        for o in self.orders:
            scores = []
            for w in self.warehouses:
                scores.append(score_order_warehouse (o, w))
                break
            break
            print(scores)
        pass

    
    def load_solution (self, filename):
        self.commands = []
        with open (filename,'r') as fp:
            ncommands = int(fp.readline())
            for i,a in enumerate(fp.readlines()):
                s = a.strip().replace('L','0').replace('U','1').replace('D','2').replace('W','3').split(' ')
                s = [int(c) for c in s]
                self.commands.append(s)
            assert (ncommands == len(self.commands))


    def execute (self, command):
        points=0
        d = self.drones[command[0]]
        if command[1]==0 or command[1]==1:
            w = self.warehouses[command[2]]
            d.time += distance(d.r, d.c, w.r, w.c)
            #print ('drone %d moved %d,%d --> %d,%d.  cost=%d.  time=%d' % (d.id, d.r, d.c, w.r, w.c, distance(d.r, d.c, w.r, w.c), d.time))
            d.r = w.r
            d.c = w.c
            if command[1]==0:
                w.items[command[3]]-=command[4]
                d.items[command[3]]+=command[4]
            else:
                w.items[command[3]]+=command[4]
                d.items[command[3]]-=command[4]
            assert(w.items[command[3]]>=0)
        elif command[1]==2:
            o = self.orders[command[2]]
            d.time += distance(d.r, d.c, o.r, o.c)
            #print ('drone %d moved %d,%d --> %d,%d.  cost=%d.  time=%d' % (d.id, d.r, d.c, o.r, o.c, distance(d.r, d.c, o.r, o.c), d.time))
            d.r = o.r
            d.c = o.c
            assert(d.items[command[3]]>=command[4])
            o.items[command[3]]-=command[4]
            d.items[command[3]]-=command[4]
            # check item is fullfilled
            if sum(o.items)==0:
                #print ('order %d is fullfilled at time %d by drone %d!' % (o.id, d.time, d.id))
                points += math.ceil (100.0*(1.0*self.duration-1.0*d.time)/(1.0*self.duration))
        elif command[1]==3:
            d.time += command[2]
        return points

    
    def save_state (self):
        self._drones = copy.deepcopy(self.drones)
        self._orders = copy.deepcopy (self.orders)
        self._warehouses = copy.deepcopy (self.warehouses)

    def restore_state (self):
        self.drones = self._drones
        self.orders = self._orders
        self.warehouses = self._warehouses

    def run (self):
        points=0
        self.save_state ()
        for command in self.commands:
            points += self.execute(command)
        self.restore_state()
        return points


    def solve (self):
        # todo : allocate orders to warehouses, allocate drones to warehouse, pick best order
        pass


def read_data (filename):
    with open (filename,'r') as fp:
        # main params
        C, R, DRONES, DURATION, MAXLOAD = [int(a) for a in fp.readline().strip().split(' ')]
        # weights
        NTYPES = int(fp.readline())
        WEIGHTS = [int(a) for a in fp.readline().strip().split(' ')]
        assert(len(WEIGHTS)==NTYPES)
        # warehouses
        warehouses = []
        NWARE = int(fp.readline())
        for k in range(NWARE):
            r,c = [int(a) for a in fp.readline().strip().split(' ')]
            items = [int(a) for a in fp.readline().strip().split(' ')]
            assert(len(items)==NTYPES)
            warehouses.append (Warehouse (k, r, c, items))
        # orders
        orders = []
        NORDERS = int(fp.readline())
        for k in range(NORDERS):
            r,c = [int(a) for a in fp.readline().strip().split(' ')]
            nitems = int(fp.readline())
            ptypes = [int(a) for a in fp.readline().strip().split(' ')]
            assert(len(ptypes)==nitems)
            items = [0]*NTYPES
            for t in ptypes:
                items[t]+=1
            orders.append (Order(k,r,c,items))
        # drones
        drones = []
        for k in range(DRONES):
            drones.append(Drone(k,warehouses[0].r,warehouses[0].c, NTYPES))
    game = Game(C, R, DURATION, MAXLOAD, NTYPES, drones, orders, warehouses)
    return game


def main(filename, solution):
    game = read_data (filename)
 #   print(game)
    #game.allocate_orders_to_warehouses()
    if solution is not None:
        game.load_solution (solution)
        game.run()
        game.run()
        game.run()

if __name__ == "__main__":
    filename = sys.argv[1]
    solution=None
    if len(sys.argv)>2:
        solution = sys.argv[2]
    main(filename, solution)

