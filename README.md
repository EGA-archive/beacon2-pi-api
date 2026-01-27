# Beacon v2 Production Implementation

Welcome to Beacon v2 Production Implementation (B2PI). This is an application that makes an instance of Beacon v2 be production ready.

## Documentation

Please, go to [B2RI/B2PI docs website](https://b2ri-documentation-demo.ega-archive.org/) to know how to use Beacon v2 Production Implementation.

## New release beacon v2.0-d4012a4 features added

* Models plug in. Beacon PI now accepts different beacon flavours, based on different model specifications. Kicking off with two models: ga4gh beacon v2 default model and EUCAIM.
* Conf now is not affected by further releases. Use your conf and keep it forever.
* Cross queries between collections and non collections now are ready to be performed at full power.
* Schema request now working: feel free to request any schema you'd like for beacon to return.
* Validation on the fly per framework and model(s).
* Configuration of the entities of each entry type now done by .yml files.
* Restart of the app when conf files or generic conf is modified (no need to rebuild).
* OR Filters (in test approach, as it is still not approved officially by GA4GH).
* Other bug fixes.
* Unit tests expanded, with a total of 313 now.

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
* Admin-ui to manage all the configuration settings from a UI is in development.

### TLS configuration

To enable TLS for the Becaon API set `beacon_server_crt` and `beacon_server_key` to the full paht of the server certificate and server key in `beacon/conf/conf.py` file.

#### TLS secured MongoDB

Edit the file `beacon/connections/mongo/conf.py` and set `database_certificate` to the full path to the client certificate. If a private CA is used also set the `database_cafile` to the full path to the CA certificate.

* The MongoDB client certificate should be in the combined PEM format `client.key + "\n" + client.crt`

For more information and have a testing on TLS, please go to [mongoDB official documentation website](https://www.mongodb.com/docs/v7.1/appendix/security/appendixA-openssl-ca/).

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

Note: If you have an Apple Silicon Mac and use [Colima](https://github.com/abiosoft/colima) as your container runtime, you may have to change the default Colima settings for the Mongo docker container to start correctly.
See [Fredrik Mørstad](https://stackoverflow.com/users/11494958/fredrik-m%c3%b8rstad)'s answer to [this stackoverflow post](https://stackoverflow.com/questions/67498836/docker-chown-changing-ownership-of-data-db-operation-not-permitted) for guidance on how to resolve this issue.

Alternatively. if you are updating the BeaconPI instance from a previous version, it is recommended to use the next commands:

```bash
docker stop beaconprod
docker compose build --no-cache beaconprod
docker compose up -d --force-recreate beaconprodx
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

Alternatively, now also you can have your json gzipped and insert them in a one step injection with the next commands:

```
gunzip --stdout genomicVariations.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations'
gunzip --stdout analyses.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection analyses'
gunzip --stdout biosamples.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection biosamples'
gunzip --stdout datasets.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection datasets'
gunzip --stdout cohorts.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection cohorts'
gunzip --stdout runs.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection runs'
gunzip --stdout individuals.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection individuals'
gunzip --stdout targets.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection targets'
gunzip --stdout caseLevelData.json.gz | docker exec -i mongoprod sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection caseLevelData'
```

This loads the JSON files inside of the `data` folder into the MongoDB database container. Each time you import data you will have to create indexes for the queries to run smoothly. Please, check the next point about how to Create the indexes.

#### Create the indexes

Remember to do this step every time you import new data!!

You can create the necessary indexes running the following Python script:

```bash
docker exec beaconprod python -m beacon.connections.mongo.reindex
```

#### Fetch the ontologies and extract the filtering terms

> This step consists of analyzing all the collections of the Mongo database for first extracting the ontology OBO files and then filling the filtering terms endpoint with the information of the data loaded in the database.

You can automatically fetch the ontologies and extract the filtering terms running the following script:

```bash
docker exec beaconprod python -m beacon.connections.mongo.extract_filtering_terms
```

#### Get descendant and semantic similarity terms

*  If you have the ontologies loaded and the filtering terms extracted* , you can automatically get their descendant and semantic similarity terms by following the next two steps:

1. Add your .obo files inside [ontologies](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/connections/mongo/ontologies) naming them as the ontology prefix in lowercase (e.g. ncit.obo) and rebuild the beacon container with:

2. Run the following script:

```bash
docker exec beaconprod python -m beacon.connections.mongo.get_descendants
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

## Dataset configuration

To state if a dataset is test or not or if is synthetic or not, you have to modify the [datasets_conf.yml](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/conf/datasets/datasets_conf.yml), writing the name of the dataset you want to declare and the two possible variables **isTest** and **isSynthetic** with a boolean value.

## Making a dataset public/registered/controlled

In order to assign the security level for a dataset in your beacon, please go to [datasets_permissions.yml](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/permissions/datasets/datasets_permissions.yml) and add your dataset you wish to assign the permissions for it. The 3 possible options to allow for the dataset are public, registered or controlled, which needs to be in the first item under the dataset name. Public means that authentication is not required, registered means authentication required and controlled means authentication required and with specific permissions for the authenticated user. After that, depending on the security level you assigned to the dataset, you can set a **default_entry_types_granularity**, which will set which is the maximum granularity allowed for this dataset, except for the **entry_types_exceptions**, that can assign a particular granularity for a particular entry type. Beware that the entry type needs to match the entry type id you set for each of the entry type files in their respective conf file: id of analysis, individual, etc. 
```
CINECA_synthetic_cohort_EUROPE_UK1:
  public:
    default_entry_types_granularity: record
    entry_types_exceptions:
      - cohort: boolean

random_dataset:
  registered:
    default_entry_types_granularity: count
    entry_types_exceptions:
      - individual: boolean
```
If you have assigned a controlled security level then you can assign a particular granularity per user and per entry type per user. You can do that by creating a **user-list** array with items that belong to each user and that need to have the following structure:
```
AV_Dataset:
  controlled:
    default_entry_types_granularity: record
    entry_types_exceptions:
      - individual: boolean
    user-list:
      - user_e-mail: jane.smith@beacon.ga4gh
        default_entry_types_granularity: count
        entry_types_exceptions:
          - individual: record
``` 

## Managing configuration

### Generic configuration

The beacon needs some configuration in order to show the correct mappings or information. In order to do that, the next variables inside [conf.py](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/conf/conf.py) can be modified for that purpose, being **uri** a critical one for showing the correct domain in the mappings of your beacon. The **uri_subpath** will be added behind this **uri** variable, in case there is an extension of the domain for your beacon. See next paragraph: Tips for configuring a nginx proxy compatible with Beacon PI.

```bash
beacon_id = 'org.ega-archive.beacon-ri-demo'  # ID of the Beacon
beacon_name = 'Beacon Reference Implementation demo'  # Name of the Beacon service
api_version = 'v2.0.0' # Version of the Beacon implementation
uri = 'http://localhost:5050'
uri_subpath = '/api'
complete_url = uri + uri_subpath
environment = 'test'
description = r"This Beacon is based on synthetic data hosted at the <a href='https://ega-archive.org/datasets/EGAD00001003338'>EGA</a>. The dataset contains 2504 samples including genetic data based on 1K Genomes data, and 76 individual attributes and phenotypic data derived from UKBiobank."
version = api_version_yaml['api_version']
welcome_url = 'https://beacon.ega-archive.org/'
alternative_url = 'https://beacon.ega-archive.org/api'
create_datetime = '2021-11-29T12:00:00.000000'
update_datetime = ''
default_beacon_granularity = "record" # boolean, count or record
security_levels = ['PUBLIC', 'REGISTERED', 'CONTROLLED']
documentation_url = 'https://b2ri-documentation-demo.ega-archive.org/'
cors_urls = ["http://localhost:3003", "http://localhost:3000"]

# Service Info
ga4gh_service_type_group = 'org.ga4gh'
ga4gh_service_type_artifact = 'beacon'
ga4gh_service_type_version = '1.0'

# Organization info
org_id = 'EGA'  # Id of the organization
org_name = 'European Genome-Phenome Archive (EGA)'  # Full name
org_description = 'The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.'
org_adress = 'C/ Dr. Aiguader, 88, PRBB Building 08003 Barcelona, Spain'
org_welcome_url = 'https://ega-archive.org/'
org_contact_url = 'mailto:beacon.ega@crg.eu'
org_logo_url = 'https://legacy.ega-archive.org/images/logo.png'
org_info = ''
``` 

#### Tips for configuring a nginx proxy compatible with BeaconPI conf.py uri and uri_subpath vars

If you are building a nginx proxy on top of beacon PI instance, the configuration of your nginx proxy can be a bit tricky if you don't have in mind what do uri and uri_subpath do. First of all, uri sets the root url of your beacon, and uri_subpath adds an extension to each of the endpoints' routes.
This means, that if you want to add a nginx proxy with an extension between the root url and the /api (uri_subpath), you will need to set the extension to the root url of the localhost, like this:
```nginx
location /extension/api/ {
    proxy_pass http://localhost:5050;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

And your conf.py variables will need to look like:
```bash
uri = 'https://<yourdomain>'
uri_subpath = '/extension/api'
complete_url = uri + uri_subpath
```

### Models configuration

#### Enable/Disable model

Now, beacon PI admits different models to be plugged in. By default, two models come with beacon PI, which are:
- EUCAIM
- ga4gh/beacon_v2_default_model

In order to enable or disable a model, you need to edit the conf/models/models_conf.yml file and set their enabled values to True or False as preferred, like shown below:
```yml
ga4gh/beacon_v2_default_model:
  model_enabled: True

EUCAIM:
  model_enabled: True
```

#### Add a new model

On the other hand, to add a new model, you need to create a new folder with the name of your model and add three folders within the new model: conf, connections, validator, with these exact same names.
In the folder conf you need to add the yml files of each entity of the model inside a folder called entry_types. The name of the files need to match the id of the entity (e.g. analysis.yml will show analysis as the main key). The info inside needs to have the same parameters shown here:
```yml
analysis:
  entry_type_enabled: True
  max_granularity: record
  endpoint_name: analyses
  open_api_definition: https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/analyses/endpoints.json
  allow_queries_without_filters: True
  allow_id_query: True # endpoint_name/{id}
  response_type: non_collection
  connection:
    name: mongo
    database: beacon
    table: analyses
    functions:
      function_name_assigned: get_phenotypic_endpoint
      id_query_function_name_assigned: get_phenotypic_endpoint_with_id
  info:
    name: Bioinformatics analysis
    ontology_id: edam:operation_2945
    ontology_name: Analysis
    description: Apply analytical methods to existing data of a specific type.
  schema:
    specification: Beacon v2
    default_schema_id: beacon-analysis-v2.0.0
    default_schema_name: Default schema for a bioinformatics analysis
    reference_to_default_schema_definition: https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/analyses/defaultSchema.json
    default_schema_version: v2.0.0
    supported_schemas:
      - beacon-analysis-v2.0.0
      - beacon-analysis-v2.0.1
      - beacon-analysis-v2.1.0
      - beacon-analysis-v2.1.1
      - beacon-analysis-v2.1.2
      - beacon-analysis-v2.2.0
  lookups:
    biosample:
      endpoint_name: analyses/{id}/biosamples
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: biosamples
        functions:
          function_name_assigned: get_phenotypic_cross_query
    cohort:
      endpoint_name: analyses/{id}/cohorts
      response_type: collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: cohorts
        functions:
          function_name_assigned: get_cross_collections
    dataset:
      endpoint_name: analyses/{id}/datasets
      response_type: collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: datasets
        functions:
          function_name_assigned: get_cross_collections
    genomicVariant:
      endpoint_name: analyses/{id}/g_variants
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: genomicVariations
        functions:
          function_name_assigned: get_variants_of_phenotypic_endpoint
    individual:
      endpoint_name: analyses/{id}/individuals
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: individuals
        functions:
          function_name_assigned: get_phenotypic_cross_query
    run:
      endpoint_name: analyses/{id}/runs
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: runs
        functions:
          function_name_assigned: get_phenotypic_cross_query
```
Note: lookups entries can vary depending on the entities available for the model.
Also, the connections folder needs to have a folder with the name of the connection for the model (only mongo available now) and then have the minimum files (collections.py and non_collections.py) with the functions that are shown in the yml conf file for each entity.
Lastly, in validator, pydantic classes per entity and collection/non_collection type need to be added, with the name of the schema they belong to and with the different properties and values that each of the entity carries in them.

### Budget configuration

If you wish to put a limit on how many queries can a user or a certain IP make to your beacon, that is now possible. In order to do that, edit the the variables under *Query budget* inside [conf.py](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/conf/conf.py). 

```bash
# Query Budget
query_budget_per_user = False
query_budget_per_ip = False
query_budget_amount = 3
query_budget_time_in_seconds = 20
query_budget_database = 'mongo'
query_budget_db_name = 'beacon'
query_budget_table = 'budget'
```

The variables **query_budget_per_user** and **query_budget_per_ip** are boolean, and if True, they will restrict the queries per user and ip. These depend on **query_budget_amount** which will tell the amount allowed per user/ip and **query_budge_time_in_seconds** which will be the period of time that this amount of queries attempt will last. Bear in mind that activating query budget per user means that if a user is not authenticated, the query will fail unless the query budget per ip is also activated. Both ip and user budgets can be activated at the same time, having preference per user but if unauthenticated, ip queries will also be valid.

### Query rounding

The last thing you can configure inside [conf.py](https://github.com/EGA-archive/beacon-production-prototype/tree/main/beacon/conf/conf.py) is query rounding, editing the variables under that name.

```bash
# Query Rounding
imprecise_count=0 # If imprecise_count is 0, no modification of the count will be applied. If it's different than 0, count will always be this number when count is smaller than this number.
round_to_tens=False # If true, the rounding will be done to the immediate superior tenth if the imprecise_count is 0
round_to_hundreds=False # If true, the rounding will be done to the immediate superior hundredth if the imprecise_count is 0 and the round_to_tens is false
```

The variable **imprecise_count** will override all the others and will tell beacon to round the counts to a number equal or greater than the one assigned to this variable. After that, the **round_to_tens** is the variable that will have priority if true, and will round a count to the immediate superior tenth. The last one **round_to_hundreds** will do the same as the one before but rounding to the immedate superior hundredth.

### Entry types configuration

The entry types configuration now works with yml files inside each model. You can edit the values of the parameters below (the values after the :). The keys have to remain the same as shown below.

```yml
analysis:
  entry_type_enabled: True
  max_granularity: record
  endpoint_name: analyses
  open_api_definition: https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/analyses/endpoints.json
  allow_queries_without_filters: True
  allow_id_query: True # endpoint_name/{id}
  response_type: non_collection
  connection:
    name: mongo
    database: beacon
    table: analyses
    functions:
      function_name_assigned: get_phenotypic_endpoint
      id_query_function_name_assigned: get_phenotypic_endpoint_with_id
  info:
    name: Bioinformatics analysis
    ontology_id: edam:operation_2945
    ontology_name: Analysis
    description: Apply analytical methods to existing data of a specific type.
  schema:
    specification: Beacon v2
    default_schema_id: beacon-analysis-v2.0.0
    default_schema_name: Default schema for a bioinformatics analysis
    reference_to_default_schema_definition: https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/analyses/defaultSchema.json
    default_schema_version: v2.0.0
    supported_schemas:
      - beacon-analysis-v2.0.0
      - beacon-analysis-v2.0.1
      - beacon-analysis-v2.1.0
      - beacon-analysis-v2.1.1
      - beacon-analysis-v2.1.2
      - beacon-analysis-v2.2.0
  lookups:
    biosample:
      endpoint_name: analyses/{id}/biosamples
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: biosamples
        functions:
          function_name_assigned: get_phenotypic_cross_query
    cohort:
      endpoint_name: analyses/{id}/cohorts
      response_type: collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: cohorts
        functions:
          function_name_assigned: get_cross_collections
    dataset:
      endpoint_name: analyses/{id}/datasets
      response_type: collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: datasets
        functions:
          function_name_assigned: get_cross_collections
    genomicVariant:
      endpoint_name: analyses/{id}/g_variants
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: genomicVariations
        functions:
          function_name_assigned: get_variants_of_phenotypic_endpoint
    individual:
      endpoint_name: analyses/{id}/individuals
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: individuals
        functions:
          function_name_assigned: get_phenotypic_cross_query
    run:
      endpoint_name: analyses/{id}/runs
      response_type: non_collection
      endpoint_enabled: True
      connection:
        name: mongo
        database: beacon
        table: runs
        functions:
          function_name_assigned: get_phenotypic_cross_query
```
These files are located in their respective folder (beacon/models/conf/entry_types).

The most importants are the variable **endpoint_name**, which will change the name of the endpoint that will show the response for analysis type of records, the **max_granularity**, which will change the maximum granularity allowed for this particular entry type, the **allow_queries_without_filters**, which will allow queries without filters if True to that particular endpoint. Also, **defaultSchema_id** says which is the version of the schema of the records that are stored in this entry type and when receiving a requestedSchema different than this id, the beacon will respond with a bad request, as other schemas are not supported. The variables that are below *Map configuration* which will activate or deactivate the different endpoints related to this entry type. See explanation next to each of the variables to know more.

### Test Mode

For verifying your beacon, there are datasets that you can reproduce from the real data ones, that can serve as test but with fake data. When verifying your beacon, the verifiers will test those datasets. Also, for unit testing, there is a test dataset we use. For declaring your dataset a test dataset, you have to edit the [datasets_conf.yml](https://github.com/EGA-archive/beacon2-pi-api/blob/main/beacon/conf/datasets/datasets_conf.yml) file and add an isTest: true parameter under the dataset desired, like this example:

```bash
CINECA_synthetic_cohort_EUROPE_UK1:
  isTest: false
test:
  isSynthetic: true
  isTest: true
```

### Execute the changes

After editing any comfiguration variable, save the file and restart the API to apply the changes by executing the next command:

```bash
docker compose restart beaconprod
```

## Fix for MongoDB exploit (CVE-2025-14847)

Beacon PI repository has been updated so the exploit for MongoDB (CVE-2025-14847) is not an issue anymore. In order to do that, the following points have been implemented:
* Removed exposing ports in docker-compose.yml file
* Built done from a mongod.conf file
* Mongo image for major version 5 adjusted to 5.0.32, not allowing prior versions with the vulnerability to be built.

**Please, make sure you update your mongoDB instance and rebuild the mongoDB container after this update.**

The steps to reproduce this exploit and check that your instance is not vulnerable anymore is to download this [repo](https://github.com/Security-Phoenix-demo/mongobleed-exploit-CVE-2025-14847) and insert it in beacon folder.

Then build the beaconprod conainer and execute the next command:
```bash
docker exec -it beaconprod python beacon/mongobleed-exploit-CVE-2025-14847-main/exploit/mongobleed.py --host mongoprod
```
If the message is something like: 
![MongoDB no vulnerabilities](https://github.com/EGA-archive/beacon-production-prototype/blob/main/ri-tools/files/mongobleed_ok.png)
Then it means the instance is safe.
Otherwise, you would get a message like:
![MongoDB vulnerabilities](https://github.com/EGA-archive/beacon-production-prototype/blob/main/ri-tools/files/mongobleed_vuln.png)

## Tests report

![Beacon prod concurrency test](https://github.com/EGA-archive/beacon-production-prototype/blob/main/ri-tools/files/concurrencytest.png)


