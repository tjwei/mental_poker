from utils import LoadFuncs
def basic_protocol(imp):
    n, N, M, G, H = imp['n'], imp['N'], imp['M'], imp['G'], imp['H']
    send, recv, send_recv, broadcast = LoadFuncs(
        imp, 'send', 'recv', 'send_recv', 'broadcast')

    ZKA2_Prove, ZKA2_Verify, ZKAK_Prove, ZKAK_Verify = LoadFuncs(
        imp, 'ZKA2_Prove', 'ZKA2_Verify', 'ZKAK_Prove', 'ZKAK_Verify')
    
    def KeyGen():
        gamma=[]
        for n2 in range(N):
            if n==n2:
                x = H.random_generator()
                gamma.append(G.g**x)
                broadcast(gamma[n])                
                ZKAK_Prove(G.g, x.v)
            else:
                gamma.append(recv(n2))
                ZKAK_Verify(n2, G.g, gamma[n2])
        return gamma, x                

    def VExp(x, g, a):        
        r= g**x
        broadcast(r)        
        ZKA2_Prove(x, a, g)
        return r
    
    def VExp_Verify(n2, g, a, b):
        r = recv(n2)
        ZKA2_Verify(n2, a, b, g, r)
        return r

    def Rand(_G):
        _r = _G.random_index()
        _g=[broadcast(_G.g**_r) if n==n2 else recv(n2) for n2 in range(N)]
        t=_G.g
        for n2 in range(N):
            t = VExp(_r, t, _G.g) if n==n2 else VExp_Verify(n2, t, _G.g, _g[n2])
        return t
    
    def Enc(r, _x, gamma):
        #assert gmpy2.legendre(r.v, G.p)==1
        for n2 in range(N):
            r = VExp(_x, r, G.g) if n==n2 else VExp_Verify(n2, r, G.g, gamma[n2])
        return r

    def Draw(n0, (a,b), c, _x, gamma):                
        r = a
        for n2 in range(N):
            if n2 != n0:                    
                r = VExp(_x, r, G.g) if n2 == n else VExp_Verify(n2, r, G.g, gamma[n2])
        if n0 == n:                
            r2 = r**_x                
            for m in range(M):
                if r2 == b**c[m]:
                    print n, "draw", m
                    break
            assert m < M
            return (n0, r, m)
        else:
            return (n0, r, -1)
    def Open(b, c, dinfo, _x, gamma):
        if dinfo is None:
            return None
        n0, r, m = dinfo
        if n0 == n:
            broadcast(m)
            VExp(_x, r, G.g)
        else:
            m = recv(n0)
            r2 = VExp_Verify(n0, r, G.g, gamma[n0])
            assert r2 == b**c[m]
            # Player n0 owns Card m
            return m
        
    return locals()
    
