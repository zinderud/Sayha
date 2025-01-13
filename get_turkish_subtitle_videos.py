import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from dotenv import load_dotenv

def get_turkish_subtitle_videos(api_key, search_query=None, start_date=None, end_date=None, max_results=50):
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_links = []
    
    try:
        # Search parametrelerini hazırla
        search_params = {
            'part': 'id,snippet',  # snippet eklendi
            'maxResults': max_results,
            'type': 'video',
            'regionCode': 'TR',    # Türkiye bölgesi eklendi
            'relevanceLanguage': 'tr'  # Türkçe içerik önceliği
        }
        
        # Opsiyonel parametreleri ekle
        if search_query:
            search_params['q'] = search_query
            
        if start_date:
            search_params['publishedAfter'] = start_date.isoformat() + "Z"
            
        if end_date:
            search_params['publishedBefore'] = end_date.isoformat() + "Z"
            
        videos_checked = 0
        page_token = None
        
        while videos_checked < max_results:
            if page_token:
                search_params['pageToken'] = page_token
                
            # Videoları ara
            search_response = youtube.search().list(**search_params).execute()
            
            if not search_response.get('items'):
                break
                
            # Her video için altyazı kontrolü yap
            for item in search_response['items']:
                videos_checked += 1
                video_id = item['id']['videoId']
                
                try:
                    # Altyazı bilgilerini al
                    captions_response = youtube.captions().list(
                        part='snippet',
                        videoId=video_id
                    ).execute()
                    
                    # Türkçe manuel altyazı kontrolü
                    has_turkish_subs = any(
                        caption['snippet']['language'] == 'tr' and 
                        caption['snippet']['trackKind'] == 'standard'
                        for caption in captions_response.get('items', [])
                    )
                    
                    if has_turkish_subs:
                        # Video başlığını ve linkini kaydet
                        video_title = item['snippet']['title']
                        video_links.append({
                            'title': video_title,
                            'url': f'https://www.youtube.com/watch?v={video_id}'
                        })
                        
                        print(f"Bulunan video: {video_title}")
                
                except HttpError as e:
                    continue  # Bir video hata verirse diğerine geç
            
            # Sonraki sayfa için token al
            page_token = search_response.get('nextPageToken')
            if not page_token:
                break
    
    except HttpError as e:
        print(f'API Hatası: {e}')
    
    return video_links

def save_links_to_txt(links, search_query=None, start_date=None, end_date=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"turkce_altyazili_videolar_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Arama Kriterleri:\n")
        if start_date and end_date:
            f.write(f"Tarih Aralığı: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n")
        if search_query:
            f.write(f"Arama Kelimesi: {search_query}\n")
        f.write("-" * 50 + "\n\n")
        
        # Her video için başlık ve link yaz
        for video in links:
            f.write(f"{video['url']}\n")
        """  f.write(f"{video['title']}\n{video['url']}\n\n")"""    
    return filename

def get_date_input(prompt):
    while True:
        try:
            date_str = input(prompt + " (GG.AA.YYYY formatında): ")
            return datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            print("Hatalı tarih formatı! Lütfen GG.AA.YYYY formatında girin (örnek: 01.01.2024)")

def main():
    load_dotenv()
    API_KEY = os.getenv('goole_api_key')
   
    # Arama terimi opsiyonel
    search_query = None
    search_option = input("Arama kelimesi kullanmak istiyor musunuz? (E/H): ").upper()
    if search_option == 'E':
        search_query = input("Aramak istediğiniz kelime veya cümleyi girin: ")
    
    # Tarih aralığı opsiyonel
    start_date = None
    end_date = None
    date_option = input("Tarih aralığı kullanmak istiyor musunuz? (E/H): ").upper()
    if date_option == 'E':
        start_date = get_date_input("Başlangıç tarihini girin")
        end_date = get_date_input("Bitiş tarihini girin")
        # Bitiş tarihinin sonuna kadar arama yapmak için
        end_date = end_date + timedelta(days=1)
    
    print("\nVideolar aranıyor...")
    video_links = get_turkish_subtitle_videos(
        API_KEY,
        search_query=search_query,
        start_date=start_date,
        end_date=end_date
    )
    
    if video_links:
        filename = save_links_to_txt(
            video_links,
            search_query=search_query,
            start_date=start_date,
            end_date=end_date
        )
        print(f"\nToplam {len(video_links)} video bulundu.")
        print(f"Linkler {filename} dosyasına kaydedildi.")
    else:
        print("Belirtilen kriterlere uygun Türkçe manuel altyazılı video bulunamadı.")

if __name__ == "__main__":
    main()
