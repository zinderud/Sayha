import os
import json

# Output klasörünün yolu
output_folder = "output"

# Veri setini tutacak liste
dataset = []

# Klasörleri ve dosyaları tarama
for root, dirs, files in os.walk(output_folder):
    for file in files:
        if file.endswith(".mp3"):
            # Dosya yolunu al
            audio_file = os.path.join(root, file)
            
            # Dosya adından metni çıkar (örneğin, "003_kara_haber_var.mp3" -> "kara haber var")
            transcription = os.path.splitext(file)[0]  # Uzantıyı kaldır
            transcription = "_".join(transcription.split("_")[1:])  # İlk kısmı (numara) kaldır
            transcription = transcription.replace("_", " ")  # Alt çizgileri boşlukla değiştir
            
            # Veri setine ekle
            dataset.append({
                "audio_file": audio_file,
                "transcription": transcription
            })

# Veri setini JSON dosyası olarak kaydet
with open("audio_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

print(f"Toplam {len(dataset)} ses dosyası bulundu ve veri seti oluşturuldu.")