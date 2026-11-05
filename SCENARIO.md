# Proje Senaryosu: Akıllı Şehir IoT Sensör Ağı ve LLM Maliyet Analizi

## 1. Proje Amacı
Bu proje, akıllı şehir altyapısındaki IoT sensörlerinden toplanan olay verilerinin işlenmesini, aciliyet durumlarına göre sınıflandırılmasını ve bu süreçte yapay zeka (LLM) bildirimlerinin yarattığı maliyet ve gecikme (latency) sürelerinin analiz edilmesini amaçlar.

## 2. Kapsam ve Senaryo Detayları
* **Sensör Ağı:** Şehrin farklı noktalarındaki çevresel ve trafik sensörlerinden gelen akış verileri.
* **Olay Yönetimi:** Sensör verilerinin kritiklik seviyelerine (Düşük, Orta, Yüksek, Kritik) göre filtrelenmesi.
* **LLM Entegrasyonu:** Farklı yapay zeka modelleri kullanılarak acil durumlarda üretilen bildirimlerin maliyet ve performans karşılaştırması.

## 3. Kullanılan Veri Setleri
* `sensors.csv`: Sensör cihaz bilgileri.
* `sensor_events.csv`: Sensörler tarafından üretilen olay kayıtları.
* `notifications.csv`: LLM çağrı logları ve maliyet metrikleri.
* `weather_hourly.csv`: Hava durumu bağlam verileri.