"""Cached, forward-IF97 saturation samples shared by all diagram projections."""
from functools import lru_cache
from threading import Lock
from math import cos, pi, isfinite
from iapws import IAPWS97
from .thermo import TC, PC

_LOCK = Lock()

def saturation_data() -> dict:
    with _LOCK:
        return _saturation_data()

@lru_cache(maxsize=1)
def _saturation_data() -> dict:
    # Stay above the triple point and explicitly below the critical singularity.
    minimum, maximum = 273.16, TC - 0.05
    rows = []
    for i in range(161):
        t = minimum + (maximum-minimum)*(1-cos(pi*i/160))/2
        liquid, vapor = IAPWS97(T=t,x=0), IAPWS97(T=t,x=1)
        row = {'T': t-273.15, 'P': liquid.P*1000,
               'sf': liquid.s, 'sg': vapor.s, 'vf': liquid.v,
               'vg': vapor.v, 'hf': liquid.h, 'hg': vapor.h}
        if not all(isfinite(v) for v in row.values()) or row['P']<=0 or not 0<row['vf']<row['vg'] or row['sf']>=row['sg'] or row['hf']>=row['hg']:
            raise ValueError('Invalid IF97 saturation sample; curve not published')
        rows.append(row)
    return {'method':'IAPWS-IF97', 'points':rows,
            'units':{'T':'°C','P':'kPa','s':'kJ/(kg·K)','v':'m³/kg','h':'kJ/kg'},
            'critical':{'T':TC-273.15,'P':PC*1000,'included':False},
            'domain':{'minimum_T_c':minimum-273.15,'maximum_T_c':maximum-273.15,'critical_gap_K':0.05},
            'warnings':['Exact critical point and the final 0.05 K interval are excluded; no fabricated apex is joined.',
                        'Straight segments connect computed samples for display; they are not a property solver.',
                        'Only stable liquid–vapor saturation boundaries are plotted. Ice, metastable states and full IF97 validity envelopes are not plotted.']}
