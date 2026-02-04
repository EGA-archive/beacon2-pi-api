DATA_PATH = /data

build:
	docker exec mongospreg /bin/bash -c 'mongo beacon -u root -p example --port 27024 --authenticationDatabase admin --eval "db.datasets.deleteMany({})"'
	docker exec mongospreg mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27024/beacon?authSource=admin" --file $(DATA_PATH)/datasets.json --collection datasets