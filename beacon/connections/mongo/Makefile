DATA_PATH = data/mock

build:
	docker exec mongoafprodspain /bin/bash -c 'mongo beacon -u root -p example --authenticationDatabase admin --eval "db.datasets.deleteMany({})"'
	docker exec mongoafprodspain /bin/bash -c 'mongo beacon -u root -p example --authenticationDatabase admin --eval "db.genomicVariations.deleteMany({})"'
	docker exec mongoafprodspain mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/datasets.json --collection datasets
	docker exec mongoafprodspain mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/genomicVariations.json --collection genomicVariations
	docker exec mongoafprodspain mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/roma.json --collection datasets
	docker exec mongoafprodspain mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file /vault/bio-scratch/mireia/beacon-datasets/iberian-roman/genomicVariations_iberian-roman.json --collection genomicVariations
	docker exec beaconafprodspain python -m beacon.connections.mongo.reindex