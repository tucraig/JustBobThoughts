'''
just bob thoughts -> all of the text that happens between parenthesis
just bob sayings  -> all of the text that happens in a bob ross show

@author Tucker Craig (twitter.com/btuckerc)
'''
import os, sys, time, glob, random
from dotenv import load_dotenv

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

def tweet(file_name):
    clip_name = file_name.split("/")[-1]
    season = clip_name.split("-")[0]
    time_stamp = clip_name.split("-")[1].replace("_",":")
    title = clip_name.split("-")[2].replace("_"," ")
    text = "({})\n-{}@{} #BobRossThoughts".format(title,time_stamp,season)
    upload_result = api.upload_chunked('{}'.format(file_name))
    api.update_status(status=text, media_ids=[upload_result.media_id_string])
    print("Tweeted status {}".format(text))
    #api.update_status(filename='clips/{}'.format(clip_name), status=text, file='{}'.format(clip_name))

if __name__ == '__main__':
    filenames = [i.split("\\")[-1] for i in glob.glob("clips/*.mp4")]
    if len(filenames) > 1:
        chosen_file = random.choice(filenames)
        tweet(chosen_file)
        os.remove(chosen_file)
    else:
        print("Please run 'download_clips.py', there don't seem to be any clips to post.")
        exit(-1)