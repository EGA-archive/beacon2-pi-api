build:
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/datasets.json --collection datasets
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/individuals.json --collection individuals
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/cohorts.json --collection cohorts
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/analyses.json --collection analyses
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/biosamples.json --collection biosamples
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/genomicVariations.json --collection genomicVariations
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/runs.json --collection runs
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/targets.json --collection targets
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /data/caseLevelData.json --collection caseLevelData