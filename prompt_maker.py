import spotipy
from spotipy.oauth2 import SpotifyOAuth
from math import floor
from collections import Counter
from openai import OpenAI


number_of_top_tracks = 10 # keep it between 3 and 50
scope = 'user-top-read' # submitted to spotify for the authentication process

# set objects for external services
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
results = sp.current_user_top_tracks(limit=number_of_top_tracks,
                                        offset=0, 
                                        time_range='long_term')

# helper function for prompt building gies here
def prompt_from_range(input_list, input_val):
    """returns the value matching the input on a range 0 to 1"""
    return_item = input_list[floor(input_val * len(input_list))]
    return f'{return_item}, '

# init variables
counter = 0
acousticness_sum = 0
danceability_sum = 0
energy_sum = 0
tempo_sum = 0
valence_sum = 0
instrumentalness_sum = 0
liveness_sum = 0
mode_sum = 0
genre_list = []
title_list = []

#iterate over top track results
for i, track in enumerate(results['items']):
    print('---')
    title = track['name']
    artist_name = track['artists'][0]['name']
    print(f'{i} {title} – {artist_name}')

    track_id = track['id']
    audio_features = sp.audio_features(track_id)

    speechiness = audio_features[0]['speechiness']
    if speechiness > 0.5:
        # ignore spoken content 
        print(f'speechiness: {speechiness} – ignoring as spoken content')
    else:
        counter += 1
        title_list.append(title)

        acousticness = audio_features[0]['acousticness']
        acousticness_sum += acousticness

        danceability = audio_features[0]['danceability']
        danceability_sum += danceability
        
        energy = audio_features[0]['energy']
        energy_sum += energy

        tempo = audio_features[0]['tempo']
        tempo_sum += tempo

        valence = audio_features[0]['valence']
        valence_sum += valence

        instrumentalness = audio_features[0]['instrumentalness']
        instrumentalness_sum += instrumentalness
        
        liveness = audio_features[0]['liveness']
        liveness_sum += liveness

        mode = audio_features[0]['mode']
        mode_sum += mode

        artist_id = track['artists'][0]['id']
        artist_info = sp.artist(artist_id)
        genres = artist_info.get('genres')
        print(f'Genres: {genres}')
        genre_list += genres #build a genre list

# turn averaged results into prompts 
acousticness_prompt = ["", "Slightly acoustic", 
                        "Some acoustic elements", 
                        "Fully acoustic"]
prompt = prompt_from_range(acousticness_prompt, acousticness_sum/counter)

danceability_prompt = ["low tempo, low beat strength", 
                        "uptempo, beat-driven", "high tempo, fast beat", 
                        "dance track"]
prompt += prompt_from_range(danceability_prompt, danceability_sum/counter)

energy_prompt = ["mellow", "moderate energy", "vibrant energy", 
                        "highly energetic, explosive"]
prompt += prompt_from_range(energy_prompt, energy_sum/counter)

tempo_prompt = ["chilled beat", "laid-back", "bouncy beat", 
                        "energetic beat", "breakneck beat"]
tempo_range = min(1, tempo_sum/counter/180) 
# everything above 180 bpm is beyond fast
prompt += prompt_from_range(tempo_prompt, tempo_range)
prompt += f'{int(tempo_sum/counter)} bpm, ' 

valence_prompt = ["sad, depressed, angry feeling", 
                    "gloomy and melancholic feeling", 
                    "neutral serene feeling", 
                    "cheerful, bright and sunny", 
                    "happy, cheerful, euphoric feeling"]
prompt += prompt_from_range(valence_prompt, valence_sum/counter)

instrumentalness_prompt = ["highly vocal", "intrumental with vocals", 
                            "instrumental song with no vocals"]
prompt += prompt_from_range(instrumentalness_prompt, 
                        instrumentalness_sum/counter)

liveness_prompt = ["studio recording", "live recording with audience"]
prompt += prompt_from_range(liveness_prompt, liveness_sum/counter)

mode_prompt = ["major mode", "", "minor mode"]
prompt += prompt_from_range(mode_prompt, mode_sum/counter)  

# Add genres yo your prompt
try:
    # get the most prominent genres
    genre_counts = Counter(genre_list) # creates a list of tuples  
    common_genres = genre_counts.most_common(3) # sort and limit 
    keys = [genre for genre, count in common_genres] 

    # find the longest genre description which is often the funniest
    max_length = max(len(genre) for genre in genre_list)
    peculiar_genre = [genre for genre in genre_list 
                        if len(genre) == max_length]
    peculiar_genre = peculiar_genre[0]

    genre_prompt = f'A {keys[0]} song with {keys[1]} and {keys[2]} elements.'
    genre_prompt += f'Spice it up with some {peculiar_genre}, '
    
    prompt = genre_prompt + prompt

except Exception as e:
    # sometimes no genres are defined and the handling fails. 
    print(f'Error {e} while handling genres. Proceeding without genres.')

# Let chatGPT determine underlying trends in your titles
try: 
    client = OpenAI()
    # chose the model: "gpt-3.5-turbo" (cheaper) or "gpt-4" (costier, but better).
    model = "gpt-4" 

    system_prompt = """You are a record company's portfolio 
        manager who analyzes 
        societal, behavioural, emotional topics in song titles.
        He considers several titles and transforms the most 
        striking meta-topic into brief for a lyricist that starts: 
        Write a song about [meta-topic]."""

    # Extrapolate the topic from your top 10 tracks 
    user_prompt = f"""Please have a look at these song titles {title_list[:10]} 
                        and turn them into a short single-sentence brief."""
    

    completion = client.chat.completions.create(
    model=model,
    messages=[  {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}])
    lyrics_prompt = completion.choices[0].message.content + " "

except Exception as e:
    print(f'Error {e} while fetching lyrics. Proceeding with generic prompt')
    lyrics_prompt = f'A song about \'{title_list[0]}\' '
    lyrics_prompt += f'from someone who adores \'{title_list[1]}\' '
    lyrics_prompt += f'while thinking \'{title_list[2]}\'.'

prompt = lyrics_prompt + prompt

print('\n\nHere is the prompt generated from your spotify data.')
print('Copy and paste it into your song generation tool.')
print('---')
print(prompt)
print('---')