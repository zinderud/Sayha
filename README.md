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
```
çalıştırma
## 
```python youtube_splitter_tr.py "YOUTUBE_VIDEO_URL"


 ```
 json formatında çıktı olarak alma
 
 ```
 python output_Json.py
 ```
 
## Sorunlar
bazı linkler windowsta uzunluk hatasına sebeb veriyor.
Oromatik altyazılarda sorunlar mevcut o yüzden veri çekimi için
elle eklenmiş altyazıları kullanın. bunun için videoları youtube filtre özelliği altyazıyıyı secmek gerekiyor.

## Kalan aşamalar
1.Veri cekimleri youtube listeleri halinde yapmak
2. Veri Setini Hazırlama 
```
    {
        "audio_file": "001_bu_bir_örnek_cümledir.mp3",
        "transcription": "Bu bir örnek cümledir."
    }
```
şeklinde  düzenleme
3. Veri setinizi Hugging Face'e yükle