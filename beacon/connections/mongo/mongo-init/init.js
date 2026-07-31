conn = new Mongo({ useUnifiedTopology: true });
db = conn.getDB("beacon");


// db.beacon.createIndex({ "address.zip": 1 }, { unique: false });
// db.beacon.insert({ "address": { "city": "Paris", "zip": "123" }, "name": "Mike", "phone": "1234" });
// db.beacon.insert({ "address": { "city": "Marsel", "zip": "321" }, "name": "Helga", "phone": "4321" });

// Create collections

db.createCollection("analyses");
db.createCollection("biosamples");
db.createCollection("cohorts");
db.createCollection("datasets");
db.createCollection("genomicVariations");
db.createCollection("individuals");
db.createCollection("runs");
