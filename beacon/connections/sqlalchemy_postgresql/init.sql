CREATE TABLE IF NOT EXISTS campings (
    id SERIAL PRIMARY KEY,
    camping_id VARCHAR(100) NOT NULL,
    dataset_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO campings (
    camping_id,
    dataset_id,
    name,
    location,
    latitude,
    longitude,
    description
)
VALUES
('CAMP001','campings','Green Valley','Girona',42.123456,2.654321,'Mountain campsite'),
('CAMP002','campings','Lake View','Lleida',42.245678,1.234567,'Next to a lake'),
('CAMP003','campings','Forest Retreat','Barcelona',41.567890,2.123456,'Surrounded by forest'),
('CAMP004','campings','Costa Camp','Tarragona',41.098765,1.345678,'Near the beach'),
('CAMP005','campings','Sunny Fields','Girona',42.876543,2.876543,'Family friendly'),
('CAMP006','campings','River Camp','Lleida',42.456789,0.987654,'Beside a river'),
('CAMP007','campings','Pine Woods','Barcelona',41.876543,1.987654,'Quiet natural setting'),
('CAMP008','campings','Nature Escape','Tarragona',41.654321,1.123456,'Ideal for hiking'),
('CAMP009','campings','Mountain Peak','Girona',42.765432,2.234567,'High-altitude camping'),
('CAMP010','campings','Blue Sky Camp','Lleida',42.345678,0.876543,'Panoramic views');

CREATE TABLE datasets (
    id TEXT PRIMARY KEY,
    description TEXT
);

INSERT INTO datasets (id, description)
VALUES (
    'campings',
    'The dataset for campings'
);