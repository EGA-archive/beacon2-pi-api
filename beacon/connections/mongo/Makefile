DATA_PATH = /data/af-ega

build:
	docker exec mongoprodega mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/GCAT.json --collection datasets
	docker exec mongoprodega mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/gnomad4.json --collection datasets
	docker exec mongoprodega mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --file $(DATA_PATH)/gnomad2.json --collection datasets
	gunzip --stdout /vault/bio-scratch/mireia/beacon2_RI_Tools_v2/beacon-data-tools/genomicVariations_gnomAD4.1_chrX.json | docker exec -i mongoprodega sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations'
	gunzip --stdout /vault/bio-scratch/mireia/beacon2_RI_Tools_v2/beacon-data-tools/genomicVariations_GCAT_chrX.json.gz | docker exec -i mongoprodega sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations'
	gunzip --stdout /vault/bio-scratch/mireia/beacon2_RI_Tools_v2/beacon-data-tools/genomicVariations_gnomAD2.1.1_chrX.json.gz | docker exec -i mongoprodega sh -c 'mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations'