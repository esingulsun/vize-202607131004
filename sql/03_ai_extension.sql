/* DÖNEM SONU YZ BÖLÜMÜ: Olay türü x model maliyet ilişki tablosu.
   Bu tablo, hangi olay türünde hangi modelin kaç bildirim ürettiğini,
   toplam/ortalama maliyetini ve gecikmesini saklar.
*/
CREATE TABLE IF NOT EXISTS event_notification_cost_relation (
    event_type                 VARCHAR(50) NOT NULL,
    model_name                 VARCHAR(60) NOT NULL,
    notification_count         INTEGER NOT NULL,
    notifications_with_cost    INTEGER NOT NULL,
    total_cost_usd             NUMERIC(14,7),
    avg_cost_usd               NUMERIC(14,7),
    avg_tokens                 NUMERIC(12,2),
    avg_latency_ms             NUMERIC(12,2),
    PRIMARY KEY (event_type, model_name)
);

TRUNCATE TABLE event_notification_cost_relation;

INSERT INTO event_notification_cost_relation (
    event_type, model_name, notification_count, notifications_with_cost,
    total_cost_usd, avg_cost_usd, avg_tokens, avg_latency_ms
)
SELECT
    se.event_type,
    n.model_name,
    COUNT(n.id),
    COUNT(n.cost_usd),
    ROUND(SUM(n.cost_usd), 7),
    ROUND(AVG(n.cost_usd), 7),
    ROUND(AVG(n.total_tokens), 2),
    ROUND(AVG(n.latency_ms) FILTER (WHERE n.latency_ms >= 0), 2)
FROM sensor_events AS se
JOIN notifications AS n ON n.event_id = se.id
GROUP BY se.event_type, n.model_name;

/* İlişki tablosunu incele: en yüksek toplam maliyetten en düşüğe. */
SELECT *
FROM event_notification_cost_relation
ORDER BY total_cost_usd DESC NULLS LAST;

/* Model karşılaştırması - genel görünüm. */
SELECT
    model_name,
    COUNT(*) AS notification_count,
    ROUND(AVG(cost_usd), 7) AS avg_cost_usd,
    ROUND(AVG(latency_ms) FILTER (WHERE latency_ms >= 0), 1) AS avg_valid_latency_ms,
    ROUND(AVG(total_tokens), 1) AS avg_tokens
FROM notifications
WHERE event_id IS NOT NULL
GROUP BY model_name
ORDER BY avg_cost_usd;

/* Daha adil karşılaştırma: aynı olay türü ve aynı şiddet seviyesinde modeller.
   Farklı iş yükleri modelleri yanıltıcı biçimde avantajlı gösterebilir.
*/
SELECT
    se.event_type,
    se.severity_1_5,
    n.model_name,
    COUNT(*) AS notification_count,
    ROUND(AVG(n.cost_usd), 7) AS avg_cost_usd,
    ROUND(AVG(n.latency_ms) FILTER (WHERE n.latency_ms >= 0), 1) AS avg_valid_latency_ms
FROM sensor_events AS se
JOIN notifications AS n ON n.event_id = se.id
GROUP BY se.event_type, se.severity_1_5, n.model_name
ORDER BY se.event_type, se.severity_1_5, avg_cost_usd;
