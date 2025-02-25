schema = {
    "name": "annotations",
    "version": "1.0",
    "fields": [
        {
            "name": "annotationID",
            "type": "int",
            "extra": "NOT NULL AUTO_INCREMENT",
            "doc": "Auto increment counter"
        },
        {
            "name": "objectId",
            "type": "string",
            "extra": "NOT NULL",
            "doc": "ObjectId of the object that this annotator applies to"
        },
        {
            "name": "topic",
            "type": "string",
            "doc": "The topic name of the annotator -- acts as primary key"
        },
        {
            "name": "version",
            "type": "string",
            "default": "0.1",
            "doc": "Version information for the annotator software"
        },
        {
            "name": "timestamp",
            "type": "timestamp",
            "extra": "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "doc": "Time at which this annotation was added to the database"
        },
        {
            "name": "classification",
            "type": "string",
            "extra": "NOT NULL",
            "doc": "Short, non-trivial string expressing the classification of this object by this annotator"
        },
        {
            "name": "explanation",
            "type": "text",
            "doc": "Natural language explanation of the classification"
        },
        {
            "name": "classdict",
            "type": "JSON",
            "doc": "Machine readable information about the classification"
        },
        {
            "name": "url",
            "type": "text",
            "default": "NULL",
            "doc": "URL for further information about this annotation of this object"
        }
    ],
    "indexes": [
        "PRIMARY KEY    (annotationID)",
        "UNIQUE KEY     one_per_object (objectId, topic)"
    ]
}
