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
    # Çerez bilgilerini environment variable'dan al
    youtube_cookies = os.getenv('YOUTUBE_COOKIES')
    
    if youtube_cookies:
        # Geçici çerez dosyası oluştur
        with open('cookies.txt', 'w') as f:
            f.write(youtube_cookies)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['tr'],
        'subtitlesformat': 'vtt',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
        'cookiefile': 'cookies.txt' if youtube_cookies else None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Video indiriliyor: {url}")
            info = ydl.extract_info(url, download=True)
            video_title = info['title']
            
            # Dosya isimlerini bul
            audio_file = None
            subtitle_file = None
            
            for file in os.listdir():
                if file.endswith(".mp3"):
                    audio_file = file
                elif file.endswith(".tr.vtt"):
                    subtitle_file = file
            
            if not audio_file or not subtitle_file:
                print(f"Ses dosyası: {audio_file}")
                print(f"Altyazı dosyası: {subtitle_file}")
                raise Exception("Ses veya altyazı dosyası bulunamadı")
                
            return audio_file, subtitle_file, video_title
            
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return None, None, None

def split_audio_by_subtitles(audio_file, subtitle_file, folder_name):
    """Ses dosyasını altyazı aralıklarına göre böler ve kaydeder."""
    if not subtitle_file or not os.path.exists(subtitle_file):
        print("Hata: Altyazı dosyası bulunamadı. İşlem iptal edildi.")
        return

    if not audio_file or not os.path.exists(audio_file):
        print("Hata: Ses dosyası bulunamadı. İşlem iptal edildi.")
        return

    subs = webvtt.read(subtitle_file)
    audio = AudioSegment.from_file(audio_file)

    output_folder = os.path.join("output", folder_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, sub in enumerate(subs):
        start_time = int(sub.start_in_seconds * 1000)
        end_time = int(sub.end_in_seconds * 1000)

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