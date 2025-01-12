# @title YouTube'dan Hugging Face'e Veri Seti Yükleme
import os
import subprocess
from getpass import getpass

# Hugging Face token'ını al
def set_hf_token():
    token = getpass('Hugging Face Token: ')
    os.environ['HUGGINGFACE_TOKEN'] = token

# Gerekli kütüphaneleri yükle
def install_dependencies():
    packages = [
        'yt-dlp',
        'pydub',
        'webvtt-py',
        'datasets',
        'transformers',
        'librosa',
        'huggingface_hub',
        'python-dotenv'
    ]
    for package in packages:
        subprocess.run(['pip', 'install', package])

# Klasör yapısını oluştur
def create_directories():
    dirs = [
        '/content/output/audio',
        '/content/output/json',
        '/content/output/spectrogram'
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

# İşlem scriptlerini indir
def download_scripts():
    scripts = {
        'youtube_splitter_tr.py': 'https://raw.githubusercontent.com/your_username/your_repo/main/youtube_splitter_tr.py',
        'processed_dataset.py': 'https://raw.githubusercontent.com/your_username/your_repo/main/processed_dataset.py',
        'upload_to_huggingface.py': 'https://raw.githubusercontent.com/your_username/your_repo/main/upload_to_huggingface.py'
    }
    for filename, url in scripts.items():
        subprocess.run(['wget', '-O', filename, url])

# Video işleme fonksiyonu
def process_youtube_video(youtube_url):
    try:
        # YouTube videosunu işle
        subprocess.run(['python', 'youtube_splitter_tr.py', youtube_url], check=True)
        
        # Veri setini işle
        subprocess.run(['python', 'processed_dataset.py'], check=True)
        
        # Hugging Face'e yükle
        subprocess.run(['python', 'upload_to_huggingface.py'], check=True)
        
        print("İşlem başarıyla tamamlandı!")
        
    except subprocess.CalledProcessError as e:
        print(f"Hata oluştu: {e}")
    finally:
        # Geçici dosyaları temizle
        for folder in ['audio', 'json', 'spectrogram']:
            path = f'/content/output/{folder}/'
            subprocess.run(['rm', '-rf', path + '*'])

def main():
    print("YouTube'dan Hugging Face'e Veri Seti Yükleme Aracı")
    print("-" * 50)
    
    # Kurulum adımları
    print("1. Bağımlılıklar yükleniyor...")
    install_dependencies()
    
    print("\n2. Klasörler oluşturuluyor...")
    create_directories()
    
    print("\n3. Scriptler indiriliyor...")
    download_scripts()
    
    print("\n4. Hugging Face token'ı ayarlanıyor...")
    set_hf_token()
    
    # YouTube URL'sini al
    print("\n5. YouTube video işleme")
    youtube_url = input("YouTube URL'sini girin: ")
    
    if youtube_url:
        process_youtube_video(youtube_url)
    else:
        print("Geçerli bir YouTube URL'si girmelisiniz!")

if __name__ == "__main__":
    main() 