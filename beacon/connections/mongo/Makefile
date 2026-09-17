
DATA_PATH = /data/elixir
DATA_PATH2 = /data/TCGA

build:
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.datasets.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.biosamples.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.analyses.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.cohorts.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.individuals.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.runs.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.genomicVariations.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.caseLevelData.deleteMany({})'
	docker exec mongoprodelixir mongosh "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --eval 'db.targets.deleteMany({})'
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/datasets.json --collection datasets
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/individuals.json --collection individuals
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/cohorts.json --collection cohorts
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/analyses.json --collection analyses
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/biosamples.json --collection biosamples
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/genomicVariations.json --collection genomicVariations
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/runs.json --collection runs
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/targets.json --collection targets
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/caseLevelData.json --collection caseLevelData
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH2)/datasets.json --collection datasets
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH2)/individuals.json --collection individuals
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH2)/cohorts.json --collection cohorts
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH2)/analyses.json --collection analyses
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH2)/biosamples.json --collection biosamples
	gunzip --stdout data/TCGA/genomicVariations.json.gz | docker exec -i mongoprodelixir sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations'	
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH2)/runs.json --collection runs
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH2)/targets.json --collection targets
	gunzip --stdout data/TCGA/caseLevelData.json.gz | docker exec -i mongoprodelixir sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection caseLevelData'
	docker exec beaconprodelixir python -m beacon.connections.mongo.extract_filtering_terms
	docker exec beaconprodelixir python -m beacon.connections.mongo.reindex