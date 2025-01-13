import os
import json
import shutil
from datasets import Dataset, Audio, Image, concatenate_datasets, load_dataset
from huggingface_hub import HfApi
from dotenv import load_dotenv

def upload_to_huggingface(json_path, repo_name=None, video_id=None):
    """
    Veri setini Hugging Face'e yükler.
    
    Args:
        json_path: İşlenmiş veri setinin JSON dosya yolu
        repo_name: Hugging Face repository adı (opsiyonel)
        video_id: Video ID (opsiyonel)
    """
    load_dotenv()
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    
    # Eğer repo_name parametre olarak verilmemişse, .env'den al
    if repo_name is None:
        repo_name = os.getenv('HUGGINGFACE_REPO', 'sadece/sayha')
    
    if not hf_token:
        raise ValueError("HUGGINGFACE_TOKEN bulunamadı. Lütfen .env dosyasını kontrol edin.")
    
    if not repo_name:
        raise ValueError("Repository adı belirtilmemiş!")

    try:
        # Repository'yi kontrol et veya oluştur
        api = HfApi()
        try:
            api.repo_exists(repo_id=repo_name, repo_type="dataset")
        except Exception:
            api.create_repo(repo_id=repo_name, repo_type="dataset", private=False)
            print(f"Yeni repository oluşturuldu: {repo_name}")

        # JSON dosyasını oku
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Yeni veriyi Hugging Face formatına dönüştür
        new_dataset_dict = {
            'id': [],
            'audio': [],
            'transcription': [],
            'spectrogram': [],
            'mfcc': [],
            'tokens': [],
            'token_ids': []
        }

        for idx, item in enumerate(data):
            if not os.path.exists(item['audio_file']) or not os.path.exists(item['spectrogram']):
                print(f"Uyarı: Dosya bulunamadı, bu örnek atlanıyor: {item['audio_file']}")
                continue

            new_dataset_dict['id'].append(f"{video_id}_{idx:03d}" if video_id else f"sample_{idx:03d}")
            new_dataset_dict['audio'].append(item['audio_file'])
            new_dataset_dict['transcription'].append(item['transcription'])
            new_dataset_dict['spectrogram'].append(item['spectrogram'])
            new_dataset_dict['mfcc'].append(item['mfcc'])
            new_dataset_dict['tokens'].append(item['tokens'])
            new_dataset_dict['token_ids'].append(item['token_ids'])

        # Yeni veriyi dataset'e dönüştür
        new_dataset = Dataset.from_dict(new_dataset_dict)
        new_dataset = new_dataset.cast_column('audio', Audio())
        new_dataset = new_dataset.cast_column('spectrogram', Image())

        # Geçici klasör oluştur
        temp_dir = os.path.join("temp_dataset", "data")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # Repository'deki mevcut dosyaları listele
            repo_files = api.list_repo_files(repo_id=repo_name, repo_type="dataset")
            # Mevcut parquet dosyalarını say
            parquet_files = [f for f in repo_files if f.startswith('data/train-') and f.endswith('.parquet')]
            if parquet_files:
                parquet_count = max([int(f.split('-')[1].split('-')[0]) for f in parquet_files]) + 1
            else:
                parquet_count = 0
        except Exception as e:
            print(f"Repository dosyaları listelenirken hata oluştu: {e}")
            parquet_count = 0

        print(f"Yeni parquet dosyası numarası: {parquet_count}")

        # Dataset'i parquet formatında kaydet
        parquet_filename = f"train-{parquet_count:05d}-of-{parquet_count+1:05d}.parquet"
        new_dataset.to_parquet(os.path.join(temp_dir, parquet_filename))

        print(f"Dataset parquet formatında kaydedildi: {parquet_filename}")

        # Hugging Face'e yükle
        api.upload_folder(
            folder_path=os.path.join("temp_dataset", "data"),
            repo_id=repo_name,
            repo_type="dataset",
            path_in_repo="data",
            token=hf_token
        )
        print(f"Veri seti başarıyla güncellendi: {repo_name}")
        
        # Geçici klasörü temizle
        if os.path.exists("temp_dataset"):
            shutil.rmtree("temp_dataset")
        
        # Yüklenen dosyayı kaydet
        with open('uploaded_to_huggingface.txt', 'a', encoding='utf-8') as f:
            f.write(f"{json_path}\n")
            
    except Exception as e:
        print(f"Yükleme sırasında hata oluştu: {e}")
        if os.path.exists("temp_dataset"):
            shutil.rmtree("temp_dataset")
        raise

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

def get_video_id_from_filename(filename):
    """JSON dosya adından video_id'yi çıkarır"""
    return filename.split('_processed_dataset.json')[0]

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
        video_id = json_file.split('_processed_dataset.json')[0]
        
        print(f"Yükleniyor: {json_path}")
        upload_to_huggingface(json_path, video_id=video_id)