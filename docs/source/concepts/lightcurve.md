# Lightcurve

A lightcurve is a record of the brightness of an astrophysical object with time, so it is a collection of 
(time, brightness) pairs. For LSST the brightness is measured as flux in nanoJanskies (nJ), and for ZTF it
is measured with the traditional magnitude system. Note that the values in the lightcurve are *difference*
fluxes, as defined in [Objects and Sources](objects_sources.html).

Since each source brightness is measured for a specific optical filter, there may be 
several lightcurves for a given object, for example the g-lightcurve and r-lightcurve will
be derived from the detections in the g filter and r filter respectively.

It is only when an object is more than 5 sigma over the reference imagery that a transient alert is sent out, 
this is the "unforced" photometry plotted in the object pages. Other brightness measurements are also computed 
from the imagery, the "forced" photometry at the location of the transient. In each case, what is measured is 
a "difference" brightness from the reference image, which can be positive or negative.
More information about forced photometry and ZTF can be found <a href=https://arxiv.org/abs/2305.16279>here</a>.

The nature of the lightcurve informs us of the underlying astrophysics. Variable stars can be characterised
by the shape of their lightcurves, and explosive transients such as supernovae can be distinguished by the 
rise and fall rates of their lightcurves.
