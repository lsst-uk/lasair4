REPLACE INTO objects SET objectId="ZTF18acvrfbh", ncand=1,
ramean=39.9364408,
rastd= NULL,
decmean=44.7023597,
decstd= NULL,
maggmin= NULL,
maggmax= NULL,
maggmean= NULL,
magrmin=19.086685180664062,
magrmax=19.086685180664062,
magrmean=19.086685180664062,
gmag= NULL,
rmag=19.086685180664062,
dmdt_g= NULL,
dmdt_r= NULL,
dmdt_g_err= NULL,
dmdt_r_err= NULL,
dmdt_g_2= NULL,
dmdt_r_2= NULL,
jdgmax= NULL,
jdrmax=2459276.645,
jdmax=2459276.645,
jdmin=2459276.645,
g_minus_r= NULL,
jd_g_minus_r= NULL,
glatmean=-14.033803133753896,
glonmean=142.41248387421447,
sgmag1=18.14620018005371,
srmag1=17.666400909423828,
sgscore1=1.0,
distpsnr1=0.07612515985965729,
ssnamenr= NULL,
ncandgp= NULL,
ncandgp_7= NULL,
ncandgp_14= NULL,
htm16=68546208391,
mag_g02= NULL,
mag_g08= NULL,
mag_g28= NULL,
mag_r02=19.086685180664062,
mag_r08=19.086685180664062,
mag_r28=19.086685180664062;

REPLACE INTO sherlock_classifications SET classification='VS',
objectId='ZTF18acvrfbh',
association_type='VS',
catalogue_table_name='SDSS/PS1',
catalogue_object_id='1237661082658931642',
catalogue_object_type='star',
raDeg='39.936443576040006',
decDeg='44.70238004023648',
separationArcsec='0.07',
northSeparationArcsec='0.09322',
eastSeparationArcsec='-0.03465',
physical_separation_kpc='0',
direct_distance='0',
distance='0',
z='0',
photoZ='0',
photoZErr='0',
Mag='17.6',
MagFilter='r',
MagErr='0',
classificationReliability='1',
major_axis_arcsec='5.42',
annotator='https://github.com/thespacedoctor/sherlock/releases/tag/v2.2.0',
additional_output='http://lasair.lsst.ac.uk/api/sherlock/object/ZTF18acvrfbh',
description='The transient is synonymous with <em><a href="http://skyserver.sdss.org/dr12/en/tools/explore/Summary.aspx?id=1237661082658931642">SDSS J023944.74+444208.5</a></em>; an r=17.60 mag stellar source found in the SDSS/PS1 catalogues. Its located 0.1" from the stellar source core.',
summary='0';

