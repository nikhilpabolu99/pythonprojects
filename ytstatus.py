from googleapiclient.discovery import build
import re
from datetime import datetime, timezone, timedelta
import tweepy

#API_KEY = 'AIzaSyAq9vTBrsBpL8UPCmeEgBF5VLgdXZUtXys'
youtube = build('youtube', 'v3', developerKey=API_KEY)

consumer_key = ''
consumer_secret = ''
bearer_token = ''
access_token = ''
access_token_secret = ''

client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_token, access_token_secret=access_token_secret)

def extract_video_id(url):
    regex = (r"(https?://)?(www\.)?"
             r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
             r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})")
    match = re.search(regex, url)
    return match.group(6) if match else None

def get_video_stats(video_id):
    request = youtube.videos().list(
        part='statistics,snippet',
        id=video_id
    )
    response = request.execute()
    
    if response['items']:
        video_stats = response['items'][0]['statistics']
        snippet = response['items'][0]['snippet']
        
        views = int(video_stats.get('viewCount', 0))
        likes = int(video_stats.get('likeCount', 0))
        upload_time = snippet.get('publishedAt', 'N/A')
        
        if upload_time != 'N/A':
            upload_datetime = datetime.strptime(upload_time, '%Y-%m-%dT%H:%M:%SZ')
            upload_datetime = upload_datetime.replace(tzinfo=timezone.utc)
            ist_offset = timedelta(hours=5, minutes=30)
            upload_ist = upload_datetime + ist_offset
            
            return {'views': views, 'likes': likes, 'upload_time': upload_ist}
        else:
            return {'views': 0, 'likes': 0, 'upload_time': 'N/A'}
    else:
        return {'views': 0, 'likes': 0, 'upload_time': 'N/A'}

def format_count(count, unit):
    """
    Format the count based on millions or thousands with 2 or 3 decimal places.
    """
    if count >= 1_000_000:
        return f"{count / 1_000_000:.3f}M" if count < 10_000_000 else f"{count / 1_000_000:.2f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.3f}K" if count < 10_000 else f"{count / 1_000:.2f}K"
    else:
        return str(count)

def main():
    video_urls = {
        'Telugu': 'https://youtu.be/22IEnKGVuUY?si=yRtnt38vP1V7OGm-',
        'Hindi': 'https://youtu.be/TV8OOVDnq8w?si=AL_g63uoSiAjZzFC',
        'Tamil': 'https://youtu.be/RLc8BsHourA?si=O80j31WWLaMd1KR_',
        'Kannada': 'https://youtu.be/7zp5iBcQA60?si=4tH5tKA9gHxvK8_S',
        'Malayalam': 'https://youtu.be/Ow_x-QNSg2U?si=Mrv3AUUxMMs-sHJs'
    }
    
    first_video_id = extract_video_id(list(video_urls.values())[0])
    first_video_stats = get_video_stats(first_video_id)
    
    upload_time = first_video_stats['upload_time']
    print(upload_time)
    now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    
    time_diff = now_ist - upload_time
    hours_since_upload, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes_since_upload = remainder // 60
    
    tweet_text = (f"{int(hours_since_upload)} hours and {int(minutes_since_upload)} minutes since upload\n" )
                 # f"Current IST time: {now_ist.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    total_views = 0
    total_likes = 0
    
    for language, url in video_urls.items():
        video_id = extract_video_id(url)
        if video_id:
            stats = get_video_stats(video_id)
            formatted_views = format_count(stats['views'], 'M')
            formatted_likes = format_count(stats['likes'], 'K')
            tweet_text += (f"{language}: {formatted_views} views & {formatted_likes} likes\n")
            
            total_views += stats['views']
            total_likes += stats['likes']
        else:
            tweet_text += f"Invalid YouTube URL for {language}: {url}\n\n"
    
    tweet_text += (f"Total: {format_count(total_views, 'M')} views & "
                   f"{format_count(total_likes, 'K')} likes\n")
    
    print(tweet_text)
    
    '''
    response = client.create_tweet(text=tweet_text)
    print(f"Tweeted: {tweet_text} | Response: {response}")
    '''

if __name__ == "__main__":
    main()
