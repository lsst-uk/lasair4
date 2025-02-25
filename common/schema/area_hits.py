schema = {
  "name": "area_hits",
  "version": "1.0",
  "fields": [
    {
      "name": "objectId",
      "type": "string",
      "extra": "CHARACTER SET utf8 COLLATE utf8_unicode_ci",
      "doc": "ZTF object identifier"
    },

    {
      "name": "ar_id",
      "type": "int",
      "doc": "Area identifier"
    }
  ],
  "indexes": [
    "PRIMARY KEY (`objectId`, `ar_id`)"
  ]
}
