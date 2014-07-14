import gmpy2
from os import urandom
from struct import unpack
from gmpy2 import mpz, powmod, mpz_random, is_prime, invert

__rs=gmpy2.random_state()

def reset_rs():
    global __rs
    seed=unpack("L", urandom(8))[0]    
    __rs=gmpy2.random_state(seed)

def rand(n):    
    return mpz_random(__rs, n)    

def prod(seq):
    r=None
    for x in seq:
        if r is None:
            r=x
        else:
            r=r*x
    return r

def value(x):
        return x.v if isinstance(x, GroupElement) else x
class GroupElement:
    def __init__(self, v, G):
        self.G=G
        self.v=v
        #assert gmpy2.legendre(v, G.p)==1

    def conv(self, x):
        if isinstance(x, GroupElement):
            assert self.G==x.G
            return x
        else:
            return GroupElement(x%self.G.p, self.G)
    def __pow__(self, x):        
        return self.conv(powmod(self.v, value(x), self.G.p))
    def __add__(self, x):        
        return self.conv(self.v+value(x))
    def __radd__(self, x):        
        return self.conv(value(x)+self.v)
    def __sub__(self, x):
        return self.conv(self.v-value(x))
    def __mul__(self, x):
        return self.conv(self.v*value(x))
    def __rmul__(self, x):
        return self.conv(value(x)*self.v)
    def __mod__(self, x):
        return self.conv(self.v%value(x))
    def invert(self):
        return self.conv(invert(self.v, self.G.p))
    def __div__(self, x):
        return self*x.invert()
    def __eq__(self,x):
        return self.v == value(x)
    def __repr__(self):
        return str(self.v)+"/G"
    #+str(self.G)
        

class Group:
    def __init__(self, q):
        self.p, self.q = q*2+1, q
        assert is_prime(self.p), is_prime(self.q)
        self.g=self.random_generator()
    def __eq__(self, x):
        return self.p==x.p        
    def random_generator(self):
        return GroupElement( powmod((2+rand(self.q-3)),2,self.p), self)
    def random_index(self):
        return 1+rand(self.q-1)        
    def __repr__(self):
        return "G(%d)"%self.q    

from types import FunctionType
from inspect import currentframe
from multiprocessing import Process, Pipe
from time import time

def LoadFuncs(provider, *names):
    if isinstance(provider, FunctionType):
        frame = currentframe()
        d = {}
        d.update(frame.f_back.f_globals)
        d.update(frame.f_back.f_locals)
        imp =  provider(d)
    else:
        imp = provider
    return [imp[n] for n in names]

def multiprocess_conn(imp):
    n, conn, N = imp['n'], imp['conn'], imp['N']
    def send(n2, msg, count=True):
        global num_messages
        if n2 !=n:            
            conn[n2].send(msg)
            
    def recv(n2):        
        return conn[n2].recv() if n!=n2 else None

    def send_recv(n2, msg):
        send(n2, msg)
        return recv(n2)

    def broadcast(msg):
        for n2 in range(N):
            send(n2, msg)
        return msg
    return locals()

def init_players(N, func):
    conn_dict={}
    cmd={}    
    for n1 in range(N):
        cmd[n1], conn_dict[n1,n1]=Pipe()
        for n2 in range(n1+1, N):
            conn_dict[n1,n2], conn_dict[n2,n1]=Pipe()
    def conn_list(n):
        return [conn_dict[n,n2] for n2 in range(N)]
    def send_command(*msgs):
        t0=time()
        print "send", msgs
        for m in msgs:
            for n in range(N):
                cmd[n].send(m)
        for n in range(N):
            assert cmd[n].recv()=='done'
        print msgs, "done", time()-t0
    def join():
        for p in players:
            p.join()
    players=[Process(target=func, args =(n, conn_list(n), multiprocess_conn)) for n in range(N)]
    for p in players:
       p.start()
    return send_command, join
