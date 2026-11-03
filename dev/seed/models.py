"""Simple brightness models for each kind of synthetic transient.

Each model returns the total (source plus host or quiescent star) magnitude at a
time `t` in days from the start of the light curve. The reference magnitude is
what the ZTF template image would show; None means no source in the template.
"""
import math

import numpy as np

FAINT_MAG = 30.0
# SOME SN, NT, CV AND AGN ARE BRIGHT AND STILL ACTIVE NOW, SO THE FRONT PAGE (mag < 17, LAST 7 DAYS) HAS OBJECTS
FEATURED_FRACTION = 0.3
FEATURED_MAG_RANGE = (15.5, 16.5)


def _sn(params, t, fid):
    rise, peak, decline = params['rise'], params['peak'], params['decline']
    colour = 0.0 if fid == 1 else -0.1 + 0.01 * max(t - params['tPeak'], 0)
    dt = t - params['tPeak']
    if dt < -rise:
        return FAINT_MAG
    if dt < 0:
        return peak + 2.5 * (dt / rise) ** 2 * 1.5 + colour
    return peak + decline * dt + colour


def _nuclear(params, t, fid):
    dt = t - params['tPeak']
    colour = -0.2 if fid == 1 else 0.0
    if dt < -params['rise']:
        return FAINT_MAG
    if dt < 0:
        return params['peak'] - 2.5 * math.log10(max(1e-3, 1 + dt / params['rise'])) + colour
    return params['peak'] + 2.5 * math.log10(1 + dt / 30.0) * 1.67 + colour


def _periodic(params, t, fid):
    phase = 2 * math.pi * t / params['period']
    colour = 0.3 if fid == 1 else 0.0
    return params['mean'] - params['amp'] * math.sin(phase + params['phase0']) + colour


def _stochastic(params, t, fid):
    walk = params['walk']
    index = min(int(t), len(walk) - 1)
    colour = 0.1 if fid == 1 else 0.0
    return params['mean'] + walk[index] + colour


def _outburst(params, t, fid):
    dt = t - params['tPeak']
    colour = -0.1 if fid == 1 else 0.0
    if dt < -1 or dt > params['duration']:
        return params['quiescent'] + colour
    return params['quiescent'] - params['amp'] + 0.3 * max(dt, 0) + colour


def _orphan(params, t, fid):
    dt = t - params['tPeak']
    if dt < 0:
        return FAINT_MAG
    return params['peak'] + params['decline'] * dt


def _single(params, t, fid):
    return params['peak'] if abs(t - params['tPeak']) < 0.01 else FAINT_MAG


def build_model(rng, objectType, baseline):
    """Return (modelFunction, params, referenceMag) for one object."""
    isFeatured = objectType in ('SN', 'NT', 'CV', 'AGN') and rng.random() < FEATURED_FRACTION
    if objectType == 'SN':
        params = {'peak': rng.uniform(17.0, 19.3), 'rise': rng.uniform(10, 18),
                  'decline': rng.uniform(0.02, 0.05), 'tPeak': rng.uniform(0.3, 0.7) * baseline}
        if isFeatured:
            params.update(peak=rng.uniform(*FEATURED_MAG_RANGE), tPeak=baseline - rng.uniform(1, 5))
        return _sn, params, None
    if objectType == 'NT':
        params = {'peak': rng.uniform(17.5, 19.0), 'rise': rng.uniform(20, 40),
                  'tPeak': rng.uniform(0.4, 0.8) * baseline}
        if isFeatured:
            params.update(peak=rng.uniform(*FEATURED_MAG_RANGE), tPeak=baseline - rng.uniform(2, 8))
        return _nuclear, params, rng.uniform(18.5, 20.0)
    if objectType == 'AGN':
        walk = np.cumsum(rng.normal(0, 0.05, int(baseline) + 2))
        params = {'mean': rng.uniform(17.5, 19.0), 'walk': walk - walk.mean()}
        if isFeatured:
            params['mean'] = rng.uniform(*FEATURED_MAG_RANGE)
        return _stochastic, params, params['mean'] + 0.2
    if objectType == 'VS':
        params = {'mean': rng.uniform(16.0, 18.5), 'amp': rng.uniform(0.3, 1.0),
                  'period': rng.uniform(0.5, 40.0), 'phase0': rng.uniform(0, 2 * math.pi)}
        return _periodic, params, params['mean']
    if objectType == 'CV':
        params = {'quiescent': rng.uniform(19.5, 20.5), 'amp': rng.uniform(2.5, 4.0),
                  'duration': rng.uniform(5, 15), 'tPeak': rng.uniform(0.4, 0.8) * baseline}
        if isFeatured:
            params.update(amp=params['quiescent'] - rng.uniform(*FEATURED_MAG_RANGE),
                          tPeak=baseline - rng.uniform(3, 5))
        return _outburst, params, params['quiescent']
    if objectType == 'BS':
        params = {'mean': rng.uniform(12.5, 14.5), 'amp': rng.uniform(0.02, 0.1),
                  'period': rng.uniform(1, 10), 'phase0': 0.0}
        return _periodic, params, params['mean']
    if objectType == 'ORPHAN':
        params = {'peak': rng.uniform(18.0, 19.5), 'decline': rng.uniform(0.1, 0.3),
                  'tPeak': rng.uniform(0.6, 0.9) * baseline}
        return _orphan, params, None
    if objectType == 'SS':
        params = {'peak': rng.uniform(18.0, 20.0), 'tPeak': baseline}
        return _single, params, None
    raise ValueError('Unknown object type %s' % objectType)
