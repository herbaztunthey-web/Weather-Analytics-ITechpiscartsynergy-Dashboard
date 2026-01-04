-- 1. Create the table
CREATE TABLE weather (
    id INTEGER PRIMARY KEY,
    city TEXT,
    temperature REAL,
    condition TEXT,
    humidity INTEGER
);-- 3. Level 1 Skill: See the data
SELECT * FROM weather;-- 2. Insert some sample data
INSERT INTO weather (city, temperature, condition, humidity) VALUES 
('Lagos', 31.5, 'Sunny', 60),
('London', 12.0, 'Rainy', 85),
('New York', 22.1, 'Cloudy', 55),
('Tokyo', 18.5, 'Clear', 40),
('Nairobi', 25.0, 'Sunny', 50);-- 1. Create the table
CREATE TABLE weather (
    id INTEGER PRIMARY KEY,
    city TEXT,
    temperature REAL,
    condition TEXT,
    humidity INTEGER
);