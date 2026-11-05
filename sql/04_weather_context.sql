/* Saatlik meteoroloji bağlamını olaylara ekle.
   event_at içindeki dakika/saniyeyi saat başına indirerek en yakın tam saate bağlar.
   Hazır CSV sentetik fallback içeriyorsa sonuçlar gerçek hava koşulu olarak yorumlanmamalıdır.
*/
SELECT
    se.event_type,
    COUNT(*) AS event_count,
    ROUND(AVG(se.severity_1_5)::NUMERIC, 2) AS avg_severity,
    ROUND(AVG(w.temperature_2m_c), 2) AS avg_temperature_c,
    ROUND(AVG(w.relative_humidity_2m_pct), 2) AS avg_humidity_pct,
    ROUND(AVG(w.precipitation_mm), 2) AS avg_precipitation_mm,
    ROUND(AVG(w.wind_speed_10m_kmh), 2) AS avg_wind_speed_kmh
FROM sensor_events AS se
LEFT JOIN weather_hourly AS w
  ON w.observed_at = DATE_TRUNC('hour', se.event_at)
GROUP BY se.event_type
ORDER BY event_count DESC;
