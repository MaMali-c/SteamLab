"""Phase-separated IF97 inversion; see SCIENCE.md for completeness limits."""
from math import isfinite
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from iapws import IAPWS97
from iapws.iapws97 import _PSat_T, _TSat_P
from .thermo import StateError, TC, PC, PMIN, calculate_tp

PAIRS = ('T_P','T_x','P_x','T_s','T_u','T_h','T_v','P_s','P_u','P_h','P_v')
ATOL = {'T': 2e-6, 'P': 2e-5, 'h': 2e-5, 'u': 2e-5, 's': 2e-8, 'v': 2e-10, 'x': 2e-8}
RTOL = 2e-7


def properties(state: IAPWS97) -> dict[str, float]:
    return dict(T=float(state.T-273.15), P=float(state.P*1000),
                h=float(state.h), u=float(state.u), s=float(state.s), v=float(state.v))


def tolerance(key: str, value: float) -> float:
    return ATOL[key] + RTOL * abs(value)


def solve(pair: str, values: dict[str, float]) -> dict:
    if pair not in PAIRS or set(values) != set(pair.split('_')):
        raise StateError('invalid_inputs', 'Supply exactly the two properties named by input_pair.')
    if any(isinstance(v, bool) or not isfinite(v) for v in values.values()):
        raise StateError('invalid_number', 'All inputs must be finite real numbers.')
    anchor, target = pair.split('_')
    if 'T' in values and not 0 <= values['T'] <= 2000:
        raise StateError('out_of_range', 'Temperature must be between 0 and 2000 °C.')
    if 'P' in values and not PMIN*1000 <= values['P'] <= 100000:
        raise StateError('out_of_range', 'Pressure is outside the supported IF97 domain.')
    if 'v' in values and values['v'] <= 0:
        raise StateError('out_of_range', 'Specific volume must be positive.')
    if 'x' in values and not 0 <= values['x'] <= 1:
        raise StateError('invalid_quality', 'Quality must be between zero and one.')
    t = values.get('T', 0) + 273.15
    p = values.get('P', 0) / 1000
    candidates: list[tuple[IAPWS97, float | None, str]] = []
    evaluations = 0
    failures = 0
    warnings: list[str] = []

    def add(state: IAPWS97, quality: float | None, method: str) -> None:
        actual = properties(state)
        if not all(isfinite(v) for v in actual.values()):
            return
        if abs(state.T-TC) < 1e-6 and abs(state.P-PC) < 1e-7:
            return
        for key, value in values.items():
            got = quality if key == 'x' else actual[key]
            if got is None or abs(got-value) > tolerance(key, value):
                return
        for previous, _, _ in candidates:
            if abs(previous.T-state.T) < 1e-5 and abs(previous.P-state.P) < 1e-7 and abs(previous.v-state.v) < tolerance('v', state.v):
                return
        candidates.append((state, quality, method))

    if pair == 'T_P':
        calculate_tp(values['T'], values['P'])  # retain saturation and domain guards
        add(IAPWS97(T=t, P=p), None, 'native IF97 T,P')
    elif target == 'x':
        if (anchor == 'T' and not 273.15 <= t < TC) or (anchor == 'P' and not PMIN <= p < PC):
            raise StateError('quality_domain', 'Quality requires subcritical liquid–vapor saturation conditions; the critical point is excluded.')
        add(IAPWS97(**{anchor: t if anchor == 'T' else p, 'x': values['x']}), values['x'], 'native IF97 saturation')
    else:
        # Include the entire two-phase segment algebraically, separately from
        # continuous single-phase branches. Never bracket across latent jumps.
        saturation = None
        if anchor == 'T' and t < TC:
            saturation = _PSat_T(t)
        elif anchor == 'P' and p < PC:
            saturation = _TSat_P(p)
        if saturation is not None:
            kwargs = {anchor: t if anchor == 'T' else p}
            liquid, vapor = IAPWS97(**kwargs, x=0), IAPWS97(**kwargs, x=1)
            lo, hi = getattr(liquid, target), getattr(vapor, target)
            if hi != lo and min(lo, hi) <= values[target] <= max(lo, hi):
                quality = (values[target]-lo)/(hi-lo)
                add(IAPWS97(**kwargs, x=quality), quality, 'IF97 saturation mixture balance')
        if anchor == 'P' and target in ('h','s'):
            try:
                native = IAPWS97(P=p, **{target: values[target]})
                add(native, native.x if native.region == 4 else None, 'native IF97 backward P,'+target)
            except (ValueError, NotImplementedError, RuntimeError, OverflowError):
                pass  # bounded forward inversion below remains available
        # Pressure is searched logarithmically; temperature in kelvin.
        if anchor == 'T':
            low, high = np.log(PMIN), np.log(50 if t > 1073.15 else 100)
            cuts = [low, high]
            if saturation is not None:
                cuts.append(float(np.log(saturation)))
            if 623.15 < t <= 863.15:
                boundary = 348.05185628969 - 1.1671859879975*t + .0010192970039326*t*t
                if PMIN < boundary < 100:
                    cuts.append(float(np.log(boundary)))
            def state_at(z: float) -> IAPWS97:
                return IAPWS97(T=t, P=min(50.0 if t > 1073.15 else 100.0, max(PMIN, float(np.exp(z)))))
        else:
            low, high = 273.15, 2273.15 if p <= 50 else 1073.15
            cuts = [low, high, 623.15, 1073.15]
            if saturation is not None:
                cuts.append(saturation)
            if p > 16.5291642526:
                cuts.append(572.54459862746 + ((p-13.91883977887)/.0010192970039326)**.5)
            def state_at(z: float) -> IAPWS97:
                return IAPWS97(T=z, P=p)
        cuts = sorted(set(float(c) for c in cuts if low <= c <= high))
        def residual(z: float) -> float:
            nonlocal evaluations, failures
            evaluations += 1
            try:
                value = float(getattr(state_at(z), target))-values[target]
                if not isfinite(value):
                    raise ValueError('Nonfinite state')
                return value
            except (ValueError, NotImplementedError, RuntimeError, OverflowError):
                failures += 1
                return float('nan')
        for left, right in zip(cuts, cuts[1:]):
            # Offset internal boundaries to avoid evaluating the wrong branch.
            a = left if left == low else np.nextafter(left, right)
            b = right if right == high else np.nextafter(right, left)
            grid = np.linspace(a, b, 257)
            ys = [residual(float(z)) for z in grid]
            roots = []
            for i in range(len(grid)-1):
                za, zb, ya, yb = grid[i], grid[i+1], ys[i], ys[i+1]
                if not (isfinite(ya) and isfinite(yb)):
                    continue
                if ya == 0:
                    roots.append(float(za))
                if ya*yb < 0:
                    try:
                        roots.append(brentq(residual, za, zb, xtol=1e-11, rtol=1e-12, maxiter=150))
                    except (ValueError, RuntimeError):
                        failures += 1
            if isfinite(ys[-1]) and ys[-1] == 0:
                roots.append(float(grid[-1]))
            # Refine stationary points: resolves tangencies and close root pairs
            # that a sign-change-only scan would miss at property extrema.
            for i in range(1, len(grid)-1):
                before, middle, after = ys[i-1:i+2]
                if not all(isfinite(v) for v in (before, middle, after)):
                    continue
                if (middle-before)*(after-middle) < 0:
                    sign = 1 if middle < before else -1
                    extremum = minimize_scalar(lambda z: sign*residual(z), bounds=(grid[i-1], grid[i+1]), method='bounded', options={'xatol':1e-11, 'maxiter':150})
                    if not extremum.success:
                        failures += 1
                    if extremum.success:
                        z, y = float(extremum.x), residual(float(extremum.x))
                        if abs(y) <= tolerance(target, values[target]):
                            roots.append(z)
                        for end in (grid[i-1], grid[i+1]):
                            if isfinite(y) and y*residual(float(end)) < 0:
                                roots.append(brentq(residual, min(z,end), max(z,end), xtol=1e-11, rtol=1e-12, maxiter=150))
            for root in roots:
                try:
                    candidate = state_at(root)
                    if saturation is not None:
                        coord = candidate.P if anchor == 'T' else candidate.T
                        if abs(coord-saturation) < (1e-9 if anchor == 'T' else 1e-7):
                            continue
                    add(candidate, None, 'phase-separated bounded forward IF97 inversion')
                except (ValueError, NotImplementedError, RuntimeError, OverflowError):
                    failures += 1
        warnings.append('Inverse search uses finite sampling plus stationary-point refinement; global root completeness is not mathematically certified, especially near critical points and narrow extrema.')
    if failures:
        raise StateError('search_incomplete', f'{failures} numerical evaluations failed; uniqueness cannot be established. No solution was selected.')
    if not candidates:
        raise StateError('no_verified_state', 'No supported state satisfies both inputs within documented residual tolerances.')
    if len(candidates) > 1:
        error = StateError('ambiguous_state', f'{len(candidates)} distinct states satisfy the inputs; supply an additional physical constraint.')
        error.candidates = [properties(s) | {'quality': q, 'region': s.region} for s,q,_ in candidates]
        raise error
    state, quality, method = candidates[0]
    full = properties(state)
    phase = ('Saturated liquid' if quality == 0 else 'Saturated vapor' if quality == 1 else 'Liquid–vapor mixture') if quality is not None else ('Supercritical fluid' if state.T >= TC and state.P >= PC else 'Gas' if state.T >= TC else 'Compressed liquid' if state.P > _PSat_T(state.T) else 'Superheated vapor')
    saturation_info = {}
    if state.T < TC:
        saturation_info['pressure_at_T_kpa'] = _PSat_T(state.T)*1000
    if PMIN <= state.P < PC:
        saturation_info['temperature_at_P_c'] = _TSat_P(state.P)-273.15
    residuals = {k: (quality if k == 'x' else full[k])-v for k,v in values.items()}
    output_keys = [k for k in ('h','u','s','v','T','P') if k not in values][:4]
    if 'x' in values:
        warnings.append('Quality pairs leave five of T/P/h/u/s/v unknown. Four property cards are h,u,s,v; the dependent saturation coordinate is included in full_state and saturation.')
    return dict(input_pair=pair, normalized_inputs=values, calculated_properties={k:full[k] for k in output_keys}, full_state=full, region=int(state.region), phase=phase, quality=quality, saturation=saturation_info, solver_method=method, convergence=dict(converged=True,residuals=residuals,tolerances={k:tolerance(k,v) for k,v in values.items()}, evaluations=evaluations, verified_candidates=len(candidates), uniqueness_certified=not evaluations), scientific_warnings=warnings)
