docker-compose up -d --build beaconprod db
sleep 15
cd beacon/connections/mongo
make