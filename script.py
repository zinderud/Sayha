import os
import subprocess
import sys

def run_youtube_splitter(youtube_url):
    """youtube_splitter_tr.py programını çalıştırır."""
    try:
        subprocess.run([sys.executable, "youtube_splitter_tr.py", youtube_url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Hata: youtube_splitter_tr.py çalıştırılırken bir sorun oluştu. Hata mesajı: {e}")
        sys.exit(1)

def run_output_json():
    """output_Json.py programını çalıştırır."""
    try:
        subprocess.run([sys.executable, "output_Json.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Hata: output_Json.py çalıştırılırken bir sorun oluştu. Hata mesajı: {e}")
        sys.exit(1)

def run_processed_dataset():
    """processed_dataset.py programını çalıştırır."""
    try:
        subprocess.run([sys.executable, "processed_dataset.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Hata: processed_dataset.py çalıştırılırken bir sorun oluştu. Hata mesajı: {e}")
        sys.exit(1)

def run_upload_to_huggingface():
    """upload_to_huggingface.py programını çalıştırır."""
    try:
        subprocess.run([sys.executable, "upload_to_huggingface.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Hata: upload_to_huggingface.py çalıştırılırken bir sorun oluştu. Hata mesajı: {e}")
        sys.exit(1)

def main(youtube_url):
    # Klasörleri oluştur
    os.makedirs("output/audio", exist_ok=True)
    os.makedirs("output/json", exist_ok=True)
    os.makedirs("output/spectrogram", exist_ok=True)
    
    try:
        # youtube_splitter_tr.py'yi çalıştır
        run_youtube_splitter(youtube_url)
        
        # output_Json.py'yi çalıştır
        run_output_json()
        
        # processed_dataset.py'yi çalıştır
        run_processed_dataset()
        
        # upload_to_huggingface.py'yi çalıştır
        run_upload_to_huggingface()
        
        print("İşlem tamamlandı! Tüm dosyalar Hugging Face'e yüklendi.")
    except Exception as e:
        print(f"Hata: İşlem sırasında bir sorun oluştu. Hata mesajı: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python script.py <youtube_link>")
    else:
        youtube_url = sys.argv[1]
        main(youtube_url)