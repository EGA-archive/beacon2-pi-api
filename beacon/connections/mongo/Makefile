DATA_PATH = /data/mock

build:
	docker exec mongoprodspain /bin/bash -c 'mongo beacon -u root -p example --port 27023 --authenticationDatabase admin --eval "db.datasets.deleteMany({})"'
	docker exec mongoprodspain /bin/bash -c 'mongo beacon -u root -p example --port 27023 --authenticationDatabase admin --eval "db.genomicVariations.deleteMany({})"'
	docker exec mongoprodspain mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27023/beacon?authSource=admin" --file $(DATA_PATH)/datasets.json --collection datasets
	docker exec mongoprodspain mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27023/beacon?authSource=admin" --file $(DATA_PATH)/genomicVariations.json --collection genomicVariations
	docker exec beaconprodspain python -m beacon.connections.mongo.reindex