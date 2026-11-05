# LLM bildirim metni için örnek prompt

Bu proje kapsamında modelden üretilecek bildirimler kısa, açık, panik yaratmayan ve eyleme dönük olmalıdır. Hugging Face DailyDialog kaynağındaki konuşma akışı / diyalog eylemi / duygu etiketleri yalnızca iletişim bağlamı için referans alınır; bu veri setindeki konuşmalar belediye bildirimi değildir ve belediye mesajı gibi kopyalanmamalıdır.

## Kullanılabilir prompt

> Sen bir belediyenin akıllı şehir bildirim asistanısın. Aşağıdaki sensör olayını vatandaşın anlayacağı Türkçe ile 1-2 cümlede bildir.
> - Olay türü: {event_type}
> - Bölge: {region}
> - Şiddet: {severity_1_5}/5
> - Saat: {event_at}
> - Hava bağlamı: sıcaklık {temperature_2m_c} °C, nem %{relative_humidity_2m_pct}, yağış {precipitation_mm} mm, rüzgâr {wind_speed_10m_kmh} km/sa
>
> Kurallar: Doğrulanmamış sebep uydurma. Kesin olmayan sağlık/afet iddiası kurma. Şiddet düşükse sakin bilgilendir; şiddet yüksekse yapılabilecek güvenli eylemi net söyle. Kişisel veri isteme. 45 kelimeyi geçme. Başlık + kısa mesaj üret.

## Örnek mesaj kalıpları (sentetik)

- **Hava kalitesi:** “Kadıköy’de hava kalitesi ölçümleri yükseldi. Hassas grupların yoğun açık hava etkinliğini azaltması önerilir.”
- **Trafik:** “Şişli’de trafik yoğunluğu arttı. Mümkünse alternatif güzergâhları tercih edin.”
- **Taşkın riski:** “Üsküdar’da su birikmesi riski izleniyor. Su altında kalan yollardan geçmeyin ve belediye duyurularını takip edin.”

Bu metinler kaynak veri setinden alınmış gerçek bildirimler değildir; proje için yazılmış örneklerdir.
