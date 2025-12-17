DATA_PATH = /data/EUCAIM

build:
	gunzip --stdout data/EUCAIM/CollectionsMetadata.json.gz | docker exec -i mongoimages sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection collections'
	gunzip --stdout data/EUCAIM/PatientsMetadata.json.gz | docker exec -i mongoimages sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection patients'
	docker exec beaconimages python -m beacon.connections.mongo.extract_filtering_terms
	docker exec beaconimages python -m beacon.connections.mongo.reindex
