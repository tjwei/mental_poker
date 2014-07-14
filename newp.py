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
       
def new_mp(n, conn, network):
    reset_rs()    
    cmd=conn[n]
    send, recv, send_recv, broadcast = LoadFuncs(
        network, 'send', 'recv', 'send_recv', 'broadcast')

    ZKA2_Prove, ZKA2_Verify, ZKAK_Prove, ZKAK_Verify = LoadFuncs(
        zk, 'ZKA2_Prove', 'ZKA2_Verify', 'ZKAK_Prove_5move', 'ZKAK_Verify_5move')
    
    KeyGen, VExp, VExp_Verify, Rand, Enc, Draw, Open= LoadFuncs(
        basic_protocol, 'KeyGen', 'VExp', 'VExp_Verify', 'Rand', 'Enc', 'Draw', 'Open')

    def Wrap_A(D_0):
        _e=[GroupElement(1, G) for m in range(M)]
        _lmbd = [H.random_generator() for i in range(3)]
        gp = G.g**_lmbd[2]
        e=[]
        for n2 in range(N):
            if n2 == n:
                _e = [_e[m] * D_0[m][0]**_lmbd[0] * D_0[m][1]**_lmbd[1] * gp for m in range(M)]
                broadcast(_e)
            else:
                _e = recv(n2)
            e.append(_e)        
        return ([D_0[m]+(e[N-1][m],) for m in range(M)], G.g),  _lmbd, e

    def Check_Secrets_A(lmbd, D0, e):
        if n > 0:
            l1, l2, l3 = [sum(lmbd[n2][i] for n2 in range(n)) for i in range(3)]
            gp = G.g**l3
            assert all(e[n-1][m] == D_0[m][0]**l1 * D_0[m][1]**l2 * gp for m in range(M))
        l1, l2, l3 = [sum(lmbd[n2][i] for n2 in range(N)) for i in range(3)]
        if n < N-1:            
            gp = G.g**l3
            assert all(e[N-1][m] == D_0[m][0]**l1 * D_0[m][1]**l2 * gp for m in range(M))
        return (l1, l2, l3)

    def Wrap_B0():        
        _u, _v = [H.random_index() for k in range(K)], [H.random_index() for k in range(K)]
        a, b = prod(f0[k]**_u[k] for k in range(K)), prod(f0[k]**_v[k] for k in range(K))        
        alpha_beta = [broadcast((a, b)) if n==n2 else recv(n2) for n2 in range(N)]
        delta = (prod(x[0] for x in alpha_beta), prod(x[1] for x in alpha_beta))        
        return delta, _u, _v, alpha_beta

    def Check_Secrets_B0(uv, alpha_beta):
        if n > 0:
            u = [sum(uv[n2][0][k] for n2 in range(n)) for k in range(K)]
            v = [sum(uv[n2][1][k] for n2 in range(n)) for k in range(K)]            
            a, b = prod(f0[k]**u[k] for k in range(K)), prod(f0[k]**v[k] for k in range(K))
            assert prod(alpha_beta[n2][0] for n2 in range(n)) == a
            assert prod(alpha_beta[n2][1] for n2 in range(n)) == b            
        u = [sum(uv[n2][0][k] for n2 in range(N)) for k in range(K)]
        v = [sum(uv[n2][1][k] for n2 in range(N)) for k in range(K)]    
        if n < N-1:
            a, b = prod(f0[k]**u[k] for k in range(K)), prod(f0[k]**v[k] for k in range(K))
            assert delta == (a,b)            
        return u, v
            
    def star( (y,z,w), ((a,ab,b,e),f) ):
        p1 = (a**(y*delta[0]**w), ab**(y*delta[1]**w), b**(y*z), e**y)        
        p2 = tuple(x[0]*x[1]**w for x in zip(f,f0))
        return (p1, p2)

    def Wrap_B((D_A, g0)):        
        h0 = [GroupElement(1, H) for k in range(K)]
        D0=[((a,a*b,b,e), h0) for (a,b,e) in D_A]
        D, g = D0, g0
        B_history=[]
        for n2 in range(N):
            if n2 == n:
                _y, _z = H.random_generator(), H.random_generator()
                _w = [H.random_index() for m in range(M)]                
                D =[star((_y,_z, _w[m]), D[m]) for m in range(M)]
                g = g**_y
                broadcast((D,g))
            else:
                D, g = recv(n2)
            B_history.append((D, g))
        B_history.append((D0, g0))
        return _y, _z, _w, B_history

    def Check_Secrets_B(yzw, B_history):
        D0, g0 = B_history[-1]
        if n > 0:
            D, g = B_history[n-1]                        
            Y = prod(yzw[n2][0] for n2 in range(n))
            Z = prod(yzw[n2][1] for n2 in range(n))
            W = [sum(yzw[n2][2][m] for n2 in range(n)) for m in range(M)]
            assert g == g0**Y
            assert all(star((Y,Z,W[m]), D0[m]) == D[m] for m in range(M) )
        Y = prod(yzw[n2][0] for n2 in range(N))
        Z = prod(yzw[n2][1] for n2 in range(N))
        W = [sum(yzw[n2][2][m] for n2 in range(N)) for m in range(M)]
        if n < N-1:
            D, g = B_history[N-1]            
            assert g == g0**Y
            assert all(star((Y,Z,W[m]), D0[m]) == D[m] for m in range(M) )
        return Z

    def NewSP(D):
        _pi = list(range(M))
        shuffle(_pi)
        _y = H.random_generator()
        w = [H.random_index() for m in range(M)]
        h = GroupElement(1,H)
        D = [star((_y, h, w[_pi[m]]), D[_pi[m]]) for m in range(M)]
        return D, _y, _pi
    
    def Shuffle_Main((D, g)):
        Main_history = []
        for n2 in range(N):
            last_g = g
            if n == n2:
                D, _y, _pi = NewSP(D)
                g = broadcast(g**_y)
                if n == N-1:                    
                    broadcast(D)
                else:
                    send(n+1, D)                                
                ZKAK_Prove(last_g, _y)
            else:
                g = recv(n2)
                D = recv(n2) if n2==N-1 or n2+1==n else None                    
                ZKAK_Verify(n2, last_g, g)
            Main_history.append((D,g))            
        return Main_history
    
    def Reveal_Check_Secrets(D_0, A_history, B0_history, B_history):
        yzw = [broadcast((_y, _z, _w)) if n2==n else recv(n2) for n2 in range(N-1,-1,-1)]        
        yzw.reverse()
        uv = [broadcast((_u, _v)) if n2==n else recv(n2) for n2 in range(N-1,-1,-1)]
        uv.reverse()        
        lmbd = [broadcast(_lmbd) if n2==n else recv(n2) for n2 in range(N-1,-1,-1)]
        lmbd.reverse()        
        l = Check_Secrets_A(lmbd, D_0, A_history)
        u,v = Check_Secrets_B0(uv, B0_history)
        Z = Check_Secrets_B(yzw, B_history)
        return l, u, v, Z

    def Unwrap_A((a,b,e), gp, l):
        assert a**l[0] * b**l[1] * gp == e
        return (a,b)
    
    def Unwrap_B( ((a,ab,b,e), f), Zi, u, v):
        Ui = prod(f[k]**u[k] for k in range(K)).invert()
        V = prod(f[k]**v[k] for k in range(K))
        ra, rb = a**Ui, b**Zi
        assert (ra*rb)**V == ab
        return (ra,rb,e)
    
    def Unwrap_Check_Deck( (DB, g), Z, u, v, l):
        Zi = Z.invert() # Zi is Z^-1
        DA = [Unwrap_B(d, Zi, u,v) for d in DB]
        # check 'e elements' are distinct
        assert len(set(d[2].v for d in DA)) == len(DA) 
        gp = g**l[2]
        return [Unwrap_A(d, gp, l) for d in DA]
    
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
            f0=[Rand(H) for k in range(K)]
            
        elif act == "Shuffle":            
            (D_A, g_A), _lmbd, A_history = Wrap_A(D_0)
            delta, _u, _v, B0_history = Wrap_B0()
            _y, _z, _w, B_history = Wrap_B((D_A, g_A))
            Main_history = Shuffle_Main( B_history[N-1])
            l, u, v, Z = Reveal_Check_Secrets(D_0, A_history, B0_history, B_history)
            if n > 0 and n < N-1:
                Unwrap_Check_Deck( Main_history[n-1], Z, u, v, l)            
            D = Unwrap_Check_Deck( Main_history[N-1], Z, u, v, l)
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
    send_command, join = init_players(N, new_mp)       
    send_command("Init")
    send_command("Shuffle")
    send_command("Draw", 0, 0)
    send_command("Open", 0)
    send_command("end")
    join()
