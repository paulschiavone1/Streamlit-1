"""Music Recommendation System - pick a mood and genre to get song recommendations."""
from urllib.parse import quote_plus
 
import streamlit as st
 
# ---------- Data ----------
# SONGS[genre][mood] -> list of (title, artist)
SONGS = {
    "Pop": {
        "Happy": [("Happy", "Pharrell Williams"), ("Can't Stop the Feeling!", "Justin Timberlake"), ("Good as Hell", "Lizzo")],
        "Sad": [("Someone Like You", "Adele"), ("drivers license", "Olivia Rodrigo"), ("when the party's over", "Billie Eilish")],
        "Relaxed": [("Sunday Morning", "Maroon 5"), ("Put Your Records On", "Corinne Bailey Rae"), ("Banana Pancakes", "Jack Johnson")],
        "Energetic": [("Levitating", "Dua Lipa"), ("Uptown Funk", "Mark Ronson ft. Bruno Mars"), ("Shake It Off", "Taylor Swift")],
        "Focused": [("Ocean Eyes", "Billie Eilish"), ("Holocene", "Bon Iver"), ("Intro", "The xx")],
    },
    "Rock": {
        "Happy": [("Don't Stop Me Now", "Queen"), ("Walking on Sunshine", "Katrina and the Waves"), ("Mr. Blue Sky", "Electric Light Orchestra")],
        "Sad": [("Fix You", "Coldplay"), ("Creep", "Radiohead"), ("Black", "Pearl Jam")],
        "Relaxed": [("Here Comes the Sun", "The Beatles"), ("Wish You Were Here", "Pink Floyd"), ("Harvest Moon", "Neil Young")],
        "Energetic": [("Thunderstruck", "AC/DC"), ("Seven Nation Army", "The White Stripes"), ("Eye of the Tiger", "Survivor")],
        "Focused": [("Time", "Pink Floyd"), ("Tom Sawyer", "Rush"), ("Karma Police", "Radiohead")],
    },
    "Hip-Hop": {
        "Happy": [("Good Life", "Kanye West ft. T-Pain"), ("Hey Ya!", "OutKast"), ("Juicy", "The Notorious B.I.G.")],
        "Sad": [("Lost Ones", "Lauryn Hill"), ("Runaway", "Kanye West"), ("Changes", "2Pac")],
        "Relaxed": [("Electric Relaxation", "A Tribe Called Quest"), ("Passin' Me By", "The Pharcyde"), ("Summertime", "DJ Jazzy Jeff & The Fresh Prince")],
        "Energetic": [("Lose Yourself", "Eminem"), ("Power", "Kanye West"), ("HUMBLE.", "Kendrick Lamar")],
        "Focused": [("N.Y. State of Mind", "Nas"), ("Get By", "Talib Kweli"), ("Dead Presidents II", "JAY-Z")],
    },
    "Electronic": {
        "Happy": [("One More Time", "Daft Punk"), ("Wake Me Up", "Avicii"), ("Don't You Worry Child", "Swedish House Mafia")],
        "Sad": [("Say My Name", "ODESZA"), ("Avril 14th", "Aphex Twin"), ("Strobe", "deadmau5")],
        "Relaxed": [("Weightless", "Marconi Union"), ("Porcelain", "Moby"), ("Sunset Lover", "Petit Biscuit")],
        "Energetic": [("Titanium", "David Guetta ft. Sia"), ("Levels", "Avicii"), ("Around the World", "Daft Punk")],
        "Focused": [("A Walk", "Tycho"), ("Open Eye Signal", "Jon Hopkins"), ("Teardrop", "Massive Attack")],
    },
}
 
MOOD_EMOJI = {"Happy": "😄", "Sad": "😢", "Relaxed": "😌", "Energetic": "⚡", "Focused": "🎯"}
 
MOOD_PERSONALITY = {
    "Happy": "You're the sunshine of the playlist: upbeat, social, and always ready to sing along.",
    "Sad": "You're a deep feeler who uses music to process emotions, and you appreciate honest, heartfelt songs.",
    "Relaxed": "You're a calm soul who values good vibes, slow mornings, and a soundtrack with no rush.",
    "Energetic": "You're a high-voltage hype machine who turns every moment into a main-character montage.",
    "Focused": "You're a mindful multitasker who knows the right background music can unlock your best work.",
}
 
GENRE_PERSONALITY = {
    "Pop": "With pop, you love a catchy hook and a chorus everyone knows.",
    "Rock": "With rock, you crave guitars, drama, and songs with a little attitude.",
    "Hip-Hop": "With hip-hop, you tune in to rhythm, wordplay, and a strong point of view.",
    "Electronic": "With electronic, you're drawn to big textures, steady beats, and futuristic sound.",
}
 
# ---------- Page ----------
st.set_page_config(page_title="Music Mood Matcher", page_icon="🎧")
st.title("Music Mood Matcher")
st.write(
    "Tell us how you're feeling and what kind of music you like, and we'll recommend "
    "songs, artists, and playlist ideas, plus a fun description of your music personality."
)
 
# ---------- Inputs ----------
st.header("1. Tell us about your vibe")
mood = st.radio("How are you feeling right now?", list(MOOD_EMOJI), horizontal=True,
                format_func=lambda m: f"{MOOD_EMOJI[m]} {m}")
genre = st.selectbox("Pick a music genre", list(SONGS))
count = st.slider("How many songs do you want?", min_value=1, max_value=3, value=3)
 
# ---------- Outputs (update whenever an input changes) ----------
picks = SONGS[genre][mood][:count]
 
st.header(f"2. Your {mood.lower()} {genre} recommendations")
st.subheader("Songs")
for title, artist in picks:
    search = quote_plus(f"{title} {artist}")
    st.markdown(f"- **{title}** by {artist} "
                f"([listen on YouTube](https://www.youtube.com/results?search_query={search}))")
 
st.subheader("Artists to explore")
artists = list(dict.fromkeys(artist for _, artist in picks))  # unique, keeps order
st.write(", ".join(artists))
 
st.subheader("Playlist ideas to search for")
st.write(f"- {mood} {genre} Mix\n- Best of {genre} for Feeling {mood}\n- {genre} {mood} Vibes")
 
st.header("3. Your music personality")
st.info(f"{MOOD_PERSONALITY[mood]} {GENRE_PERSONALITY[genre]}")