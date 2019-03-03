'''
just bob thoughts -> all of the text that happens between parenthesis
just bob sayings  -> all of the text that happens in a bob ross show

@author Tucker Craig (twitter.com/btuckerc)
'''
import os, sys, time, glob, random, shutil
from tqdm import tqdm
from dotenv import load_dotenv

from pytube import YouTube, Playlist

from moviepy.editor import *
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup as bs

import tweepy

# Create .env file path.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# Load file from the path.
load_dotenv(dotenv_path)

# Accessing variables.
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
# Creation of the actual interface, using authentication
api = tweepy.API(auth)

def tweet(clip_name):
    season = clip_name.split("-")[0] 
    title = clip_name.split("-")[1].replace("_"," ")
    text = "({})\n-{} #JustBobRossThoughts".format(title,season)
    upload_result = api.upload_chunked('clips/{}'.format(clip_name))
    api.update_status(status=text, media_ids=[upload_result.media_id_string])
    #api.update_status(filename='clips/{}'.format(clip_name), status=text, file='{}'.format(clip_name))

def main():
    try:
        shutil.rmtree("clips")
    except Exception as e:
        pass
    time.sleep(3)
    os.mkdir("clips")

    with requests.Session() as session:
        url = "https://www.youtube.com/user/BobRossInc/playlists?shelf_id=7&view=50&sort=dd"
        session.get(url)
        sauce = session.get(url)
        soup = bs(sauce.content,'html')
        for season,playlist in enumerate(soup.find_all('h3',{'class':'yt-lockup-title'})):
            if season == 0:
                season_url = "https://www.youtube.com/{}".format(playlist.find('a').get('href'))
                pl = Playlist(season_url)
                pl.populate_video_urls()
                for episode,episode_url in enumerate(tqdm(pl.video_urls)):
                    clip_titles = []
                    vid = YouTube(episode_url)
                    vid.streams.filter(subtype='mp4').first().download()
                    episode_filename = "{}.mp4".format(vid.title.replace(".",""))
                    xml_caps = vid.captions.get_by_language_code('en').xml_captions
                    root = ET.fromstring(xml_caps)
                    for child in root:
                        start = child.attrib["start"]
                        dur = child.attrib["dur"]
                        text = child.text
                        if "(" in text:
                            text = text.replace("(","").replace(")","").replace(" ","_")
                            clip = VideoFileClip(episode_filename)
                            clip.subclip(float(start),float(start) + float(dur)).write_videofile("clips/S1E{}-{}-{}.mp4".format(episode+1,text,clip_titles.count(text)),fps=30,codec='libx264')
                            clip.subclip(float(start),float(start) + float(dur)).write_videofile("clips/S1E{}-{}-{}.gif".format(episode+1,text,clip_titles.count(text)),fps=30,codec='gif')
                            clip_titles.append(text)
                            clip.reader.close()
                            clip.audio.reader.close_proc()
                    time.sleep(3) # give clip audio/reader enough time to close
                    os.remove(episode_filename) # delete episode file

if __name__ == '__main__':
    main()
    filenames = [i.split("\\")[-1] for i in glob.glob("clips/*.mp4")]
    chosen_file = random.choice(filenames)
    tweet(chosen_file)