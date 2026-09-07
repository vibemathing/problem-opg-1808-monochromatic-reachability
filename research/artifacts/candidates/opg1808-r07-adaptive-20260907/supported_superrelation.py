"""Optional candidate strengthening, complete for actual reachability models.
Every positive R needs an outgoing/incoming incident arc, or (mode ends) a
first and last physical arc supported by R. This is NOT a least-fixpoint claim.
"""
from superrelation import build as base_build

def build(n,palette=3,rainbow=True,positive=True,mode='ends'):
 if mode not in ('incidence','ends'):raise ValueError('mode')
 text=base_build(n,palette,rainbow,positive);lines=[]
 def e(u,v,c):return f'e{c}_{u}_{v}'
 def r(u,v,c):return f'r{c}_{u}_{v}'
 for c in range(palette):
  for u in range(n):
   for v in range(n):
    if u==v:continue
    if mode=='incidence':
     first=[e(u,z,c) for z in range(n) if z!=u];last=[e(z,v,c) for z in range(n) if z!=v]
    else:
     first=[e(u,v,c)]+[f'(and {e(u,z,c)} {r(z,v,c)})' for z in range(n) if z not in (u,v)]
     last=[e(u,v,c)]+[f'(and {r(u,z,c)} {e(z,v,c)})' for z in range(n) if z not in (u,v)]
    for rhs in (first,last):lines.append('(assert (=> '+r(u,v,c)+' (or '+' '.join(rhs)+')))')
 return text+'\n'.join(lines)+'\n'
