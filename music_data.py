"""Loads the Kaggle Spotify Tracks dataset and turns audio features into moods and personalities."""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "dataset.csv"

COLUMNS = ["track_id", "artists", "album_name", "track_name", "popularity", "duration_ms", "explicit",
           "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness",
           "valence", "tempo", "track_genre"]
FEATURES = ["danceability", "energy", "valence", "acousticness", "instrumentalness"]

MOODS = {
    "Happy": {"emoji": "😄", "color": "#FFC857", "blurb": "Bright, positive, danceable"},
    "Sad": {"emoji": "😢", "color": "#5B8DEF", "blurb": "Low-valence, softer, emotional"},
    "Relaxed": {"emoji": "😌", "color": "#4ECDC4", "blurb": "Slow, acoustic, easygoing"},
    "Energetic": {"emoji": "⚡", "color": "#FF5C77", "blurb": "Loud, fast, high-intensity"},
    "Focused": {"emoji": "🎯", "color": "#B388FF", "blurb": "Instrumental, steady, low-lyric"},
}


@st.cache_data(show_spinner="Loading the song library…")
def load_tracks():
    """One row per unique track; `genres` holds every genre tag as '|a|b|'."""
    if not DATA_PATH.exists():
        return None
    df = pd.read_csv(DATA_PATH, usecols=lambda c: c in COLUMNS)
    df = df.dropna(subset=["track_id", "track_name", "artists"])
    df["track_genre"] = df["track_genre"].fillna("unknown")
    genres = df.groupby("track_id")["track_genre"].agg(lambda s: "|" + "|".join(sorted(set(s))) + "|")
    df = df.sort_values("popularity", ascending=False).drop_duplicates("track_id")
    df["genres"] = df["track_id"].map(genres)
    df["artists"] = df["artists"].astype(str).str.replace(";", ", ")
    df["album_name"] = df["album_name"].fillna("")
    df["explicit"] = df["explicit"].astype(bool)
    df["minutes"] = (df["duration_ms"] / 60000).round(2)
    return df.drop(columns=["track_genre"]).set_index("track_id", drop=False)


@st.cache_data
def genre_list(_df):
    tags = set()
    for g in _df["genres"].unique():
        tags.update(g.strip("|").split("|"))
    return sorted(tags)


def has_genre(df, genre):
    return df["genres"].str.contains(f"|{genre}|", regex=False)


def mood_score(df, mood):
    """0-1 score of how well each track fits a mood, computed from Spotify audio features."""
    tempo = ((df["tempo"] - 60) / 120).clip(0, 1)
    if mood == "Happy":
        return df["valence"] * 0.6 + df["energy"] * 0.2 + df["danceability"] * 0.2
    if mood == "Sad":
        return (1 - df["valence"]) * 0.6 + (1 - df["energy"]) * 0.25 + df["acousticness"] * 0.15
    if mood == "Relaxed":
        return (1 - df["energy"]) * 0.45 + df["acousticness"] * 0.3 + (1 - tempo) * 0.25
    if mood == "Energetic":
        return df["energy"] * 0.5 + tempo * 0.25 + df["danceability"] * 0.25
    # Focused
    wordless = 1 - (df["speechiness"] * 2).clip(0, 1)
    steady = 1 - (df["energy"] - 0.5).abs() * 2
    return df["instrumentalness"] * 0.4 + wordless * 0.2 + steady * 0.4


def recommend(df, mood, genre, count, min_popularity, seed):
    pool = df if genre == "Any genre" else df[has_genre(df, genre)]
    pool = pool[pool["popularity"] >= min_popularity]
    if pool.empty:
        return pool
    top = pool.loc[mood_score(pool, mood).nlargest(200).index]
    return top.sample(min(count, len(top)), random_state=seed).sort_values("popularity", ascending=False)


def build_profile(df, plays, favorites):
    """Weighted listening profile: each play counts once, each favorite counts as 3 extra plays."""
    weights = {}
    for tid, n in plays.items():
        weights[tid] = weights.get(tid, 0) + n
    for tid in favorites:
        weights[tid] = weights.get(tid, 0) + 3
    weights = {t: w for t, w in weights.items() if t in df.index}
    if not weights:
        return None
    rows = df.loc[list(weights)]
    w = pd.Series(weights).loc[rows.index]
    avg = {f: float(np.average(rows[f], weights=w)) for f in FEATURES}
    avg["tempo"] = float(np.average(rows["tempo"], weights=w))
    avg["popularity"] = float(np.average(rows["popularity"], weights=w))
    genre_w = {}
    for tid, genres in rows["genres"].items():
        for g in genres.strip("|").split("|")[:2]:
            genre_w[g] = genre_w.get(g, 0) + w[tid]
    artist_w = {}
    for tid, artists in rows["artists"].items():
        lead = artists.split(",")[0].strip()
        artist_w[lead] = artist_w.get(lead, 0) + w[tid]
    return {
        "avg": avg,
        "genres": sorted(genre_w.items(), key=lambda kv: -kv[1])[:5],
        "artists": sorted(artist_w.items(), key=lambda kv: -kv[1])[:5],
        "n_tracks": len(rows),
        "n_plays": int(sum(plays.values())),
    }


def archetype(avg):
    """Pick a listener type from average audio features. First matching rule wins."""
    e, v, d, a, i = (avg[k] for k in ("energy", "valence", "danceability", "acousticness", "instrumentalness"))
    if i > 0.3:
        return "🎯", "The Focused Mind", "Your library leans instrumental and steady: music that helps you get into flow."
    if e > 0.7 and v > 0.6:
        return "⚡", "The Hype Machine", "Loud, fast, and joyful. Your playlists are a main-character montage."
    if e > 0.7:
        return "🔥", "The Adrenaline Seeker", "You like intensity, even when the mood is darker. Volume up."
    if v < 0.35:
        return "🌧️", "The Deep Feeler", "You gravitate to moody, emotional songs and use music to process feelings."
    if e < 0.45 and a > 0.5:
        return "🌿", "The Acoustic Dreamer", "Soft, organic, unhurried. You pick warmth over volume."
    if d > 0.7:
        return "🪩", "The Groove Architect", "If it has a beat you can move to, it's in. Rhythm comes first for you."
    return "🎧", "The Balanced Listener", "You move easily between moods and styles. No single box fits you."