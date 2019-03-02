'''
just bob thoughts -> all of the text that happens between parenthesis
just bob sayings  -> all of the text that happens in a bob ross show

@author Tucker Craig (twitter.com/btuckerc)
'''
import os, sys, time
from tqdm import tqdm
from dotenv import load_dotenv

from pytube import YouTube, Playlist

from moviepy.editor import *
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup as bs

# Create .env file path.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# Load file from the path.
load_dotenv(dotenv_path)
# Accessing variables.
TWITTER_USER = os.getenv('TWITTER_USER')
TWITTER_PASS = os.getenv('TWITTER_PASS')

with requests.Session() as session:
    url = "https://www.youtube.com/user/BobRossInc/playlists?shelf_id=7&view=50&sort=dd"
    session.get(url)
    sauce = session.get(url)
    soup = bs(sauce.content,'html')
    for season,playlist in enumerate(soup.find_all('h3',{'class':'yt-lockup-title'})):
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
                    clip.subclip(float(start),float(start) + float(dur)).write_videofile("clips/S1E{}-{}{}.mp4".format(episode+1,text,clip_titles.count(text)),fps=24,codec='mpeg4')
                    clip_titles.append(text)
                    clip.reader.close()
                    clip.audio.reader.close_proc()
            time.sleep(3) # give clip audio/reader enough time to close
            os.remove(episode_filename) # delete episode file