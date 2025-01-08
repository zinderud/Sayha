# Sayha
youtube videolarını indirir, alt yazılarına göre video_ismi örnek "Ahmet'e gelen dürüm" ---- ahmet-e_gelen_durum.mp3 olarak parçalar.



## Amac
Oluşturulcak Türkce dil modeli için kaynak oluşturmak.

## Kurulum:
ffmpeg'i sisteminize kurmanız gerekiyor. Kurulum için:

Windows: FFmpeg'i [indirin](https://ffmpeg.org/download.html) ve PATH'e ekleyin.

```
pip install yt-dlp pydub pysrt
pip install webvtt-py
pip install librosa matplotlib transformers
pip install soundfile audioread
pip install datasets huggingface_hub

```
çalıştırma
## 
```
python youtube_splitter_tr.py "YOUTUBE_VIDEO_URL"
 ```
 json formatında çıktı olarak alma
 
 ```
 python output_Json.py
 ```
 uploaded hugenface
  ```
 python upload_to_huggingface.py

 ```
## Sorunlar
bazı linkler windowsta uzunluk hatasına sebeb veriyor.
Oromatik altyazılarda sorunlar mevcut o yüzden veri çekimi için
elle eklenmiş altyazıları kullanın. bunun için videoları youtube filtre özelliği altyazıyıyı secmek gerekiyor.



# Çıktı Klasörü Yapısı
İşlem tamamlandıktan sonra, processed_output klasörü şu şekilde olacak:

```
processed_output/
├── 001_bir_örnek_cümle.mp3_spectrogram.png
├── 002_baska_bir_cümle.mp3_spectrogram.png
├── 003_kara_haber_var.mp3_spectrogram.png
├── 001_farklı_bir_cümle.mp3_spectrogram.png
├── 002_başka_örnek.mp3_spectrogram.png
└── processed_dataset.json
```
Spektrogram Görselleri: Her bir MP3 dosyası için spektrogram görseli.
processed_dataset.json: Tüm ses dosyalarının işlenmiş verilerini içeren JSON dosyası.
Spektrogram veya MFCC özelliklerini bir sinir ağına girdi olarak verebilirsiniz.

Tokenize edilmiş metinleri, metin üretme veya dil modeli eğitimi için kullanabilirsiniz.

## Kalan aşamalar
Bir ai agent ile otomatik olarak veri ekleme yapmak