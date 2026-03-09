DATA_PATH = /data/elixir

build:
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/datasets.json --collection datasets
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/individuals.json --collection individuals
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/cohorts.json --collection cohorts
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/analyses.json --collection analyses
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/biosamples.json --collection biosamples
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/genomicVariations.json --collection genomicVariations
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/runs.json --collection runs
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/targets.json --collection targets
	docker exec mongoprodelixir mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/caseLevelData.json --collection caseLevelData
	docker exec beaconprodelixir python -m beacon.connections.mongo.extract_filtering_terms
	docker exec beaconprodelixir python -m beacon.connections.mongo.reindex