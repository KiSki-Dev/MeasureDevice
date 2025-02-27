--
-- File generated with SQLiteStudio v3.4.17 on Do Feb 27 22:18:45 2025
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: heatIndexDays
CREATE TABLE IF NOT EXISTS heatIndexDays (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: heatIndexHours
CREATE TABLE IF NOT EXISTS heatIndexHours (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: heatIndexMin
CREATE TABLE IF NOT EXISTS heatIndexMin (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: humidityDays
CREATE TABLE IF NOT EXISTS humidityDays (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: humidityHours
CREATE TABLE IF NOT EXISTS humidityHours (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: humidityMin
CREATE TABLE IF NOT EXISTS humidityMin (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: lightDays
CREATE TABLE IF NOT EXISTS lightDays (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: lightHours
CREATE TABLE IF NOT EXISTS lightHours (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: lightMin
CREATE TABLE IF NOT EXISTS lightMin (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: temperatureDays
CREATE TABLE IF NOT EXISTS temperatureDays (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: temperatureHours
CREATE TABLE IF NOT EXISTS temperatureHours (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: temperatureMin
CREATE TABLE IF NOT EXISTS temperatureMin (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: voltageDays
CREATE TABLE IF NOT EXISTS voltageDays (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: voltageHours
CREATE TABLE IF NOT EXISTS voltageHours (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


-- Table: voltageMin
CREATE TABLE IF NOT EXISTS voltageMin (
    value     INT,
    timestamp INT,
    id        INTEGER PRIMARY KEY
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
