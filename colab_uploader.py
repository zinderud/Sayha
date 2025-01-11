import os
import sys
from google.colab import drive
import subprocess

# Google Drive'ı bağla
drive.mount('/content/drive')

# Gerekli kütüphaneleri yükle
!pip install yt-dlp pydub webvtt-py datasets transformers librosa huggingface_hub python-dotenv

# Hugging Face token'ını ayarla
import os
os.environ['HUGGINGFACE_TOKEN'] = 'your_token_here'  # Token'ınızı buraya yazın

# Gerekli klasörleri oluştur
!mkdir -p /content/output/audio
!mkdir -p /content/output/json
!mkdir -p /content/output/spectrogram

# GitHub'dan dosyaları indir
!wget https://raw.githubusercontent.com/your_username/your_repo/main/youtube_splitter_tr.py
!wget https://raw.githubusercontent.com/your_username/your_repo/main/processed_dataset.py
!wget https://raw.githubusercontent.com/your_username/your_repo/main/upload_to_huggingface.py

def process_youtube_video(youtube_url):
    try:
        # YouTube videosunu işle
        !python youtube_splitter_tr.py {youtube_url}
        
        # Veri setini işle
        !python processed_dataset.py
        
        # Hugging Face'e yükle
        !python upload_to_huggingface.py
        
        print("İşlem başarıyla tamamlandı!")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        # Geçici dosyaları temizle
        !rm -rf /content/output/audio/*
        !rm -rf /content/output/json/*
        !rm -rf /content/output/spectrogram/*

# Kullanım örneği
youtube_url = "https://www.youtube.com/watch?v=your_video_id"
process_youtube_video(youtube_url) 