"""Valuación de BAC (Bank of America) — informe-bancos, actualización 3T 2026 (3-nov-2026).

Correr:  python valuacion.py
Reproduce el blend publicado en informes/bac.html ($53.61 vs $49.57, +8.1%).
Con los supuestos de la versión de sep-2026 (EPS 4.34, TBV 29.37, COE 10.75%) reproduce
al centavo los valores de entonces (DDM base $57.13, RIM base $48.74) — ver check_version_anterior().
Fuentes de cada dato: comentarios en el informe (8-K 14-oct-2026, 10-Q 3T26, XBRL, stockanalysis, Yahoo).
"""
def lin(a,b,n=5): return [a+(b-a)*i/(n-1) for i in range(n)]
def ddm(eps0,g1,g5,p1,p5,k,gT):
    gs,ps=lin(g1,g5),lin(p1,p5); e=eps0; pv=0
    for t in range(5):
        e*=1+gs[t]; d=e*ps[t]; pv+=d/(1+k)**(t+1)
    tv=d*(1+gT)/(k-gT)/(1+k)**5
    return pv+tv, tv/(pv+tv)
def rim(bv0,r1,r5,b1,b5,k,gT,tvmode=0):
    rs,bs=lin(r1,r5),lin(b1,b5); bv=bv0; pv=0
    for t in range(5):
        ri=(rs[t]-k)*bv; pv+=ri/(1+k)**(t+1); bv*=1+bs[t]
    tv=ri*(1+gT)/(k-gT)/(1+k)**5 if tvmode==0 else (rs[4]-k)*bv/(k-gT)/(1+k)**5
    return bv0+pv+tv
P=49.57; TBV=29.14; Rf=.0489; beta=1.21; ERP=.05
coe=Rf+beta*ERP; print('COE raw',round(coe*100,3))
k={'bear':.119,'base':.109,'bull':.099}
# EPS TTM
q=[0.98,1.11,1.21,0.91]; print('EPS TTM rep',sum(q),'adj',round(sum(q)+0.17,2))
EPS0=round(sum(q)+0.17,2)
# NI / payout
ni=[7647,8584,9074,6933]; bb=[6310,7240,6006,6005]; dv=[2052,2023,1993,2246]
print('NI TTM',sum(ni),'adj',sum(ni)+1200,'BB',sum(bb),'DIV',sum(dv),'tot',sum(bb)+sum(dv))
print('payout tot rep %.1f adj %.1f div %.1f'%(100*(sum(bb)+sum(dv))/sum(ni),100*(sum(bb)+sum(dv))/(sum(ni)+1200),100*sum(dv)/sum(ni)))
nii=[15750,15745,15997,16449]; nonii=[12617,14527,15561,13509]; exp=[17437,18531,18627,19722]
print('NII TTM',sum(nii),'nonII',sum(nonii),'exp',sum(exp),'eff %.1f'%(100*sum(exp)/(sum(nii)+sum(nonii))),'eff adj %.1f'%(100*(sum(exp)-1200)/(sum(nii)+sum(nonii))),'rev',sum(nii)+sum(nonii))
print('prov TTM',1308+1337+1366+1269)
rot=[14.0,16.0,17.0,14.9]; print('ROTCE 4Q adj avg',sum(rot)/4,'rep',(14.0+16+17+12.6)/4, '3y',(13.46+12.94+14.22)/3)
# DDM
D={}
D['bear']=ddm(EPS0,.02,.02,.55,.55,k['bear'],.025)
D['base']=ddm(EPS0,.08,.05,.75,.82,k['base'],.035)
D['bull']=ddm(EPS0,.14,.08,.88,.92,k['bull'],.04)
for s in D: print('DDM',s,round(D[s][0],2),'TV%',round(D[s][1]*100))
R={}
R['bear']=rim(TBV,.125,.115,.02,.02,k['bear'],.025)
R['base']=rim(TBV,.150,.155,.04,.05,k['base'],.032)
R['bull']=rim(TBV,.170,.180,.07,.06,k['bull'],.038)
for s in R: print('RIM',s,round(R[s],2))
J={}
for s,(r,g) in {'bear':(.115,.025),'base':(.1525,.032),'bull':(.18,.038)}.items():
    m=(r-g)/(k[s]-g); J[s]=(m,m*TBV); print('PTBV',s,round(m,3),round(m*TBV,2))
mk=P/TBV; print('P/TBV mkt',round(mk,3),'implied ROTCE',round((mk*(k['base']-.032)+.032)*100,2))
# comps
peers={'JPM':(340.58,112.64,25.57),'WFC':(85.89,44.46,8.01),'C':(123.10,101.59,13.07)}
ptbv=[p/t for p,t,e in peers.values()]; pe=[p/e for p,t,e in peers.values()]
for n,(p,t,e) in peers.items(): print(n,round(p/t,3),round(p/e,2))
a1=sum(ptbv)/3; a2=sum(pe)/3; c1=a1*TBV; c2=a2*5.19; comp=(c1+c2)/2
print('comps',round(a1,3),round(c1,2),round(a2,3),round(c2,2),round(comp,2), 'BAC own',round(P/TBV,2),round(P/5.19,2))
# reversion
hist=[(33.67,24.46),(43.95,26.58),(55.00,28.73)]
mult=[p/t for p,t in hist]; print('rev mults',[round(x,3) for x in mult],[round(x*TBV,2) for x in mult])
rev=sum(mult)/3*TBV; print('rev avg',round(sum(mult)/3,3),round(rev,2))
cons=62.61
W=[.1,.1,.1,.2,.3,.2]; V=[D['base'][0],R['base'],J['base'][1],comp,rev,cons]
blend=sum(w*v for w,v in zip(W,V)); print('BLEND',round(blend,2),'gap %.1f'%(100*(blend/P-1)))
print('simple avg',round(sum(V)/6,2))
ev=.25*(D['bear'][0]+R['bear'])/2+.45*(D['base'][0]+R['base'])/2+.30*(D['bull'][0]+R['bull'])/2; print('EV prob',round(ev,2))
print('cons upside %.1f'%(100*(cons/P-1)))
for v in V: print('  vs mkt %.1f'%(100*(v/P-1)))
# sens grid RIM base
for kk in [.099,.104,.109,.114,.119]:
    print(kk,[round(rim(TBV,.150,.155,.04,.05,kk,g),2) for g in [.022,.027,.032,.037,.042]])
print('TBV yoy',round(100*(29.14/28.16-1),1),'CET1 cushion now $B',round(.009*1821,1),'2027 $B',round(.004*1821,1))

def check_version_anterior():
    print('sep-2026 DDM', [round(ddm(4.34,*a)[0],2) for a in [(.02,.02,.55,.55,.1175,.025),(.08,.05,.75,.82,.1075,.035),(.14,.08,.88,.92,.0975,.04)]])
    print('sep-2026 RIM', [round(rim(29.37,*a),2) for a in [(.125,.115,.03,.02,.1175,.025),(.145,.155,.06,.05,.1075,.032),(.17,.18,.09,.07,.0975,.038)]])
check_version_anterior()
