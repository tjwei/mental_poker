from gmpy2 import mpz
from utils import Group, reset_rs, GroupElement, prod
from utils import LoadFuncs, init_players
from random import shuffle
from zk import zk
from basic_protocol import basic_protocol

q=mpz(open("prime1024.txt").read())
#q=mpz(open("prime.txt").read())
#q=mpz(100012421)
G, H=Group(q*2+1), Group(q) # G and H are global variables
L=30

def mcrp(n, conn, network):
    reset_rs()    
    cmd=conn[n]
    send, recv, send_recv, broadcast = LoadFuncs(
        network, 'send', 'recv', 'send_recv', 'broadcast')

    ZKA2_Prove, ZKA2_Verify, ZKAK_Prove, ZKAK_Verify = LoadFuncs(
        zk, 'ZKA2_Prove', 'ZKA2_Verify', 'ZKAK_Prove_5move', 'ZKAK_Verify_5move')

    KeyGen, VExp, VExp_Verify, Rand, Enc, Draw, Open= LoadFuncs(
        basic_protocol, 'KeyGen', 'VExp', 'VExp_Verify', 'Rand', 'Enc', 'Draw', 'Open')
    
    def Mixup(D,_y,_pi):
        def _pow(d, y):
            return (d[0]**y, d[1]**y)
        return [_pow(D[_pi[m]],_y) for m in range(M)]    

    def SP(D):
        _pi = list(range(M))
        shuffle(_pi)
        _y = H.random_generator()                
        D = Mixup(D, _y, _pi)
        return D, _y, _pi
    
    def SV_Prove(n0, D0, D1, y, pi):
       for l in range(L):
           D2, y2, pi2 = SP(D1)
           broadcast(D2)
           b = Rand(G).v&1
           if b == 1:
               broadcast((y2,pi2))
           else:
               p3 = [pi[pi2[m]] for m in range(M)]
               broadcast((y2*y, p3))
               
    def SV_Verify(n0, D0, D1):
       for l in range(L):
           D2 = recv(n0)           
           b = Rand(G).v&1
           y2,pi2 = recv(n0)
           if b == 1:
               D=D1               
           else:
               D=D0
           assert Mixup(D, y2, pi2) == D2
           
    while True:
        act = cmd.recv()        
        if act == "end":
            cmd.send('done')
            break
        elif act == "Init":        
            gamma, _x=KeyGen()
            c = [GroupElement((1+m)**2, H) for m in range(M)]
            rand_a = (Rand(G) for m in range(M))
            D_0 = [(a**t, Enc(a, _x, gamma)) for a,t in zip(rand_a, c)]
            
        elif act == "Shuffle":
            D = D_0
            for n2 in range(N):
                D_last = D
                if n == n2:
                    D, _y, _pi =SP(D)
                    broadcast(D)
                    SV_Prove(n2, D_last, D, _y, _pi)
                else:
                    D = recv(n2)
                    SV_Verify(n2, D_last, D)                    
            D_INFO = [None]*M
            
        elif act == "Draw":
            n0 = cmd.recv()                        
            m0 = cmd.recv()            
            D_INFO[m0] = Draw(n0, D[m0], c, _x, gamma)
                
        elif act == "Open":
            m0 = cmd.recv()
            m = Open(D[m0][1], c, D_INFO[m0], _x, gamma)
            
        else:
            print "Unknown action", act        
        cmd.send('done')
             
N, M, K=9, 52, 4

if __name__=="__main__":    
    send_command, join = init_players(N, mcrp)       
    send_command("Init")
    send_command("Shuffle")
    send_command("Draw", 0, 0)
    send_command("Open", 0)
    send_command("end")
    join()

       
