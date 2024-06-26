schema = {
    "name": "objects",
    "version": "1.0",
    "fields": [
        {
            "name": "objectId",
            "type": "string",
            "extra": "CHARACTER SET utf8 COLLATE utf8_unicode_ci",
            "doc": "ZTF object identifier"
        },
        {
            "name": "decmean",
            "type": "double",
            "doc": "Mean Dec in degrees"
        },
        {
            "name": "decstd",
            "type": "double",
            "doc": "Standard deviation of Dec in arcseconds"
        },
        {
            "name": "ramean",
            "type": "double",
            "doc": "Mean RA in degrees"
        },
        {
            "name": "rastd",
            "type": "double",
            "doc": "Standard deviation of RA in arcseconds"
        },

        {
            "name": "glatmean",
            "type": "double",
            "doc": "Mean galactic latitude in degrees"
        },
        {
            "name": "glonmean",
            "type": "double",
            "doc": "Mean galactic longitude in degrees"
        },


        {
            "name": "jdgmax",
            "type": "double",
            "doc": "Latest Julian Day of g mag candidates"
        },
        {
            "name": "gmag",
            "type": "float",
            "doc": "Latest g magnitude "
        },
        {
            "name": "dmdt_g",
            "type": "float",
            "doc": "Most recent increase in g magnitude divided by time difference, (brightening = positive). Units are Mags per day, and measurement can have large errors (dmdt_g_err)."
        },
        {
            "name": "dmdt_g_2",
            "type": "float",
            "doc": "Deprecated -- always Null"
        },
        {
            "name": "mag_g02",
            "type": "float",
            "doc": "Latest Exponential Moving Average of difference magnitude in g band, with 2-day timescale (see note)"
        },
        {
            "name": "mag_g08",
            "type": "float",
            "doc": "Latest Exponential Moving Average of difference magnitude in g band, with 8-day timescale (see note)"
        },
        {
            "name": "mag_g28",
            "type": "float",
            "doc": "Latest Exponential Moving Average of difference magnitude in g band, with 28-day timescale (see note)"
        },
        {
            "name": "maggmax",
            "type": "float",
            "doc": "Maximum g magnitude of light curve (faintest)"
        },
        {
            "name": "maggmean",
            "type": "float",
            "doc": "Mean g magnitude of light curve"
        },
        {
            "name": "maggmin",
            "type": "float",
            "doc": "Minimum g magnitude of light curve (brightest)"
        },




        {
            "name": "jdrmax",
            "type": "double",
            "doc": "Latest Julian Day of r mag candidates"
        },
        {
            "name": "mag_r02",
            "type": "float",
            "doc": "Latest Exponential Moving Average of difference magnitude in r band, with 2-day timescale (see note)"
        },
        {
            "name": "mag_r08",
            "type": "float",
            "doc": "Latest Exponential Moving Average of difference magnitude in r band, with 8-day timescale (see note)"
        },
        {
            "name": "mag_r28",
            "type": "float",
            "doc": "Latest Exponential Moving Average of difference magnitude in r band, with 28-day timescale (see note)"
        },
        {
            "name": "rmag",
            "type": "float",
            "doc": "Latest r magnitude"
        },
        {
            "name": "dmdt_r",
            "type": "float",
            "doc": "Most recent increase in r magnitude divided by time difference, (brightening = positive). Units are Mags per day, and measurement can have large errors (dmdt_r_err)."
        },
        {
            "name": "dmdt_r_2",
            "type": "float",
            "doc": "Deprecated -- always Null"
        },
        {
            "name": "magrmax",
            "type": "float",
            "doc": "Maximum r magnitude of light curve (faintest)"
        },
        {
            "name": "magrmean",
            "type": "float",
            "doc": "Mean r magnitude of light curve"
        },
        {
            "name": "magrmin",
            "type": "float",
            "doc": "Minimum r magnitude of light curve (brightest)"
        },



        {
            "name": "jdmax",
            "type": "double",
            "doc": "Maximum of jdgmax and jdrmax"
        },
        {
            "name": "jdmin",
            "type": "double",
            "doc": "Earliest Julian Day of candidates that cite this object"
        },
        {
            "name": "ncand",
            "type": "int",
            "doc": "Number in light curve"
        },
        {
            "name": "ncandgp",
            "type": "int",
            "doc": "Number in light curve with good quality and brighter than reference"
        },
        {
            "name": "distpsnr1",
            "type": "float",
            "doc": "Distance of closest source from PS1 catalog; if exists within 30 arcsec [arcsec]"
        },
        {
            "name": "sgscore1",
            "type": "float",
            "doc": "Star/Galaxy score of closest source from PS1 catalog 0 <= sgscore <= 1 where closer to 1 implies higher likelihood of being a star"
        },
        {
            "name": "sgmag1",
            "type": "float",
            "doc": "g-band PSF magnitude of closest source from PS1 catalog; if exists within 30 arcsec"
        },
        {
            "name": "srmag1",
            "type": "float",
            "doc": "r-band PSF magnitude of closest source from PS1 catalog; if exists within 30 arcsec"
        },
        {
            "name": "htm16",
            "type": "bigint",
            "doc": "Hierarchical Triangular Mesh level 16"
        },
        {
            "name": "g_minus_r",
            "type": "float",
            "doc": "Value of g-r on most recent night when both were available and both positive difference magnitudes"
        },
        {
            "name": "jd_g_minus_r",
            "type": "double",
            "doc": "Julian date of most recent g measure on a night when both ag and r were available and both positive difference magnitudes"
        },
        {
            "name": "ncandgp_7",
            "type": "int",
            "doc": "Number in light curve with good quality and brighter than reference in last 7 days"
        },
        {
            "name": "ncandgp_14",
            "type": "int",
            "doc": "Number in light curve with good quality and brighter than reference in last 14 days"
        },
        {
            "name": "ssnamenr",
            "type": "string",
            "doc": "MPC name of Solar System object"
        },
        {
            "name": "dmdt_g_err",
            "type": "float",
            "doc": "Error estimate for dmdt_g"
        },
        {
            "name": "dmdt_r_err",
            "type": "float",
            "doc": "Error estimate for dmdt_r"
        }
    ],
    "indexes": [
        "PRIMARY KEY (`objectId`)",
        "KEY `htmid16idx` (`htm16`)",
        "KEY `idx_ncand` (`ncand`)",
        "KEY `idx_ramean` (`ramean`)",
        "KEY `idx_decmean` (`decmean`)",
        "KEY `idx_jdmin` (`jdmin`)",
        "KEY `idx_jdgmax` (`jdgmax`)",
        "KEY `idx_jdrmax` (`jdrmax`)",
        "KEY `idx_jdmax` (`jdmax`)",
        "KEY `idx_htm16` (`htm16`)",
        "KEY `idx_sgscore1` (`sgscore1`)",
        "KEY `idx_distpsnr1` (`distpsnr1`)",
        "KEY `idx_ncandgp` (`ncandgp`)"
    ]
}
