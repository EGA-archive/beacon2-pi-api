DATA_PATH = /data

build:
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.targets.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.caseLevelData.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.runs.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.analyses.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.biosamples.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.cohorts.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.datasets.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.individuals.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.genomicVariations.deleteMany({})"'
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.filtering_terms.deleteMany({})"'
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/datasets.json --collection datasets
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/individuals.json --collection individuals
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/cohorts.json --collection cohorts
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/analyses.json --collection analyses
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/biosamples.json --collection biosamples
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/genomicVariations.json --collection genomicVariations
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/runs.json --collection runs
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/targets.json --collection targets
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/caseLevelData.json --collection caseLevelData
	docker exec beaconspreg python -m beacon.connections.mongo.extract_filtering_terms
	docker exec beaconspreg python -m beacon.connections.mongo.reindex