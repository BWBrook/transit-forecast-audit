"""Host-resampling sizing for the T015 confirmation experiment (plan revision R6). Reads committed D039 tables only."""

import csv,collections,numpy as np
I=[r for r in csv.DictReader(open('results/t015_validation/injections.csv')) if r['status']=='timed' and r['flux']=='pdcsap']
rng=np.random.default_rng(7)
for prod in ('TESS-SPOC_200','SPOC_120'):
    by=collections.defaultdict(list)
    for r in I:
        if r['product']==prod: by[r['host']].append((float(r['z']),r['cover95']=='True',float(r['tmag'])))
    hosts=list(by); print(prod,'hosts',len(hosts),'mean inj/host',round(np.mean([len(v) for v in by.values()]),1))
    for H in (6,12,20,30,40,60):
        st=[]
        for _ in range(4000):
            pick=rng.integers(0,len(hosts),H)
            z=np.concatenate([[x[0] for x in by[hosts[i]]] for i in pick]); c=np.concatenate([[x[1] for x in by[hosts[i]]] for i in pick])
            st.append((np.sqrt(np.mean(z**2)),c.mean(),np.median(z)))
        s=np.array(st); print(f"  H={H:3d} sd zrms={s[:,0].std():.3f} sd cov95={s[:,1].std():.4f} sd medz={s[:,2].std():.3f}")
    # Tmag trend in z^2 across hosts
    t=np.array([by[h][0][2] for h in hosts]); m=np.array([np.mean([x[0]**2 for x in by[h]]) for h in hosts])
    b=np.polyfit(t-11,np.log(m),1); print('  log mean z^2 slope per mag',round(b[0],3))
