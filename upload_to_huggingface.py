import os
import json
from datasets import Dataset, Audio, Image  # Audio ve Image sınıflarını içe aktar
from huggingface_hub import HfApi, login


# Hugging Face token'ınızı buraya ekleyin
HUGGINGFACE_TOKEN = "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1"
# Hugging Face'deki veri setinizin adı
DATASET_NAME = "sayha"

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

def upload_to_huggingface(data, json_file_name, output_folder):
    """Verileri Hugging Face veri setine yükler."""
    # Verileri Hugging Face Dataset formatına dönüştür
    dataset_dict = {
        "audio": [],
        "transcription": [],
        "spectrogram": [],
        "mfcc": [],
        "tokens": [],
        "token_ids": [],
    }

    for item in data:
        # Ses dosyasının yolunu oluştur (output/video_id/...)
        audio_file = os.path.join("output", os.path.basename(os.path.dirname(item["audio_file"])), os.path.basename(item["audio_file"]))
        
        # Ses dosyasını ekle
        if audio_file and os.path.exists(audio_file):
            dataset_dict["audio"].append(audio_file)
        else:
            print(f"Hata: {audio_file} dosyası bulunamadı!")
            dataset_dict["audio"].append(None)

        # Transkripsiyon ve diğer bilgileri ekle
        dataset_dict["transcription"].append(item.get("transcription", ""))
        dataset_dict["mfcc"].append(item.get("mfcc", []))
        dataset_dict["tokens"].append(item.get("tokens", []))
        dataset_dict["token_ids"].append(item.get("token_ids", []))

        # Spektrogram dosyasının yolunu oluştur (processed_output/...)
        spectrogram_file = os.path.join(output_folder, os.path.basename(item["spectrogram"]))
        
        # Spektrogram dosyasını ekle
        if spectrogram_file and os.path.exists(spectrogram_file):
            dataset_dict["spectrogram"].append(spectrogram_file)
        else:
            print(f"Hata: {spectrogram_file} dosyası bulunamadı!")
            dataset_dict["spectrogram"].append(None)

    # Dataset oluştur
    dataset = Dataset.from_dict(dataset_dict)

    # Ses dosyalarını Audio formatına dönüştür
    try:
        dataset = dataset.cast_column("audio", Audio())
    except Exception as e:
        print(f"Hata: Ses dosyaları Audio formatına dönüştürülürken bir sorun oluştu. Hata mesajı: {e}")
        return

    # Spektrogramları Image formatına dönüştür
    try:
        dataset = dataset.cast_column("spectrogram", Image())
    except Exception as e:
        print(f"Hata: Spektrogramlar Image formatına dönüştürülürken bir sorun oluştu. Hata mesajı: {e}")
        return

    # Hugging Face'e yükle
    try:
        dataset.push_to_hub(
            repo_id=DATASET_NAME,
            split=json_file_name.replace(".json", ""),  # Veri seti bölümü (split)
        )
        print(f"{json_file_name} ve ilgili dosyalar Hugging Face'e başarıyla yüklendi!")
    except Exception as e:
        print(f"Hata: Veriler Hugging Face'e yüklenirken bir sorun oluştu. Hata mesajı: {e}")

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
        upload_to_huggingface(data, json_file, output_folder)
        
        # Dosyayı yüklenenler listesine ekle
        mark_file_as_uploaded(json_file)

if __name__ == "__main__":
    main()