Music Recommendation System

Paul Schiavone

App Description

Music Mood Matcher recommends music based on how the user is feeling. The user selects a mood (happy, sad, relaxed, energetic, or focused), chooses a music genre, and picks how many songs they want. The app instantly displays recommended songs with links to search for them on YouTube, a list of artists to explore, playlist ideas to search for, and a fun description of the user's music personality.

Intended Users

This app is intended for music fans of all ages, especially students and young adults, who want quick, personalized suggestions for what to listen to without searching through streaming apps for the right vibe.

Current Features (Implemented)
Select a mood with radio buttons (happy, sad, relaxed, energetic, focused)
Choose a music genre from a dropdown (Pop, Rock, Hip-Hop, Electronic)
Choose how many songs to show with a slider
Song recommendations that update automatically based on the selections
Artists to explore, taken from the recommended songs
Playlist ideas to search for
Music personality description based on the chosen mood and genre
Planned Features (Final Version)
Add more genres (such as Country, R&B, Jazz, and Classical) and more songs per mood
Connect to a music service API for live recommendations and real playlist links
Let users save favorite songs to a list
Add a "Surprise me" button that picks a random mood and genre
Make the music personality result more detailed and shareable
How to Run
python -m pip install -r requirements.txt
streamlit run app.py