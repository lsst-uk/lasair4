schema = {
  "name": "watchlist_hits",
  "version": "1.0",
  "fields": [
    {
      "name": "objectId",
      "type": "string",
      "extra": "CHARACTER SET utf8 COLLATE utf8_unicode_ci",
      "doc": "ZTF object identifier"
    },
    {
      "name": "wl_id",
      "type": "int",
      "doc": "Watchlist identifier in watchlists"
    },
    {
      "name": "cone_id",
      "type": "long",
      "doc": "Cone identifier in watchlist_cones"
    },
    {
      "name": "arcsec",
      "type": "float",
      "doc": "Distance between ZTF and watchlist source (arcsec)"
    },
    {
      "name": "name",
      "type": "bigstring",
      "doc": "Name of cone given by user"
    }
  ],
  "indexes": [
    "PRIMARY KEY (`objectId`, `cone_id`)"
  ]
}
