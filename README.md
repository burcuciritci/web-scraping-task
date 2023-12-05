# web-scraping-task

Bu Python script'i, Turkish Network Times web sitesinden veri çekmek ve kaydetmek için tasarlanmıştır. 'Gundem' kategorisinden haber içeriklerini çeker, ilgili bilgileri çıkarır ve bunları bir MongoDB veritabanında depolar. Ayrıca kelime yoğunluk istatistikleri üretir ve en sık kullanılan ilk 10 kelimenin bar grafiğini oluşturur.

## Önkoşullar

Script'i çalıştırmadan önce aşağıdakilerin yüklü olduğundan emin olun:

- Python 3
- MongoDB
- Gerekli Python paketleri (kurmak için `pip install -r requirements.txt`)

## Kullanım

1. Clone Repository:

    ```bash
    git clone https://github.com/burcuciritci/web-scraping-task.git
    ```

2. Kullanılan kütüphanelerin kurulumu:

    ```bash
    pip install -r requirements.txt
    ```

3. MongoDB:

    Script içindeki `mongo_uri` değişkenini kendi MongoDB bağlantı dizenizle güncelleyin.


## Script Yapısı

- `main.py`: Veri çekme, depolama ve analiz için fonksiyonlar içeren ana script dosyası.
- `requirements.txt`: Script için gereken Python paketlerinin listesi.
- `logs/logs.log`: Script çalıştırma detaylarını kaydetmek için kullanılan log dosyası.

## Ek Bilgiler

- Script, web sayfalarını paralel olarak çekmek için threadingpool kullanır.
- Veri çekme sürecinde oluşabilecek hataları yönetmek için hata işleme mekanizmaları uygulanmıştır.
- Script içindeki `print_grouped_data_by_update_date` fonksiyonu, MongoDB koleksiyonundaki 'update_date' alanına göre gruplanmış verileri yazdırmak için kullanılabilir.
