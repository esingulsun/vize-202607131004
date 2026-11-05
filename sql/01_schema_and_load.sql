/*
KURA #5 - PostgreSQL schema and CSV import
Run from the project root with:
  psql -d kura5_city -f sql/01_schema_and_load.sql
Create the database once beforehand:
  createdb kura5_city

If you use pgAdmin, create the database, run only the CREATE TABLE statements,
then use Import/Export on each table with its matching CSV in data/.
*/

CREATE TABLE IF NOT EXISTS sensors (
    id      VARCHAR(10) PRIMARY KEY,
    region  VARCHAR(60) NOT NULL,
    type    VARCHAR(40) NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_events (
    id           BIGINT PRIMARY KEY,
    sensor_id    VARCHAR(10) NOT NULL REFERENCES sensors(id),
    event_type   VARCHAR(50) NOT NULL,
    severity_1_5 SMALLINT NOT NULL CHECK (severity_1_5 BETWEEN 1 AND 5),
    event_at     TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id          BIGINT PRIMARY KEY,
    event_id    BIGINT NULL REFERENCES sensor_events(id),
    model_name  VARCHAR(60) NOT NULL,
    total_tokens INTEGER NOT NULL CHECK (total_tokens >= 0),
    cost_usd    NUMERIC(12,7) NULL,
    latency_ms  INTEGER NULL,
    sent_at     TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_hourly (
    observed_at             TIMESTAMP PRIMARY KEY,
    temperature_2m_c        NUMERIC(6,2),
    relative_humidity_2m_pct NUMERIC(6,2),
    precipitation_mm        NUMERIC(7,2),
    wind_speed_10m_kmh      NUMERIC(7,2),
    data_source             VARCHAR(100) NOT NULL
);

/*
CSV import commands (run in psql from the project root).
The blank event_id and cost_usd fields become SQL NULL values.
If tables already contain rows, TRUNCATE them first to avoid duplicate PK errors.
*/
TRUNCATE TABLE notifications, sensor_events, sensors, weather_hourly;

\copy sensors(id, region, type) FROM 'data/sensors.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy sensor_events(id, sensor_id, event_type, severity_1_5, event_at) FROM 'data/sensor_events.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy notifications(id, event_id, model_name, total_tokens, cost_usd, latency_ms, sent_at) FROM 'data/notifications.csv' WITH (FORMAT csv, HEADER true, NULL '')
\copy weather_hourly(observed_at, temperature_2m_c, relative_humidity_2m_pct, precipitation_mm, wind_speed_10m_kmh, data_source) FROM 'data/weather_hourly.csv' WITH (FORMAT csv, HEADER true, NULL '')

CREATE INDEX IF NOT EXISTS idx_sensor_events_event_type ON sensor_events(event_type);
CREATE INDEX IF NOT EXISTS idx_sensor_events_event_at ON sensor_events(event_at);
CREATE INDEX IF NOT EXISTS idx_notifications_event_id ON notifications(event_id);
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications(sent_at);
CREATE INDEX IF NOT EXISTS idx_notifications_model_name ON notifications(model_name);

ANALYZE sensors;
ANALYZE sensor_events;
ANALYZE notifications;
ANALYZE weather_hourly;
