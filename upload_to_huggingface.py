import os
import json
from datasets import Dataset, Audio, Image
from huggingface_hub import HfApi
from dotenv import load_dotenv

def get_next_file_number():
    # uploaded_to_huggingface.txt'den son numarayı al
    if os.path.exists('uploaded_to_huggingface.txt'):
        with open('uploaded_to_huggingface.txt', 'r', encoding='utf-8') as f:
            uploaded_files = f.read().splitlines()
            if uploaded_files:
                # Son yüklenen dosyanın numarasını bul
                last_file = uploaded_files[-1]
                try:
                    # Dosya adından numarayı çıkar (0000001_processed_dataset.json)
                    last_number = int(os.path.basename(last_file).split('_')[0])
                    return last_number + 1
                except (ValueError, IndexError):
                    pass
    return 1

def upload_to_huggingface(json_path, repo_name, file_number):
    # .env dosyasından token'ı yükle
    load_dotenv()
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    
    if not hf_token:
        raise ValueError("HUGGINGFACE_TOKEN bulunamadı. Lütfen .env dosyasını kontrol edin.")

    # JSON dosyasını oku
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Veriyi Hugging Face formatına dönüştür
    dataset_dict = {
        'id': [],
        'audio': [],
        'transcription': [],
        'spectrogram': [],
        'mfcc': [],
        'tokens': [],
        'token_ids': []
    }

    for idx, item in enumerate(data):
        # Dosyaların varlığını kontrol et
        if not os.path.exists(item['audio_file']) or not os.path.exists(item['spectrogram']):
            print(f"Uyarı: Dosya bulunamadı, bu örnek atlanıyor: {item['audio_file']}")
            continue

        dataset_dict['id'].append(f"{idx:07d}")
        dataset_dict['audio'].append(item['audio_file'])
        dataset_dict['transcription'].append(item['transcription'])
        dataset_dict['spectrogram'].append(item['spectrogram'])
        dataset_dict['mfcc'].append(item['mfcc'])
        dataset_dict['tokens'].append(item['tokens'])
        dataset_dict['token_ids'].append(item['token_ids'])

    # Dataset oluştur
    dataset = Dataset.from_dict(dataset_dict)

    # Audio ve Image özelliklerini yapılandır
    dataset = dataset.cast_column('audio', Audio())
    dataset = dataset.cast_column('spectrogram', Image())

    # Hugging Face'e yükle
    try:
        dataset.push_to_hub(
            repo_name,
            token=hf_token,
            private=False
        )
        print(f"Veri seti başarıyla yüklendi: {repo_name}")
        
        # Yeni dosya adını oluştur
        new_json_filename = f"{file_number:07d}_processed_dataset.json"
        new_json_path = os.path.join(os.path.dirname(json_path), new_json_filename)
        
        # Dosyayı yeni adıyla kaydet
        os.rename(json_path, new_json_path)
        
        # Yüklenen dosyayı kaydet
        with open('uploaded_to_huggingface.txt', 'a', encoding='utf-8') as f:
            f.write(f"{new_json_path}\n")
            
    except Exception as e:
        print(f"Yükleme sırasında hata oluştu: {e}")

def clean_output_directory():
    """Output klasörünü temizler, alt klasörlerdeki tüm dosyaları siler"""
    output_dir = "output"
    subdirs = ['audio', 'json', 'spectrogram']
    
    try:
        for subdir in subdirs:
            dir_path = os.path.join(output_dir, subdir)
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        print(f"Silindi: {file_path}")
                    except Exception as e:
                        print(f"Hata: {file_path} silinirken sorun oluştu: {e}")
        print("Output klasörü temizlendi.")
    except Exception as e:
        print(f"Output klasörü temizlenirken hata oluştu: {e}")

if __name__ == "__main__":
    # JSON dosyalarını bul
    json_folder = os.path.join("output", "json")
    if not os.path.exists(json_folder):
        raise ValueError("JSON klasörü bulunamadı!")

    json_files = [f for f in os.listdir(json_folder) if f.endswith('_processed_dataset.json')]
    
    if not json_files:
        raise ValueError("İşlenmiş veri seti JSON dosyası bulunamadı!")

    # Bir sonraki dosya numarasını al
    next_file_number = get_next_file_number()
    
    upload_success = True  # Yükleme başarısını takip etmek için

    # Her JSON dosyası için
    for json_file in json_files:
        json_path = os.path.join(json_folder, json_file)
        
        # Daha önce yüklenip yüklenmediğini kontrol et
        if os.path.exists('uploaded_to_huggingface.txt'):
            with open('uploaded_to_huggingface.txt', 'r', encoding='utf-8') as f:
                uploaded_files = f.read().splitlines()
                if json_path in uploaded_files:
                    print(f"Bu dosya zaten yüklenmiş, atlanıyor: {json_path}")
                    continue

        # Repo adını oluştur
        repo_name = f"turkish-folk-songs-{next_file_number:07d}"
        
        print(f"Yükleniyor: {json_path} -> {repo_name}")
        try:
            upload_to_huggingface(json_path, repo_name, next_file_number)
            next_file_number += 1
        except Exception as e:
            print(f"Yükleme hatası: {e}")
            upload_success = False
            break

    # Tüm yüklemeler başarılı olduysa output klasörünü temizle
    if upload_success:
        print("Tüm yüklemeler başarıyla tamamlandı. Output klasörü temizleniyor...")
        clean_output_directory()
    else:
        print("Bazı yüklemeler başarısız oldu. Output klasörü temizlenmedi.")