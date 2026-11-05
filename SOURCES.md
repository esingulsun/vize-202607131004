# Kaynak notları

1. Kaggle — Beijing Multi-Site Air-Quality Data Set: https://www.kaggle.com/datasets/sid321axn/beijing-multisite-airquality-data-set
   - Açıklamaya göre 12 ulusal hava kalitesi istasyonunda saatlik kirletici ölçümleri; 1 Mart 2013–28 Şubat 2017; meteoroloji alanları da mevcut.
   - Coğrafya Pekin'dir. İstanbul belediye verisi olarak etiketlenmemelidir.

2. Open-Meteo — Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api
   - `/v1/archive` arşiv uç noktası, koordinat ve tarih aralığı ile saatlik hava değişkenleri sağlayabilir.
   - Bu paket `temperature_2m`, `relative_humidity_2m`, `precipitation`, `wind_speed_10m` alanlarını ister.

3. Hugging Face — DailyDialog: https://huggingface.co/datasets/anezatra/dailydialog
   - Çok turlu gündelik diyaloglar; `dialog`, `act`, `emotion` alanları. Yalnızca diyalog tonu/akışı için referans. Doğrudan belediye uyarısı olarak kullanılmaz.

4. Kaggle — DS2OS traffic traces: https://www.kaggle.com/datasets/francoisxa/ds2ostraffictraces
   - IoT ortamında dört simüle saha ve farklı sensör/cihaz türlerinden uygulama katmanı izleri. IoT olay ağı tasarımına yardımcı bir referanstır; belediye bildirimi verisi değildir.
