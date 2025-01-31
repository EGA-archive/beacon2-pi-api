# OMOP CDM implementation

## Add your PostgreSQL database information

Modify the `conf.py` file with your database information:

```
database_user = 'pgadmin'
database_password = 'admin'
database_host = 'host.docker.internal' #'host.docker.internal' or localhost
database_port = 5432
database_name = 'synthetic_data_w_measurements'
```

## Add the backend information for each schema

Go to [../../source/manage.py](../../source/manage.py) and change the `database` property to `mongo` or `omopcdm`. Depending on where you are doing the queries.

## Add you dataset permissions

Go to [../../permissions/datasets/](../../permissions/datasets/) and add your dataset id in one of the `.yml` files, depending on the access of your users.

## Deploy the tool

```
docker compose up -d --build
```

## Create the database model and connect Ids

Modify the [../mongo/data/datasets.json](../mongo/data/datasets.json) adding the information of your dataset (only the `id` is mandatory).

- Example:

```
[
    {
        "createDateTime": "",
        "dataUseConditions": {
            "duoDataUse": [
                {
                    "id": "",
                    "label": "",
                    "version": ""
                }
            ]
        },
        "description": "",
        "externalUrl": "",
        "id": "omop_cdm",
        "info": {
            "beacon": {
                "contact": "",
                "mapping": "",
                "version": "v2.0"
            },
            "dataset": {
                "derived": [
                    {
                        "ContactPerson": {
                            "contact": "example@example.com",
                            "externalUrl": "",
                            "license": {
                                "$ref": "#/dataUseConditions/duoDataUse"
                            }
                        }
                    }
                ],
                "origin": [
                    {
                        "referenceInfo": {
                            "contact": "example@example.com",
                            "externalUrl": "",
                            "license": "",
                            "managers": ""
                        }
                    }
                ]
            }
        },
        "name": "OMOP CDM dataset example",
        "updateDateTime": "",
        "version": "v1.0"
    }
]
```

Then, create or modify a file called `datasetsToId.json` at [../mongo/data/](../mongo/data/) folder. Add the ids belonging to your dataset at `individualId` and `biosampleId` list with the id of your individuals and and biosamples, respectively. 

- Example:

```
[
    { 
        "datasetId": "omop_cdm",
        "individualId": [
            "1",
            "2",
            "3",
            "4"
        ],
        "biosampleId": [
            "10091",
            "10263",
            "10702",
            "10888"
        ]
    }
]
```

Add the `datasets.json` and datasetsToId to the mongo database:

```
cd beacon/connections/mongo

docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/datasets.json --collection datasets
docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/datasetsToId.json --collection datasetsToId
```

