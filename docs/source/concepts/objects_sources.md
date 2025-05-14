# Objects and Sources

Lasair deals in *objects* and *sources*. A source is a detection by the telescope of an object.  A source is a collection of pixels on the telescopes light-collection device, which is significantly brighter (five sigma) than it was in the reference imagery, that was taken at the beginning of the survey.  A source is detected with a specific [narrowband optical filter](https://en.wikipedia.org/wiki/Photometric_system):
LSST uses filters u,g,r,i,z,y and ZTF uses g,r. The wavelengths of these are
0.380,     0.500,     0.620,     0.740,     0.880,     1.000 microns, respectively.

When a lot of sources are found in the same place in the sky (i.e. within 1.5 arcsec), 
the collection is called an object.  Thus an object is a star or similar that *does not move* in the sky.  Usually it is assumed that an object corresponds to a real astrophysical object, such as star or something extragalactic.

The brightness of a source in a transient survey is actually a *difference* brightness.
If an object is a variable star, then its optical flux was measured before the survey -- 
a reference flux -- and the source detection is the difference, positive or negative, from this.
When difference brightness is expressed as magnitudes, this 
measurement has two parts: absolute value, converted 
to magnitudes, and a flag to indicate positive or negative difference.
However, if there was nothing detected in the reference sky, then the difference magnitude
is the same as the apparent magnitude.

There are also solar-system objects and solar-system sources. The sources correspond to detections, 
and the objects to asteroids or other moving bodies in our solar system. However, the association 
of sources is more difficult becuase that are in different positions in the sky due to orbital motion.
