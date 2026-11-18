# 🎧 Music Mood Matcher

Paul Schiavone

Pick a mood, explore 100k+ Spotify tracks, build playlists, and discover your music personality.

## Features
- **Discover**: choose a mood (Happy, Sad, Relaxed, Energetic, Focused) and an optional genre. Songs are ranked by Spotify audio features (valence, energy, tempo, acousticness, instrumentalness), not hand-picked lists.
- **Surprise me / Shuffle**: random mood + genre, or a fresh set of picks.
- **Library**: search by title, artist or album; filter by genre; sort by popularity, energy, danceability, mood or tempo.
- **Playlists**: auto-built *Favorites* and *Most listened* lists, plus your own custom playlists. Export any list to CSV.
- **Music personality**: calculated from the audio features of the songs you favorite and listen to, with your top genres and artists.
- **Saved data**: favorites, play counts and playlists are stored in SQLite (`data/user_data.db`) per profile name.

## Data setup
1. Download the [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) from Kaggle.
2. Save the CSV as `data/dataset.csv`.

## Run
```
python -m pip install -r requirements.txt
streamlit run app.py
```

## Notes
- On Streamlit Community Cloud the file system resets when the app restarts, so saved playlists may not survive. For permanent storage, swap SQLite for a hosted database.
- There is no audio playback; "▶" logs a listen and "Open on YouTube" searches for the track.

## Project layout
`app.py` (UI) · `music_data.py` (dataset, moods, personality) · `user_db.py` (SQLite) · `styles.py` (CSS)
