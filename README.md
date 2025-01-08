# Beacon v2 Production Implementation

Welcome to Beacon v2 Production Implementation (B2PI). This is an application that makes an instance of Beacon v2 be production ready. To go to the beacon reference implementation (test instance) please visit [B2RI](https://github.com/EGA-archive/beacon2-ri-api). For further information on how to use this app, please visit [B2RI docs](https://b2ri-documentation-demo.ega-archive.org/)

## Main changes from B2RI

* Handlers of the endpoints are classes, not functions
* Unit testing has been developed for the application, starting with 108 unit tests that cover 4000 lines of code approximately (100%)
* Concurrency testing has been applied for this new beacon instance, showing results of responses for more than 3 million genomic variants splitted in different datasets in less than 100 millisecs, for a total of 1000 requests made by 10 users per second at the same time.
* Linking ids to a dataset in a yaml file is not needed anymore
* A couple more indexes for mongoDB have been applied, that, in addition to the restructuration of the code, have improved the quickness of the responses
* Authentication/Authorization is now applied as a decorator, not as a different container
* LOGS now show more relevant information about the different processes (from request to response) including transaction id, the time of execution of each function and the initial call and the return call
* Exceptions now are raised from the lower layer to the top layer, with information and status for the origin of the exception
* Architecture of the code is not dependent on a particular database, meaning that different types of databases (and more than one) can be potentially applied to this instance (although now only MongoDB is the one developed)
* Parameters are sanitized
* Users can manage what entry types want their beacon to show by editing a manage conf file inside source

### TLS configuration

To enable TLS for the Becaon API set `beacon_server_crt` and `beacon_server_key` to the full paht of the server certificate and server key in `beacon/conf/conf.py` file.

#### TLS secured MongoDB

Edit the file `beacon/connections/mongo/conf.py` and set `database_certificate` to the full path to the client certificate. If a private CA is used also set the `database_cafile` to the full path to the CA certificate.

* The MongoDB client certificate should be in the combined PEM format `client.key + "\n" + client.crt`

## Prerequisites

You should have installed:

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Data from [RI TOOLS](https://github.com/EGA-archive/beacon2-ri-tools-v2). Please, bear in mind that the datasetId for your records must match the id for the dataset in the /datasets entry type. 

### Light up the database and the Beacon

#### Up the containers

If you are using a build with all the services in the same cluster, you can use:

```bash
docker compose up -d --build
```

#### Up the containers (with services in independent servers)

If you wish to have each service (or some of them) in different servers, you will need to use the remote version of the docker compose file, and deploy the remote services you need by selecting them individually in the build. Example:

```bash
docker-compose -f docker-compose.remote.yml up -d --build beaconprod
```

After that, you will need to configure the IPs in the different conf files to make them connect. Remember to bind the IP in mongo to 0.0.0.0 in case you are making an independent deployment of the beacon and the mongodb.

#### Load the data

To load the database (mongo) just copy your files in the data folder. Then, locate yourself in the mongo folder:

```bash
cd beacon/connections/mongo
```

And execute the next commands (only the ones you need):

```bash
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/datasets.json --collection datasets
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/individuals.json --collection individuals
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/cohorts.json --collection cohorts
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/analyses.json --collection analyses
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/biosamples.json --collection biosamples
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/genomicVariations.json --collection genomicVariations
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/runs.json --collection runs
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/targets.json --collection targets
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/caseLevelData.json --collection caseLevelData
```

This loads the JSON files inside of the `data` folder into the MongoDB database container. Each time you import data you will have to create indexes for the queries to run smoothly. Please, check the next point about how to Create the indexes.

#### Create the indexes

Remember to do this step every time you import new data!!

You can create the necessary indexes running the following Python script:

```bash
docker exec beaconprod python /beacon/connections/mongo/reindex.py
```

#### Fetch the ontologies and extract the filtering terms

> This step consists of analyzing all the collections of the Mongo database for first extracting the ontology OBO files and then filling the filtering terms endpoint with the information of the data loaded in the database.

You can automatically fetch the ontologies and extract the filtering terms running the following script:

```bash
 docker exec beaconprod python beacon/connections/mongo/extract_filtering_terms.py
```

#### Get descendant and semantic similarity terms

*  If you have the ontologies loaded and the filtering terms extracted* , you can automatically get their descendant and semantic similarity terms by following the next two steps:

1. Add your .obo files inside [ontologies](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/connections/mongo/ontologies) naming them as the ontology prefix in lowercase (e.g. ncit.obo) and rebuild the beacon container with:

2. Run the following script:

```bash
 docker exec beaconprod python beacon/connections/mongo/get_descendants.py
```

#### Check the logs

Check the logs until the beacon is ready to be queried:

```bash
docker compose logs -f beaconprod
```

## Usage

You can query the beacon using GET or POST. Below, you can find some examples of usage:

> For simplicity (and readability), we will be using [HTTPie](https://github.com/httpie/httpie).

### Using GET

Querying this endpoit it should return the 13 variants of the beacon (paginated):

```bash
http GET http://localhost:5050/api/g_variants
```

You can also add [request parameters](https://github.com/ga4gh-beacon/beacon-v2-Models/blob/main/BEACON-V2-Model/genomicVariations/requestParameters.json) to the query, like so:

```bash
http GET http://localhost:5050/api/individuals?filters=NCIT:C16576,NCIT:C42331
```

### Using POST

You can use POST to make the previous query. With a `request.json` file like this one:

```json
{
    "meta": {
        "apiVersion": "2.0"
    },
    "query": {
        "requestParameters": {
    "alternateBases": "G" ,
    "referenceBases": "A" ,
"start": [ 16050074 ],
            "end": [ 16050568 ],
	    "referenceName": "22",
        "assemblyId": "GRCh37"
        },
        "filters": [],
        "includeResultsetResponses": "HIT",
        "pagination": {
            "skip": 0,
            "limit": 10
        },
        "testMode": false,
        "requestedGranularity": "record"
    }
}

```

You can execute:

```bash
curl \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "meta": {
        "apiVersion": "2.0"
    },
    "query": {
        "requestParameters": {
    "alternateBases": "G" ,
    "referenceBases": "A" ,
"start": [ 16050074 ],
            "end": [ 16050568 ],
	    "referenceName": "22",
        "assemblyId": "GRCh37"
        },
        "filters": [],
        "includeResultsetResponses": "HIT",
        "pagination": {
            "skip": 0,
            "limit": 10
        },
        "testMode": false,
        "requestedGranularity": "record"
    }
}' \
  http://localhost:5050/api/g_variants


```

But you can also use complex filters:

```json
{
    "meta": {
        "apiVersion": "2.0"
    },
    "query": {
        "filters": [
            {
                "id": "UBERON:0000178",
                "scope": "biosample",
                "includeDescendantTerms": false
            }
        ],
        "includeResultsetResponses": "HIT",
        "pagination": {
            "skip": 0,
            "limit": 10
        },
        "testMode": false,
        "requestedGranularity": "count"
    }
}
```

You can execute:

```bash
http POST http://localhost:5050/api/biosamples --json < request.json
```

And it will use the ontology filter to filter the results.

## Allowing authentication/authorization

Go to [auth folder](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/auth/idp_providers) and create an .env file with the next Oauthv2 OIDC Identity Provider Relying Party known information:
```bash
CLIENT_ID='your_idp_client_id'
CLIENT_SECRET='your_idp_client_secret'
USER_INFO='https://login.elixir-czech.org/oidc/userinfo'
INTROSPECTION='https://login.elixir-czech.org/oidc/introspect'
ISSUER='https://login.elixir-czech.org/oidc/'
JWKS_URL='https://login.elixir-czech.org/oidc/jwk'
```

For Keycloak IDP, an "aud" parameter will need to be added to the token's mappers, matching the Audience for the Keycloak realm.

## Making a dataset public/registered/controlled

In order to assign the security level for a dataset in your beacon, please go to [permissions/datasets](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/permissions/datasets) and add your dataset into the .yml corresponding file you wish to assign the permissions for it.

## Managing configuration

You can edit some parameters for your Beacon v2 API that are in [conf.py](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/conf/conf.py). For that, edit the variables you see fit, save the file and restart the API by executing the next command:

```bash
docker compose restart beaconprod
```

## Managing source

You can edit some parameters concerning entry types developed for your Beacon in [manage.py](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/source/manage.py). For that, change to True the entry types you want to have developed and shown with data for your beacon and execute the next command:

```bash
docker compose restart beaconprod
```

## Tests report

![Beacon prod concurrency test](https://github.com/EGA-archive/beacon-production-prototype/blob/main/ri-tools/files/concurrencytest.png)


