"""Synthetic 63x63 pixel ZTF-style cutout images.

The Template shows the static scene (host galaxy or star plus field stars), the
Science image adds the transient, and the Difference image is the transient on
its own. Files are written with the production `objectStore`, so the webserver's
`/fits/<imjd>/<candid>_cutout<Type>/` route finds them.
"""
import io

import numpy as np
from astropy.io import fits

CUTOUT_SIZE = 63
CUTOUT_TYPES = ('Science', 'Template', 'Difference')
PSF_SIGMA_PIX = 1.8
HOST_SIGMA_PIX = 5.0
SKY_LEVEL = 150.0
SKY_NOISE = 6.0
N_FIELD_STARS = 4


def _gaussian(size, x0, y0, sigma, amplitude):
    y, x = np.mgrid[0:size, 0:size]
    return amplitude * np.exp(-((x - x0) ** 2 + (y - y0) ** 2) / (2 * sigma ** 2))


def _scene(rng):
    centre = CUTOUT_SIZE // 2
    image = _gaussian(CUTOUT_SIZE, centre + rng.uniform(-3, 3), centre + rng.uniform(-3, 3),
                      HOST_SIGMA_PIX, rng.uniform(20, 120))
    for _ in range(N_FIELD_STARS):
        x, y = rng.uniform(3, CUTOUT_SIZE - 3, 2)
        image += _gaussian(CUTOUT_SIZE, x, y, PSF_SIGMA_PIX, rng.uniform(50, 800))
    return image


def make_cutout(seed, cutoutType, isDetection=True, negative=False):
    """Return FITS bytes for one cutout. The same seed gives the same scene."""
    sceneRng = np.random.default_rng(seed)
    noiseRng = np.random.default_rng([seed, CUTOUT_TYPES.index(cutoutType)])
    centre = CUTOUT_SIZE // 2
    transient = _gaussian(CUTOUT_SIZE, centre, centre, PSF_SIGMA_PIX, 400.0 if isDetection else 0.0)
    if negative:
        transient = -transient
    if cutoutType == 'Difference':
        data = transient + noiseRng.normal(0, SKY_NOISE, (CUTOUT_SIZE, CUTOUT_SIZE))
    else:
        data = SKY_LEVEL + _scene(sceneRng) + noiseRng.normal(0, SKY_NOISE, (CUTOUT_SIZE, CUTOUT_SIZE))
        if cutoutType == 'Science':
            data = data + transient
    buffer = io.BytesIO()
    fits.PrimaryHDU(data.astype(np.float32)).writeto(buffer)
    return buffer.getvalue()


def write_cutouts(store, candid, imjd, seed, negative=False):
    """Write the three cutouts for one detection. Return the file paths."""
    paths = []
    for cutoutType in CUTOUT_TYPES:
        name = '%d_cutout%s' % (candid, cutoutType)
        store.putObject(name, imjd, make_cutout(seed, cutoutType, True, negative))
        paths.append(store.getFileName(name, imjd))
    return paths
