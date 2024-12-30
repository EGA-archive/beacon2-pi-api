build:
	docker cp data/analyses.json mongoprod:tmp/analyses.json
	docker cp data/biosamples.json mongoprod:tmp/biosamples.json
	docker cp data/cohorts.json mongoprod:tmp/cohorts.json
	docker cp data/datasets.json mongoprod:tmp/datasets.json
	docker cp data/genomicVariations.json mongoprod:tmp/genomicVariations.json
	docker cp data/individuals.json mongoprod:tmp/individuals.json
	docker cp data/runs.json mongoprod:tmp/runs.json
	docker cp data/targets.json mongoprod:tmp/targets.json
	docker cp data/caseLevelData.json mongoprod:tmp/caseLevelData.json
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/datasets.json --collection datasets
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/individuals.json --collection individuals
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/cohorts.json --collection cohorts
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/analyses.json --collection analyses
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/biosamples.json --collection biosamples
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/genomicVariations.json --collection genomicVariations
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/runs.json --collection runs
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/targets.json --collection targets
	docker exec mongoprod mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /tmp/caseLevelData.json --collection caseLevelData