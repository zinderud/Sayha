import os
import subprocess
import glob

def get_next_file_number(output_folder):
    """processed_output klasöründeki dosyalara bakarak bir sonraki dosya numarasını belirler."""
    existing_files = glob.glob(os.path.join(output_folder, "*.json"))
    if not existing_files:
        return 1
    max_num = 0
    for file in existing_files:
        file_name = os.path.basename(file)
        file_num = int(file_name.split("_")[0])
        if file_num > max_num:
            max_num = file_num
    return max_num + 1

def run_youtube_splitter(youtube_url):
    """youtube_splitter_tr.py programını çalıştırır."""
    subprocess.run(["python", "youtube_splitter_tr.py", youtube_url], check=True)

def run_processed_dataset():
    """processed_dataset.py programını çalıştırır."""
    subprocess.run(["python", "processed_dataset.py"], check=True)

def main(youtube_url):
    output_folder = "processed_output"
    os.makedirs(output_folder, exist_ok=True)
    
    # youtube_splitter_tr.py'yi çalıştır
    run_youtube_splitter(youtube_url)
    
    # processed_dataset.py'yi çalıştır
    run_processed_dataset()
    
    print(f"İşlem tamamlandı! Dosyalar '{output_folder}' klasörüne kaydedildi.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Kullanım: python script.py <youtube_link>")
    else:
        youtube_url = sys.argv[1]
        main(youtube_url)