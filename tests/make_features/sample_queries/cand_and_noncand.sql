REPLACE INTO objects SET objectId="ZTF17aacmaht", ncand=35,
ramean=43.87133624571428,
rastd=0.28187220800988255,
decmean=8.234244477142859,
decstd=0.36960168619792627,
maggmin=16.69219970703125,
maggmax=18.08970069885254,
maggmean=17.43144170443217,
magrmin=16.486919403076172,
magrmax=17.608400344848633,
magrmean=17.193174708973277,
gmag=17.603200912475586,
rmag=16.486919403076172,
dmdt_g= NULL,
dmdt_r= NULL,
dmdt_g_err= NULL,
dmdt_r_err= NULL,
dmdt_g_2= NULL,
dmdt_r_2= NULL,
jdgmax=2459274.6697338,
jdrmax=2459276.6384144,
jdmax=2459276.6384144,
jdmin=2459248.6928704,
g_minus_r=0.6000995635986328,
jd_g_minus_r=2459251.6304398,
glatmean=-43.59877197418795,
glonmean=167.68926463659346,
sgmag1=15.352399826049805,
srmag1=14.780599594116211,
sgscore1=0.975911021232605,
distpsnr1=0.11973714083433151,
ssnamenr= NULL,
ncandgp=8,
ncandgp_7= NULL,
ncandgp_14=4,
htm16=67979700948,
mag_g02=17.44271622779704,
mag_g08=17.491408362836925,
mag_g28=17.524313003657042,
mag_r02=16.57408323107028,
mag_r08=16.967459639113475,
mag_r28=17.20551077520568;

REPLACE INTO sherlock_classifications SET classification='VS',
objectId='ZTF17aacmaht',
association_type='VS',
catalogue_table_name='GSC/GAIA/PS1',
catalogue_object_id='NC3I004594',
catalogue_object_type='star',
raDeg='43.871325050531176',
decDeg='8.23424173666824',
separationArcsec='0.12',
northSeparationArcsec='0.11843481985',
eastSeparationArcsec='0.19577319333',
physical_separation_kpc='0',
direct_distance='0',
distance='0',
z='0',
photoZ='0',
photoZErr='0',
Mag='14.75',
MagFilter='r',
MagErr='0',
classificationReliability='1',
major_axis_arcsec='0',
annotator='https://github.com/thespacedoctor/sherlock/releases/tag/v2.2.0',
additional_output='http://lasair.lsst.ac.uk/api/sherlock/object/ZTF17aacmaht',
description='The transient is synonymous with <em>NC3I004594</em>; a V=15.12 mag stellar source found in the GSC/GAIA/PS1 catalogues. Its located 0.1" from the stellar source core.',
summary='0';

