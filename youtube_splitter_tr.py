import os
import re
import sys
from pydub import AudioSegment
import webvtt
import yt_dlp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
    # YouTube API anahtarını environment variable'dan al
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'writeautomaticsub': True,
        'subtitlesformat': 'vtt',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    }
    
    try:
        # Video ID'sini URL'den çıkar
        video_id = url.split('watch?v=')[1]
        
        # YouTube API client'ını oluştur
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Video detaylarını al
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            raise Exception("Video bulunamadı")
            
        video_title = response['items'][0]['snippet']['title']
        
        # Video indirme işlemi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Video indiriliyor: {url}")
            ydl.download([url])
            
        audio_file = f"{video_title}.mp3"
        subtitle_file = f"{video_title}.tr.vtt"
        
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