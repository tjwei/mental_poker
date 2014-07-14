from utils import LoadFuncs

def zk(imp):
    n, N = imp['n'], imp['N']
    send, recv, send_recv, broadcast = LoadFuncs(
        imp, 'send', 'recv', 'send_recv', 'broadcast')
    
    def ZKAK_Verify_4move(n2, g, X):        
        _G=g.G
        if n2==n:
            return
        i1, j1, i2, j2 = [_G.random_index() for _ in range(4)]
        h1, h2 = g**i1 * X**j1, g**i2 * X**j2        
        c,B = send_recv(n2, (h1,h2))        
        i3, j3 = (i1*c + i2)%_G.q, (j1*c + j2)%_G.q
        k = _G.random_index()
        r,z = send_recv(n2, (i3,j3,k))
        assert g**(z+i1*r) == X**(k-(c+j1)*r)*B    

    def ZKAK_Prove_4move(g, x):        
        _G=g.G
        B0 =[None]*N
        cdr = [[_G.random_index() for _ in range(3)] for n2 in range(N)]
        for n2 in range(N):
            if n2 !=n:
                c,d,r = cdr[n2]
                B0[n2] = g**(x*c*r+d)
        H = [recv(n2) for n2 in range(N)]        
        for n2 in range(N):
            if n2 !=n:
                c,d,r =cdr[n2]
                B = B0[n2] * H[n2][0]** cdr[n2][2]
                send(n2, (c, B))
        for n2 in range(N):
            if n2 != n:
                c, d, r = cdr[n2]
                h1, h2 = H[n2]
                i3,j3,k =recv(n2)
                assert g**(x*j3+i3) == h1**c * h2
                z = (k*x+d)%_G.q
                send(n2, (r,z))
                
    def ZKAK_Verify_5move(n2, g, X):        
        _G=g.G
        if n2==n:
            return
        c,d = _G.random_index(), _G.random_index()
        Xc = X**c
        Y=recv(n2)
        B = send_recv(n2, Xc * Y**d)
        l, y = send_recv(n2, (c,d))
        assert g**l == Xc*B
        assert Y == X**y


    def ZKAK_Prove_5move(g, x):        
        _G=g.G
        y=[_G.random_index() for _ in range(N)]
        s=[_G.random_index() for _ in range(N)]
        for n2 in range(N):
            if n2!=n:
                send(n2, g**(x*y[n2]))
        A = []
        for n2 in range(N):
            if n2!=n:
                A.append(recv(n2))
                send(n2, g**s[n2])
            else:
                A.append(None)
        for n2 in range(N):
            if n2!=n:
                c,d = recv(n2)
                assert A[n2] == g**(x*c + x*y[n2]*d)
                send(n2, (c*x+s[n2], y[n2]))
        
    def ZKA2_Verify(n2, a,b,c,d):
        assert a.G == b.G == c.G == d.G        
        if n2==n:
            return
        _G=a.G        
        l,m = _G.random_index(), _G.random_index()
        e = a**l * c**m
        f1,f2 = send_recv(n2, e)
        k = send_recv(n2,(l,m))
        assert e**k == f1
        assert b**(l*k) * d**(m*k) == f2

    def ZKA2_Prove(x, a, c):
        assert a.G == c.G        
        _G = a.G
        K = [_G.random_index() for n2 in range(N)]
        E = [recv(n2) for n2 in range(N)]
        for n2 in range(N):
            if n2 != n:
                e, k = E[n2], K[n2]
                f1, f2 = e**k, e**(k*x)
                send(n2, (f1, f2))
        for n2 in range(N):
            if n != n2:
                l,m = recv(n2)
                assert E[n2] == a**l * c**m
                send(n2, K[n2])    
    return locals()
