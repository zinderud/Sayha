import os
import json
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from transformers import AutoTokenizer

# Giriş ve çıkış klasörleri
input_folder = "output"
output_folder = "processed_output"

# Tokenizer'ı yükle (örneğin, BERT tokenizer)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Çıkış klasörünü oluştur
os.makedirs(output_folder, exist_ok=True)

# Veri setini tutacak liste
dataset = []

# Video kimliğini al (örneğin, klasör adından)
video_id = os.path.basename(os.path.normpath(input_folder))

# Klasörleri ve dosyaları tarama
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.endswith(".mp3"):
            # Dosya yolunu al
            audio_path = os.path.join(root, file)
            
            # Dosya adından metni çıkar
            transcription = os.path.splitext(file)[0]  # Uzantıyı kaldır
            transcription = "_".join(transcription.split("_")[1:])  # İlk kısmı (numara) kaldır
            transcription = transcription.replace("_", " ")  # Alt çizgileri boşlukla değiştir
            
            try:
                # Ses dosyasını yükle
                y, sr = librosa.load(audio_path, sr=None)
                
                # Spektrogram oluştur
                spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
                
                # Spektrogramı görselleştir ve kaydet
                plt.figure(figsize=(10, 4))
                librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max), y_axis='mel', x_axis='time')
                plt.colorbar(format='%+2.0f dB')
                plt.title('Mel Spectrogram')
                
                # Mevcut spektrogram dosyalarını kontrol et ve bir sonraki sıradaki numarayı belirle
                existing_spectrogram_files = [f for f in os.listdir(output_folder) if f.endswith("_spectrogram.png")]
                next_file_number = len(existing_spectrogram_files) + 1
                
                # Dosya adındaki numarayı al (örneğin, "002" gibi)
                file_number = file.split("_")[0]  # Dosya adındaki ilk kısmı al (örneğin, "002")
                
                # Dosya ismini oluştur (sıralı numara ile dosya adındaki numarayı eşleştir)
                spectrogram_filename = f"{next_file_number:07d}_{file_number}_{'_'.join(file.split('_')[1:])}_spectrogram.png"
                spectrogram_path = os.path.join(output_folder, spectrogram_filename)
                plt.savefig(spectrogram_path)
                plt.close()
                
                # MFCC özelliklerini çıkar
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                
                # Metni tokenize et
                tokens = tokenizer.tokenize(transcription)
                token_ids = tokenizer.encode(transcription)
                
                # Veri setine ekle
                dataset.append({
                    "audio_file": audio_path,
                    "transcription": transcription,
                    "spectrogram": spectrogram_path,
                    "mfcc": mfcc.tolist(),  # Numpy array'i listeye çevir
                    "tokens": tokens,
                    "token_ids": token_ids
                })
            except Exception as e:
                print(f"Hata: {audio_path} işlenirken bir sorun oluştu. Hata mesajı: {e}")

# JSON dosyası için sıralı bir isim oluştur (video kimliği eklenmeden)
existing_json_files = [f for f in os.listdir(output_folder) if f.endswith(".json")]
next_file_number = len(existing_json_files) + 1
output_json_filename = f"{next_file_number:07d}_processed_dataset.json"
output_json_path = os.path.join(output_folder, output_json_filename)

# Veri setini JSON dosyası olarak kaydet
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

print(f"Toplam {len(dataset)} ses dosyası işlendi ve çıktılar '{output_folder}' klasörüne kaydedildi.")