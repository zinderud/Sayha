import os
import re
import sys
from pydub import AudioSegment
import webvtt
import yt_dlp

def sanitize_filename(text):
    """Dosya isimlerindeki geçersiz karakterleri temizler."""
    # Yeni satır, soru işareti, iki nokta üst üste gibi karakterleri kaldır
    text = re.sub(r'[\n\r?*:|"<>/\\]', "", text)
    # Boşlukları alt çizgi ile değiştir
    text = text.replace(" ", "_")
    # Birden fazla alt çizgiyi tek alt çizgiye indir
    text = re.sub(r'_+', '_', text)
    # Baştaki ve sondaki boşlukları ve alt çizgileri kaldır
    text = text.strip('_')
    return text

def download_video_and_subtitles(url):
    """YouTube'dan video ve altyazı indirir."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'writesubtitles': True,
        'writeautomaticsub': True,  # Otomatik altyazıları etkinleştir
        'subtitleslangs': ['tr'],   # Önce Türkçe altyazıyı dene
        'subtitlesformat': 'vtt',   # VTT formatında altyazı indir
        'outtmpl': 'video.%(ext)s', # Ses dosyasının adı
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', 'video')

        # İndirilen ses dosyasının adını bul
        audio_file = None
        for file in os.listdir():
            if file.endswith(".mp3") or file.endswith(".webm") or file.endswith(".m4a"):
                audio_file = file
                break

        # İndirilen altyazı dosyasını bul
        subtitle_file = None
        for file in os.listdir():
            if file.endswith(".vtt") and "tr" in file:  # Türkçe altyazı dosyasını ara
                subtitle_file = file
                break

        # Eğer Türkçe altyazı yoksa, otomatik altyazıyı Türkçe'ye çevir
        if not subtitle_file:
            print("Türkçe altyazı bulunamadı. Otomatik altyazı Türkçe'ye çevriliyor...")
            ydl_opts_auto = {
                'format': 'bestaudio/best',
                'writeautomaticsub': True,
                'subtitleslangs': ['tr'],  # Otomatik altyazıyı Türkçe'ye çevir
                'subtitlesformat': 'vtt',  # VTT formatında altyazı indir
                'outtmpl': 'video.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts_auto) as ydl_auto:
                ydl_auto.download([url])
            
            # Otomatik altyazı dosyasını bul
            for file in os.listdir():
                if file.endswith(".vtt") and "tr" in file:
                    subtitle_file = file
                    break

        if not audio_file:
            print("Hata: Ses dosyası bulunamadı!")
        elif not subtitle_file:
            print("Hata: Türkçe altyazı dosyası bulunamadı!")
        else:
            print(f"Ses dosyası bulundu: {audio_file}")
            print(f"Altyazı dosyası bulundu: {subtitle_file}")

    return audio_file, subtitle_file, video_title

def split_audio_by_subtitles(audio_file, subtitle_file, video_title):
    """Ses dosyasını altyazı aralıklarına göre böler ve kaydeder."""
    if not subtitle_file or not os.path.exists(subtitle_file):
        print("Hata: Altyazı dosyası bulunamadı. İşlem iptal edildi.")
        return

    if not audio_file or not os.path.exists(audio_file):
        print("Hata: Ses dosyası bulunamadı. İşlem iptal edildi.")
        return

    # WebVTT formatındaki altyazıyı oku
    subs = webvtt.read(subtitle_file)
    audio = AudioSegment.from_file(audio_file)

    output_folder = os.path.join("output", sanitize_filename(video_title))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, sub in enumerate(subs):
        start_time = int(sub.start_in_seconds * 1000)  # Saniyeden milisaniyeye çevir
        end_time = int(sub.end_in_seconds * 1000)      # Saniyeden milisaniyeye çevir

        segment = audio[start_time:end_time]
        filename = f"{i+1:03d}_{sanitize_filename(sub.text)}.mp3"
        output_path = os.path.join(output_folder, filename)

        print(f"Exporting: {output_path}")
        segment.export(output_path, format="mp3")

def delete_temp_files(audio_file, subtitle_file):
    """Geçici dosyaları (video ve altyazı) siler."""
    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)
        print(f"Geçici ses dosyası silindi: {audio_file}")

    if subtitle_file and os.path.exists(subtitle_file):
        os.remove(subtitle_file)
        print(f"Geçici altyazı dosyası silindi: {subtitle_file}")

def main():
    if len(sys.argv) != 2:
        print("Kullanım: python script.py <youtube_link>")
        return

    youtube_url = sys.argv[1]
    print(f"İndiriliyor: {youtube_url}")

    # Video ve altyazıyı indir
    audio_file, subtitle_file, video_title = download_video_and_subtitles(youtube_url)

    # Ses dosyasını altyazı aralıklarına göre böl
    split_audio_by_subtitles(audio_file, subtitle_file, video_title)

    # Geçici dosyaları sil
    delete_temp_files(audio_file, subtitle_file)

    print("İşlem tamamlandı!")

if __name__ == "__main__":
    main()