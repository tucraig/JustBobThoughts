'''
just bob thoughts -> all of the text that happens between parenthesis
just bob sayings  -> all of the text that happens in a bob ross show

@author Tucker Craig (twitter.com/btuckerc)
'''
import os, sys, time, glob, random, shutil
from tqdm import tqdm

from pytube import YouTube, Playlist

from moviepy.editor import *
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup as bs

import tweepy

def download_clips(selected_season = None):
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
        for season,playlist in enumerate(tqdm(soup.find_all('h3',{'class':'yt-lockup-title'}))):
            if season == selected_season or selected_season == None:
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
                            try:
                                clip = VideoFileClip(episode_filename)
                                clip.subclip(float(start),float(start) + float(dur)).write_videofile("clips/S{}E{}-{}-{}.mp4".format(season+1,episode+1,text,clip_titles.count(text)),fps=30,codec='libx264')
                                # clip.subclip(float(start),float(start) + float(dur)).write_videofile("clips/S1E{}-{}-{}.gif".format(episode+1,text,clip_titles.count(text)),fps=30,codec='gif')
                                clip_titles.append(text)
                                clip.reader.close()
                                clip.audio.reader.close_proc()
                            except:
                                print("Could not get clip {}.".format(text))
                            os.system('cls' if os.name == 'nt' else 'clear')
                    time.sleep(3) # give clip audio/reader enough time to close
                    os.remove(episode_filename) # delete episode file

if __name__ ==  '__main__':
    download_clips()
    print("Finished downloading clips.")