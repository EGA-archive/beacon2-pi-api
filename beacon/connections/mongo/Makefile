DATA_PATH = /data/af-ega

build:
	docker exec mongoprodega mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/GCAT.json --collection datasets
	docker exec mongoprodega mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/gnomad4.json --collection datasets
	docker exec mongoprodega mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/gnomad2.json --collection datasets
