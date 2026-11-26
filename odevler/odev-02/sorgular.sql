-- Ödev 2, Bölüm 1: Filo soruları
-- Ad Soyad: Esin Gülsün Akdemir
-- Veritabanı: robot_fleet
-- Her sorgunun altına sonucu açıklayan tek cümlelik yorum yaz.

-- Soru 1: Her robotun adı, operatör adı ve operatör telefonu (INNER JOIN)
SELECT r.name, o.operator_name, o.phone
FROM robots r
INNER JOIN operators o ON r.operator_name = o.operator_name;
-- Yorum: 9 satır döndü; Mars-03'ün operatör alanı NULL olduğu için INNER JOIN onu eşleştiremedi ve listeden düştü.


-- Soru 2: Aynı liste, bütün robotlar görünsün (LEFT JOIN). 1. sorguyla karşılaştır, kim kayboldu?
SELECT r.name, o.operator_name, o.phone
FROM robots r
LEFT JOIN operators o ON r.operator_name = o.operator_name;
-- Yorum: 10 satır döndü; Mars-03 bu kez listede göründü, operatör ve telefon sütunları NULL olarak geldi çünkü LEFT JOIN eşleşmesi olmayan satırı da dahil eder.


-- Soru 3: Hiç görev almamış robotların adı ve modeli
SELECT r.name, r.model
FROM robots r
LEFT JOIN missions m ON r.id = m.robot_id
WHERE m.id IS NULL;
-- Yorum: 4 satır döndü; bu robotların missions tablosunda hiç kaydı yok, LEFT JOIN sonrası m.id NULL olan satırlar görevsiz robotlardır.


-- Soru 4a: JOIN ile hesaplanan toplam batarya (görevi olan robotlar)
SELECT SUM(r.battery_level) AS yanlis_toplam
FROM robots r
INNER JOIN missions m ON r.id = m.robot_id;

-- Soru 4b: JOIN kullanmadan doğru toplam
SELECT SUM(battery_level) AS dogru_toplam
FROM robots
WHERE id IN (SELECT DISTINCT robot_id FROM missions);

-- Yorum (iki sonuç ve fark): 4a'da her görev için robot satırı tekrar ettiğinden (fan-out) batarya değeri birden fazla sayıldı ve toplam şişti; 4b'de her robot yalnızca bir kez sayıldığı için gerçek toplam doğru çıktı.


-- Soru 5: Robot başına görev sayısı; count(*) ve count(m.id) yan yana
SELECT r.name,
       COUNT(*)    AS count_yildiz,
       COUNT(m.id) AS count_id
FROM robots r
LEFT JOIN missions m ON r.id = m.robot_id
GROUP BY r.name
ORDER BY r.name;
-- Yorum: Hiç görevi olmayan robotlarda count(*) 1 dönerken count(m.id) 0 döner çünkü count(*) NULL dahil tüm satırları sayar, count(m.id) ise yalnızca NULL olmayan değerleri sayar.
