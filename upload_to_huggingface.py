import os
import json
from datasets import Dataset, Audio, Image
from huggingface_hub import HfApi
from dotenv import load_dotenv

def upload_to_huggingface(json_path, repo_name):
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
        
        # Yüklenen dosyayı kaydet
        with open('uploaded_to_huggingface.txt', 'a', encoding='utf-8') as f:
            f.write(f"{json_path}\n")
            
    except Exception as e:
        print(f"Yükleme sırasında hata oluştu: {e}")

if __name__ == "__main__":
    # JSON dosyalarını bul
    json_folder = os.path.join("output", "json")
    if not os.path.exists(json_folder):
        raise ValueError("JSON klasörü bulunamadı!")

    json_files = [f for f in os.listdir(json_folder) if f.endswith('_processed_dataset.json')]
    
    if not json_files:
        raise ValueError("İşlenmiş veri seti JSON dosyası bulunamadı!")

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
        base_name = os.path.splitext(json_file)[0]
        repo_name = f"turkish-folk-songs-{base_name}"
        
        print(f"Yükleniyor: {json_path} -> {repo_name}")
        upload_to_huggingface(json_path, repo_name)