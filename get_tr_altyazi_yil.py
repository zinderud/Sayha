import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from dotenv import load_dotenv
import isodate
import platform
import json

def parse_duration(duration_iso):
    """ISO 8601 süresini dakikaya çevirir."""
    try:
        duration = isodate.parse_duration(duration_iso)
        return int(duration.total_seconds() // 60)
    except Exception as e:
        logging.error(f"Süre parse hatası: {e}")
        return 0

def get_api_key():
    """API anahtarını .env dosyasından alır."""
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logging.error("Lütfen .env dosyanızda GOOGLE_API_KEY tanımlayın!")
        raise ValueError("API key eksik.")
    return api_key

def get_turkish_subtitle_videos(api_key, search_query=None, year=None, max_results=50):
    """YouTube API ile Türkçe altyazıya sahip videoları arar."""
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_links = []

    logging.info("get_turkish_subtitle_videos fonksiyonu çağrıldı.")

    try:
        search_params = {
            'part': 'id,snippet',
            'maxResults': max_results,
            'type': 'video',
            'regionCode': 'TR',
            'relevanceLanguage': 'tr'
        }

        if search_query:
            search_params['q'] = search_query

        if year:
            start_date = datetime(year, 1, 1).isoformat() + "Z"
            end_date = datetime(year, 12, 31, 23, 59, 59).isoformat() + "Z"
            search_params['publishedAfter'] = start_date
            search_params['publishedBefore'] = end_date

        videos_checked = 0
        page_token = None

        while videos_checked < max_results:
            if page_token:
                search_params['pageToken'] = page_token

            search_response = youtube.search().list(**search_params).execute()

            if not search_response.get('items'):
                break

            video_ids = [item['id']['videoId'] for item in search_response['items']]

            try:
                videos_response = youtube.videos().list(
                    part='contentDetails',
                    id=','.join(video_ids)
                ).execute()
            except HttpError as e:
                logging.error(f"Video süreleri alınamadı: {e}")
                continue

            duration_map = {}
            for video in videos_response.get('items', []):
                vid = video['id']
                duration_iso = video['contentDetails']['duration']
                duration_map[vid] = parse_duration(duration_iso)

            for item in search_response['items']:
                videos_checked += 1
                video_id = item['id']['videoId']

                if duration_map.get(video_id, 0) < 3:
                    logging.info(f"Atlanan video {video_id} (Süre: {duration_map[video_id]} dakika)")
                    continue

                try:
                    captions_response = youtube.captions().list(
                        part='snippet',
                        videoId=video_id
                    ).execute()

                    has_turkish_subs = any(
                        caption['snippet']['language'] == 'tr' and 
                        caption['snippet']['trackKind'] == 'standard'
                        for caption in captions_response.get('items', [])
                    )

                    if has_turkish_subs:
                        video_links.append(f"https://www.youtube.com/watch?v={video_id}")
                        logging.info(f"Uygun video bulundu: {item['snippet']['title']}")

                except HttpError as e:
                    logging.error(f"Altyazı hatası ({video_id}): {e}")
                    continue

                if len(video_links) >= max_results:
                    break

            if len(video_links) >= max_results:
                break

            page_token = search_response.get('nextPageToken')
            if not page_token:
                break

    except HttpError as e:
        logging.error(f'API Hatası: {e}')

    return video_links

def save_links_to_txt(links, search_query=None, year=None):
    """Videoları bir dosyaya kaydeder."""
    logging.info("save_links_to_txt fonksiyonu çağrıldı.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"turkce_altyazili_videolar_{timestamp}.txt"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            formatted_links = [f'"{link}"' for link in links]
            f.write(','.join(formatted_links))
        logging.info(f"Dosya başarıyla oluşturuldu: {filename}")
    except Exception as e:
        logging.error(f"Dosya oluşturulurken hata oluştu: {e}")
        raise

    return filename

def main():
    """Ana uygulama fonksiyonu."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("application.log", mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    try:
        API_KEY = get_api_key()
        search_query = input("Arama yapmak istediğiniz kelimeyi girin (boş bırakabilirsiniz): ").strip() or None
        year = None

        if input("Belirli bir yıl için filtrelemek istiyor musunuz? (E/H): ").strip().upper() == 'E':
            while True:
                try:
                    year = int(input("Yıl girin (örneğin 2023): "))
                    break
                except ValueError:
                    logging.warning("Geçerli bir yıl giriniz.")

        logging.info("Videolar aranıyor...")
        videos = get_turkish_subtitle_videos(API_KEY, search_query, year)

        if videos:
            filename = save_links_to_txt(videos)
            logging.info(f"Bulunan videolar: {filename}")

            if platform.system() == "Windows":
                os.startfile(filename)
            else:
                logging.info(f"Lütfen dosyayı manuel olarak açın: {filename}")
        else:
            logging.info("Uygun video bulunamadı.")

    except Exception as e:
        logging.error(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    main()