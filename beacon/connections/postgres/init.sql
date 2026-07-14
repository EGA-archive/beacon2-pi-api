CREATE TABLE IF NOT EXISTS campings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);