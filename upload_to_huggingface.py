import os
import json
from datasets import Dataset
from huggingface_hub import HfApi, login

# Hugging Face token'ınızı buraya ekleyin
HUGGINGFACE_TOKEN = "your_huggingface_token"
# Hugging Face'deki veri setinizin adı
DATASET_NAME = "your_huggingface_dataset_name"

# Yüklenen dosyaların listesini tutacak dosya
UPLOADED_FILES_LOG = "uploaded_to_huggingface.txt"

# Hugging Face'e giriş yap
login(token=HUGGINGFACE_TOKEN)

def get_uploaded_files():
    """Yüklenen dosyaların listesini döndürür."""
    if not os.path.exists(UPLOADED_FILES_LOG):
        return set()
    with open(UPLOADED_FILES_LOG, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

def mark_file_as_uploaded(file_name):
    """Dosyayı yüklenenler listesine ekler."""
    with open(UPLOADED_FILES_LOG, "a", encoding="utf-8") as f:
        f.write(file_name + "\n")

def get_new_json_files(output_folder):
    """processed_output klasöründeki yeni (yüklenmemiş) JSON dosyalarını bulur."""
    uploaded_files = get_uploaded_files()
    json_files = [f for f in os.listdir(output_folder) if f.endswith(".json")]
    new_files = [f for f in json_files if f not in uploaded_files]
    return new_files

def load_data_from_json(json_file):
    """JSON dosyasındaki verileri yükler."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def upload_to_huggingface(data):
    """Verileri Hugging Face veri setine yükler."""
    # Verileri Hugging Face Dataset formatına dönüştür
    dataset = Dataset.from_list(data)
    
    # Hugging Face API'sini kullanarak veri setini güncelle
    api = HfApi()
    api.upload_file(
        path_or_fileobj=dataset.to_json(),
        path_in_repo="data.json",  # Veri setindeki dosya adı
        repo_id=DATASET_NAME,
        repo_type="dataset",
    )
    print("Veriler Hugging Face'e başarıyla yüklendi!")

def main():
    output_folder = "processed_output"
    
    # Yeni (yüklenmemiş) JSON dosyalarını bul
    new_json_files = get_new_json_files(output_folder)
    if not new_json_files:
        print("Yeni veri bulunamadı.")
        return
    
    for json_file in new_json_files:
        json_path = os.path.join(output_folder, json_file)
        
        # JSON dosyasındaki verileri yükle
        data = load_data_from_json(json_path)
        
        # Verileri Hugging Face'e yükle
        upload_to_huggingface(data)
        
        # Dosyayı yüklenenler listesine ekle
        mark_file_as_uploaded(json_file)
        print(f"{json_file} dosyası Hugging Face'e yüklendi ve işaretlendi.")

if __name__ == "__main__":
    main()