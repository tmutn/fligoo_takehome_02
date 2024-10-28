DROP DATABASE IF EXISTS testfligoo;
CREATE DATABASE testfligoo;

\c testfligoo

CREATE TABLE IF NOT EXISTS testdata (
    flight_date DATE,
    flight_status TEXT,
    departure_airport TEXT,
    departure_timezone TEXT,
    arrival_airport TEXT,
    arrival_timezone TEXT,
    arrival_terminal TEXT,
    airline_name TEXT,
    flight_number TEXT
);
