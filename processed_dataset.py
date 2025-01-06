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
                spectrogram_path = os.path.join(output_folder, f"{file}_spectrogram.png")
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

# Veri setini JSON dosyası olarak kaydet
output_json_path = os.path.join(output_folder, "processed_dataset.json")
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

print(f"Toplam {len(dataset)} ses dosyası işlendi ve çıktılar '{output_folder}' klasörüne kaydedildi.")