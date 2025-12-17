docker-compose up -d --build beaconimages dbimages
sleep 15
cd beacon/connections/mongo
make