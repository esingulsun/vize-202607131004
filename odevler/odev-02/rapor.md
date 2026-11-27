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
Soru 4a'da `robots` ile `missions` tablosunu INNER JOIN ile birleştirip `SUM(r.battery_level)` aldığımda toplam **262'den 700'e** çıktı (yaklaşık 2,7 kat). Nedeni, birden fazla görevi olan her robotun satırının görev sayısı kadar tekrarlanmasıdır (fan-out): Kartal-01, Kartal-03 ve Atlas-01 **3'er kez**, Mars-02 ve Mars-01 **2'şer kez** sayıldı, bataryaları da o kadar kez toplandı.

4b'de `WHERE id IN (SELECT DISTINCT robot_id FROM missions)` ile JOIN kullanmadan her robotu yalnızca bir kez saydım ve doğru toplam olan **262**'yi buldum.

Gerçek bir raporda bu hata, filonun toplam şarjını gerçekte olduğundan 2,7 kat fazla gösterir; filo sorumlusu şarj ve bakım planını bu şişkin sayıya göre yapar ve yanlış karar verir.

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
