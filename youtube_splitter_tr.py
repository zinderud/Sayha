import os
import re
import sys
from pydub import AudioSegment
import webvtt
import yt_dlp

def sanitize_filename(text):
    """Dosya isimlerindeki geçersiz karakterleri temizler."""
    text = re.sub(r'[\n\r?*:|"<>/\\]', "", text)
    text = text.replace(" ", "_")
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    return text

def extract_video_id(url):
    """YouTube URL'sinden video kimliğini çıkarır."""
    video_id_match = re.search(r'(?<=v=)[^&#]+', url)
    video_id = video_id_match.group(0) if video_id_match else None
    return video_id

def check_if_video_downloaded(video_id):
    """Video kimliğinin daha önce indirilip indirilmediğini kontrol eder."""
    if not os.path.exists("downloaded_videos.txt"):
        return False  # Dosya yoksa, video indirilmemiş demektir.
    
    with open("downloaded_videos.txt", "r") as file:
        downloaded_videos = file.read().splitlines()
        return video_id in downloaded_videos

def mark_video_as_downloaded(video_id):
    """Video kimliğini indirilenler listesine ekler."""
    with open("downloaded_videos.txt", "a") as file:
        file.write(video_id + "\n")

def download_video_and_subtitles(url):
    """YouTube'dan video ve altyazı indirir."""
    ydl_opts = {
        'format': 'bestaudio[language=tr]/bestaudio/best',
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['tr'],
        'subtitlesformat': 'vtt',
        'outtmpl': 'video.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', 'video')

        audio_file = None
        for file in os.listdir():
            if file.endswith(".mp3") or file.endswith(".webm") or file.endswith(".m4a"):
                audio_file = file
                break

        subtitle_file = None
        for file in os.listdir():
            if file.endswith(".vtt") and "tr" in file:
                subtitle_file = file
                break

        if not subtitle_file:
            print("Türkçe altyazı bulunamadı. Otomatik altyazı Türkçe'ye çevriliyor...")
            ydl_opts_auto = {
                'format': 'bestaudio/best',
                'writeautomaticsub': True,
                'subtitleslangs': ['tr'],
                'subtitlesformat': 'vtt',
                'outtmpl': 'video.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts_auto) as ydl_auto:
                ydl_auto.download([url])
            
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

def clean_filename(filename):
    """Dosya adındaki geçersiz karakterleri temizler"""
    # Yeni satır karakterlerini boşlukla değiştir
    filename = filename.replace('\n', ' ')
    
    # Windows'da dosya adında kullanılamayan karakterleri temizle
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Noktalama işaretlerini kontrol et
    filename = filename.replace('.', '_')
    
    # Birden fazla boşluğu tek boşluğa indir
    filename = ' '.join(filename.split())
    
    # Boşlukları alt çizgi ile değiştir
    filename = filename.replace(' ', '_')
    
    return filename

def webvtt_to_milliseconds(time_str):
    """WebVTT zaman formatını milisaniyeye çevirir"""
    h, m, s = time_str.split(':')
    s, ms = s.split('.')
    total_ms = (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)
    return total_ms

def split_audio_by_subtitles(audio_file, subtitle_file, video_id):
    """Ses dosyasını altyazılara göre böler."""
    try:
        # Ses dosyasını yükle
        audio = AudioSegment.from_file(audio_file)
        
        # Çıktı klasörünü oluştur
        output_dir = os.path.join("output", "audio", video_id)
        os.makedirs(output_dir, exist_ok=True)

        # Altyazı dosyasını doğrudan oku
        subtitles = webvtt.read(subtitle_file)

        # Her altyazı için ses dosyasını böl
        for i, caption in enumerate(subtitles):
            try:
                start_time = webvtt_to_milliseconds(caption.start)
                end_time = webvtt_to_milliseconds(caption.end)
                
                # Çok kısa segmentleri atla
                if end_time - start_time < 500:  # 500ms'den kısa segmentleri atla
                    continue
                
                # Ses segmentini kes
                segment = audio[start_time:end_time]
                
                # Dosya adını oluştur
                text = clean_filename(caption.text)
                output_filename = f"{i:03d}_{text}.mp3"
                output_path = os.path.join(output_dir, output_filename)
                
                # Ses segmentini kaydet
                segment.export(output_path, format="mp3")
                print(f"Kaydedildi: {output_path}")
                
            except Exception as e:
                print(f"Uyarı: Segment {i} işlenirken hata oluştu: {e}")
                continue

    except Exception as e:
        print(f"Hata: Ses bölme işlemi sırasında bir sorun oluştu: {e}")
        raise

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
        print("Kullanım: python youtube_splitter_tr.py <youtube_link>")
        return

    youtube_url = sys.argv[1]
    print(f"İndiriliyor: {youtube_url}")

    video_id = extract_video_id(youtube_url)
    if not video_id:
        print("Hata: YouTube video kimliği bulunamadı!")
        return

    # Video daha önce indirilmiş mi kontrol et
    if check_if_video_downloaded(video_id):
        print(f"Uyarı: Bu video daha önce indirilmiş! (Video ID: {video_id})")
        sys.exit(1)  # Programı burada durdur

    # Video ve altyazıyı indir
    audio_file, subtitle_file, video_title = download_video_and_subtitles(youtube_url)

    # Ses dosyasını altyazı aralıklarına göre böl
    split_audio_by_subtitles(audio_file, subtitle_file, video_id)

    # Geçici dosyaları sil
    delete_temp_files(audio_file, subtitle_file)

    # Video kimliğini indirilenler listesine ekle
    mark_video_as_downloaded(video_id)

    print("İşlem tamamlandı!")

if __name__ == "__main__":
    main()