schema = {
    "name": "crossmatch_tns",
    "version": "1.0",
    "fields": [
        {
            "name": "ra",
            "type": "double",
            "doc": "Right Ascension in decimal degrees"
        },
        {
            "name": "decl",
            "type": "double",
            "doc": "Declination in decimal degrees"
        },
        {
            "name": "tns_name",
            "type": "string",
            "doc": "TNS name, for example 2021iru"
        },
        {
            "name": "tns_prefix",
            "type": "string",
            "doc": "For example SN or AT"
        },
        {
            "name": "disc_mag",
            "type": "float",
            "doc": "Discovery magnitude"
        },
        {
            "name": "disc_mag_filter",
            "type": "string",
            "doc": "Discovery magnitude filter"
        },
        {
            "name": "type",
            "type": "bigstring",
            "doc": "Astrophysical type of supernova, eg SN Ia"
        },
        {
            "name": "z",
            "type": "float",
            "doc": "Redshift"
        },
        {
            "name": "hostz",
            "type": "float",
            "doc": "Redshift of host galaxy",
            "default": "NULL"
        },
        {
            "name": "host_name",
            "type": "bigstring",
            "doc": "Name of host galaxy",
            "default": "NULL"
        },
        {
            "name": "ext_catalogs",
            "type": "bigstring",
            "doc": "External catalogues used",
            "default": "NULL"
        },
        {
            "name": "disc_int_name",
            "type": "bigstring",
            "doc": "Discoverers internal name"
        },
        {
            "name": "disc_date",
            "type": "date",
            "doc": "Discovery date"
        },
        {
            "name": "lastmodified_date",
            "type": "date",
            "doc": "Last Modified date"
        },
        {
            "name": "sender",
            "type": "string",
            "doc": "Discoverers internal name"
        },
        {
            "name": "reporters",
            "type": "bigstring",
            "doc": "Discoverers internal name"
        },
        {
            "name": "source_group",
            "type": "string",
            "doc": "Discoverers internal name"
        },
        {
            "name": "htm16",
            "type": "bigint",
            "doc": "Hierarchical Triangular Mesh level 16"
        },
        {
            "name": "lasairmodified_date",
            "type": "timestamp",
            "extra": "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "doc": "Lasair last Modified date"
        }
    ],
    "indexes": [
        "id int(10) unsigned NOT NULL AUTO_INCREMENT",
        "PRIMARY KEY (`id`)",
        "KEY `idx_htm16` (`htm16`)",
        "KEY tns_name_idx (tns_name)"
    ]
}
