# Ödev Raporu

> **Bu rapor yazdırılıp derste elden teslim edilir.**

---

**Ödev no:** Ödev 2     **Hafta:** 7     **Tarih:** 27 / 11 / 2026

**Ad Soyad:** Esin Gülsün Akdemir  **Öğrenci No:** 202607131004

**Program:** ☑ Yapay Zeka Operatörlüğü  ☐ Robotik ve Yapay Zeka

**Kullandığım veritabanı:** ☐ `llm_ops`  ☑ `robot_fleet`

**PR bağlantısı:** `https://github.com/esingulsun/vize-202607131004`

**Commit sayısı:** 3+

---

## 1. Fan-out (Soru 4)

Soru 4a'da `robots` ile `missions` tablosunu INNER JOIN ile birleştirip `SUM(r.battery_level)` aldığımda sonuç şişti. Nedeni: birden fazla görevi olan her robot için JOIN, o robotun satırını kaç görev varsa o kadar tekrarlıyor — batarya değeri birden fazla kez toplandı. Bu olaya "fan-out" deniyor.

4b'de `WHERE id IN (SELECT DISTINCT robot_id FROM missions)` ile JOIN kullanmadan her robotun bataryasını yalnızca bir kez topladım ve doğru sonucu elde ettim.

Gerçek bir raporda bu hata tehlikelidir: bütçe hesabında her robotun maliyeti kaç görevi varsa o kadar sayılır, toplam gerçeğin çok üzerinde çıkar ve yanlış kararlar alınır.

---

## 2. En Zor Karar (ERD)

Kendi projemde `notifications` tablosunun `event_id` sütununun NULL olmasına izin verip vermeyeceğime karar vermek en zorlu noktaydı. İki seçenek vardı: her bildirimin mutlaka bir olaya bağlı olması (NOT NULL FK), ya da bazı bildirimlerin sistem testi amaçlı event_id'siz gönderilmesi (NULL FK).

Veriye bakınca gerçekten event_id'siz bildirimler var, bu yüzden NULL olarak bıraktım. Bu karar kardinaliteyi de etkiledi: bir bildirim sıfır veya bir olaya bağlı olabilir, ERD'de `o|` işaretiyle gösterdim.

---

## 5. Yapay Zeka Kullanım Beyanı

☑ Kullandım, aşağıda belirttim:

| Soru no | Araç | Ne sordum (özet) | Cevabı nasıl doğruladım |
|---|---|---|---|
| 1-5 | Claude (Anthropic) | JOIN sorguları, fan-out açıklaması | psql'de çalıştırdım, 9 ve 10 rows sonuçlarını gördüm |
| 1-5 | Google Gemini | Sorgu yapısı kontrolü | Aynı sorguları manuel çalıştırarak doğruladım |
| Bölüm 2 | Claude (Anthropic) | ERD sözdizimi, normalizasyon örnekleri | Mermaid önizlemesiyle diyagramı kontrol ettim |

---

**İmza:** Esin Gülsün Akdemir

---

*Doğruluk beyanı: Bu çalışmayı kendim yaptım. Kullandığım tüm yardımcı kaynakları ve yapay zeka araçlarını yukarıda beyan ettim.*
