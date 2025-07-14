build:
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr1.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr2.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr3.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr4.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr5.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr6.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr7.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr8.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr9.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr10.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr11.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr12.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr13.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr14.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr15.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr16.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr17_chr18.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr19.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr20.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr21.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chr22.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chrX.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/chrY.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection genomicVariations
	gunzip --stdout /vault/oriol/oriol_beacon_data/gnomAD38/gnomAD38_datasets.json.gz | mongoimport --jsonArray --uri "mongodb://root:example@127.0.0.1:27017/beacon?authSource=admin" --collection datasets
	docker exec beaconprod python -m beacon.connections.mongo.reindex
