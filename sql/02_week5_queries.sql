/* KURA #5 - HAFTA 5 SORGULARI */

/* 1) Olay türüne göre bildirim sayısı ve toplam maliyet (GROUP BY, SUM).
   LEFT JOIN kullanıyoruz; bildirimi olmayan olay türleri de listede kalır.
   SUM(cost_usd), NULL maliyetleri otomatik olarak toplama katmaz.
*/
SELECT
    se.event_type,
    COUNT(n.id) AS notification_count,
    ROUND(COALESCE(SUM(n.cost_usd), 0), 4) AS total_cost_usd,
    ROUND(AVG(n.cost_usd), 6) AS avg_cost_per_notification_usd,
    ROUND(AVG(n.total_tokens), 1) AS avg_tokens
FROM sensor_events AS se
LEFT JOIN notifications AS n ON n.event_id = se.id
GROUP BY se.event_type
ORDER BY total_cost_usd DESC;


/* 2) event_id boş bildirim sayısı ve yüzdesi.
   Payda bütün bildirimlerdir; oranı bu şekilde yorumluyoruz.
*/
SELECT
    COUNT(*) FILTER (WHERE event_id IS NULL) AS missing_event_id_count,
    COUNT(*) AS total_notifications,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE event_id IS NULL) / NULLIF(COUNT(*), 0),
        2
    ) AS missing_event_id_percent
FROM notifications;


/* 3) Toplam maliyeti 1 USD üstünde olan olay türleri (HAVING).
   NULL cost değerleri SUM tarafından yok sayılır; eksik maliyet sayısı ayrıca raporlanmalıdır.
*/
SELECT
    se.event_type,
    COUNT(n.id) AS notification_count,
    ROUND(SUM(n.cost_usd), 4) AS total_cost_usd
FROM sensor_events AS se
JOIN notifications AS n ON n.event_id = se.id
GROUP BY se.event_type
HAVING SUM(n.cost_usd) > 1.00
ORDER BY total_cost_usd DESC;


/* 4) CASE WHEN ile gecikme kategorileri ve şiddet x kategori çapraz tablosu.
   Negatif gecikme ayrı tutulur; hızlı/geç kategorisine karıştırılmaz.
*/
WITH latency_classified AS (
    SELECT
        n.id AS notification_id,
        n.event_id,
        CASE
            WHEN n.latency_ms IS NULL THEN 'UNKNOWN'
            WHEN n.latency_ms < 0 THEN 'NEGATIVE_CLOCK_ERROR'
            WHEN n.latency_ms <= 1000 THEN 'FAST_0_1000_MS'
            WHEN n.latency_ms <= 3000 THEN 'MEDIUM_1001_3000_MS'
            ELSE 'SLOW_OVER_3000_MS'
        END AS latency_category
    FROM notifications AS n
)
SELECT
    se.severity_1_5,
    lc.latency_category,
    COUNT(*) AS notification_count
FROM latency_classified AS lc
JOIN sensor_events AS se ON se.id = lc.event_id
GROUP BY se.severity_1_5, lc.latency_category
ORDER BY se.severity_1_5, lc.latency_category;


/* 5) Saatlik bildirim yoğunluğu ve o saatteki ortalama gecikme.
   sent_at, bu örnek projede Europe/Istanbul yerel saatidir.
*/
SELECT
    EXTRACT(HOUR FROM sent_at)::INT AS sent_hour,
    COUNT(*) AS notification_count,
    COUNT(*) FILTER (WHERE latency_ms >= 0) AS valid_latency_count,
    ROUND(AVG(latency_ms) FILTER (WHERE latency_ms >= 0), 1) AS avg_valid_latency_ms
FROM notifications
GROUP BY EXTRACT(HOUR FROM sent_at)
ORDER BY notification_count DESC, sent_hour;


/* Ek araştırma: Şiddet ile gecikme ilişkili mi?
   CORR Pearson korelasyonunu hesaplar. Negatif gecikmeler saat senkron hatası
   kabul edildiği için yalnızca bu istatistikte dışarıda bırakılır; ham tablodan silinmez.
*/
SELECT
    COUNT(*) AS valid_pairs,
    ROUND(CORR(se.severity_1_5::DOUBLE PRECISION,
               n.latency_ms::DOUBLE PRECISION)::NUMERIC, 4) AS pearson_r
FROM sensor_events AS se
JOIN notifications AS n ON n.event_id = se.id
WHERE n.latency_ms >= 0;


/* Hafta 4 veri kalite kartı: üç beklenen sorunu görünür kıl. */
SELECT
    COUNT(*) FILTER (WHERE event_id IS NULL) AS empty_event_id_rows,
    COUNT(*) FILTER (WHERE cost_usd IS NULL) AS empty_cost_rows,
    COUNT(*) FILTER (WHERE latency_ms < 0) AS negative_latency_rows,
    COUNT(*) AS total_notification_rows
FROM notifications;

/* Negatif gecikme satırlarını silmeden listele. */
SELECT id, event_id, model_name, latency_ms, sent_at
FROM notifications
WHERE latency_ms < 0
ORDER BY id;
