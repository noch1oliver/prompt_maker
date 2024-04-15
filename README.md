# Prompt Maker 
**Turn your Spotify data into highly descriptive music generation prompts**

A Python script to transform the songs and styles you really like into data, and then into prompts. This creative exploration translates Spotify’s detailed audio metrics into highly descriptive tokens for tool like udio.com

## Prerequisites

- A well curated Spotify account that reflects your listening habits.
- Optional: access to the openAI API to improve the lyric analysis and generation.
This script was written and tested on a Mac with Python 3.12 — it should work with minor modifications on Linux and Windows machines and older Python versions.

This exploration will access your top track information from Spotify. You will get the audio features for each track to combine and translate them into a prompt. Acousticness, Danceability, Energy, Tempo and others are an awesome foundation for descriptive prompts. Moreover, you will need the genre information for the track’s artist.

## Let’s start
Switch to you Mac’s Terminal app and prepare the code.

```
git clone https://github.com/noch1oliver/prompt_maker
cd prompt_maker

# setup to isolate the installation 
virtualenv env

# activate environment
source env/bin/activate

# install necessary libraries
pip3 install spotipy openai
```

We will use the spotipy library to connect to your Spotify account. This requires to set up a Spotify developer app. The workflow can be a little tricky. If you encounter problems, check out Ian Annase’s comprehensive walkthrough on Youtube.

On your browser, head to the Spotify developer dashboard and click “Create app”.

Enter the information in the form:

- App name: promptmaker (or any app name you prefer)
- Redirect URI: http://www.google.com/ (This can be any valid URL. Just make sure to put a forward slash at the end)

Click “settings” and copy the relevant information. Switch to your Terminal window and add the info as secrets to your environent. For each line, paste the information between the quotation marks and hit enter.

```
export SPOTIPY_CLIENT_ID='your-spotify-client-id'
export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
# Again, make sure you have the forward slash at the end

# If you want to analyze the song titles 
# and have access to openAI API, enter the key
export OPENAI_API_KEY='your-open-ai-api-key'
```

Find a detailed walkthrough and more hints on the setup in the medium story.
https://medium.com/@mail_54889/let-your-spotify-data-write-your-best-music-prompt-3e9400009f43




