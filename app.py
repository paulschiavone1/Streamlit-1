"""Music Mood Matcher: mood-based recommendations, playlists, and a listening-based personality."""
import random
from html import escape
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

import music_data as md
import user_db as db
from styles import CSS

st.set_page_config(page_title="Music Mood Matcher", page_icon="🎧", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
db.init_db()

tracks = md.load_tracks()
if tracks is None:
    st.title("🎧 Music Mood Matcher")
    st.warning("The song library hasn't been added yet.")
    st.markdown(
        "1. Download the **Spotify Tracks Dataset** from "
        "[Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset)\n"
        "2. Put the CSV in this project at `data/dataset.csv`\n"
        "3. Reload the app"
    )
    st.stop()

# ---------- Session defaults ----------
st.session_state.setdefault("seed", 0)
st.session_state.setdefault("mood", "Happy")
st.session_state.setdefault("genre", "Any genre")
GENRES = ["Any genre"] + md.genre_list(tracks)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🎧 Your profile")
    user = st.text_input("Profile name", value="guest", help="Favorites, plays and playlists are saved per name.")
    user = user.strip().lower() or "guest"
    st.caption(f"Saving as **{user}**")
    st.divider()
    min_pop = st.slider("Minimum popularity", 0, 90, 30, help="Spotify popularity score, 0 to 100.")
    st.caption(f"Library: {len(tracks):,} tracks · {len(GENRES) - 1} genres")

favs = db.favorite_ids(user)
fav_set = set(favs)
counts = db.play_counts(user)


# ---------- Helpers ----------
def mini_bar(label, value):
    return (f'<div><div class="bar-label">{label}</div>'
            f'<div class="bar"><span style="width:{int(value * 100)}%"></span></div></div>')


def track_card(row, key, mood=None):
    tid = row["track_id"]
    with st.container(border=True):
        info, actions = st.columns([5, 3], vertical_alignment="center")
        with info:
            badges = ""
            if mood:
                m = md.MOODS[mood]
                badges += f'<span class="badge" style="background:{m["color"]}">{m["emoji"]} {mood}</span>'
            for g in row["genres"].strip("|").split("|")[:2]:
                badges += f'<span class="badge ghost">{escape(g)}</span>'
            if row["explicit"]:
                badges += '<span class="badge ghost">E</span>'
            plays = counts.get(tid, 0)
            plays_txt = f" · ▶ {plays}" if plays else ""
            st.markdown(
                f'<div>{badges}</div>'
                f'<div class="t-title">{escape(row["track_name"])}</div>'
                f'<div class="t-sub">{escape(row["artists"])} · {escape(row["album_name"])} · '
                f'{row["minutes"]:.1f} min · popularity {int(row["popularity"])}{plays_txt}</div>'
                f'<div class="bars">{mini_bar("Dance", row["danceability"])}{mini_bar("Energy", row["energy"])}'
                f'{mini_bar("Mood", row["valence"])}{mini_bar("Acoustic", row["acousticness"])}</div>',
                unsafe_allow_html=True,
            )
        with actions:
            c1, c2, c3 = st.columns(3)
            is_fav = tid in fav_set
            c1.button("❤️" if is_fav else "🤍", key=f"fav_{key}_{tid}", help="Favorite",
                      on_click=db.toggle_favorite, args=(user, tid), use_container_width=True)
            c2.button("▶", key=f"play_{key}_{tid}", help="Log a listen",
                      on_click=db.log_play, args=(user, tid), use_container_width=True)
            with c3.popover("＋", help="Add to playlist", use_container_width=True):
                pls = db.list_playlists(user)
                if not pls:
                    st.caption("Create a playlist in the Playlists tab first.")
                else:
                    choice = st.selectbox("Playlist", pls, format_func=lambda p: p[1], key=f"sel_{key}_{tid}")
                    if st.button("Add", key=f"add_{key}_{tid}"):
                        db.add_to_playlist(choice[0], tid)
                        st.toast(f"Added to {choice[1]}")
            q = quote_plus(f'{row["track_name"]} {row["artists"].split(",")[0]}')
            st.link_button("Open on YouTube", f"https://www.youtube.com/results?search_query={q}",
                           use_container_width=True)


def tracks_from_ids(ids):
    return tracks.loc[[t for t in ids if t in tracks.index]]


# ---------- Hero ----------
st.markdown(
    '<div class="hero"><h1>🎧 Music Mood Matcher</h1>'
    "<p>Pick a mood, explore a library of 100k+ Spotify tracks, build playlists, "
    "and see what your listening says about you.</p></div>",
    unsafe_allow_html=True,
)

tab_discover, tab_library, tab_playlists, tab_persona = st.tabs(
    ["🎯 Discover", "🔎 Library", "📚 Playlists", "🧬 Music personality"])

# ---------- Discover ----------
with tab_discover:
    def surprise():
        st.session_state.mood = random.choice(list(md.MOODS))
        st.session_state.genre = random.choice(GENRES[1:])
        st.session_state.seed = random.randint(0, 10_000)

    c1, c2 = st.columns([3, 2])
    with c1:
        mood = st.radio("How are you feeling?", list(md.MOODS), key="mood", horizontal=True,
                        format_func=lambda m: f"{md.MOODS[m]['emoji']} {m}")
        st.caption(md.MOODS[mood]["blurb"])
    with c2:
        genre = st.selectbox("Genre", GENRES, key="genre")
    c3, c4, c5 = st.columns([3, 1, 1])
    count = c3.slider("How many songs?", 3, 15, 6)
    c4.button("🔀 Shuffle", on_click=lambda: st.session_state.update(seed=random.randint(0, 10_000)),
              use_container_width=True)
    c5.button("🎲 Surprise me", on_click=surprise, use_container_width=True)

    picks = md.recommend(tracks, mood, genre, count, min_pop, st.session_state.seed)
    if picks.empty:
        st.info("No songs match. Try lowering the minimum popularity or choosing another genre.")
    else:
        st.subheader(f"{md.MOODS[mood]['emoji']} {mood} · {genre}")
        for _, row in picks.iterrows():
            track_card(row, "disc", mood)
        st.markdown("#### Artists to explore")
        st.write(" · ".join(dict.fromkeys(a.split(",")[0].strip() for a in picks["artists"])))
        favs_btn = st.button("❤️ Favorite all of these")
        if favs_btn:
            for tid in picks["track_id"]:
                if tid not in fav_set:
                    db.toggle_favorite(user, tid)
            st.rerun()

# ---------- Library ----------
with tab_library:
    st.subheader("Browse the library")
    f1, f2, f3 = st.columns([3, 3, 1])
    query = f1.text_input("Search title, artist or album", placeholder="e.g. Taylor Swift")
    chosen = f2.multiselect("Genres", GENRES[1:])
    hide_explicit = f3.toggle("Hide explicit")
    sort_by = st.radio("Sort by", ["popularity", "energy", "danceability", "valence", "tempo"],
                       horizontal=True, format_func=str.title)

    res = tracks[tracks["popularity"] >= min_pop]
    if query:
        q = query.lower()
        mask = (res["track_name"].str.lower().str.contains(q, regex=False)
                | res["artists"].str.lower().str.contains(q, regex=False)
                | res["album_name"].str.lower().str.contains(q, regex=False))
        res = res[mask]
    if chosen:
        res = res[pd.concat([md.has_genre(res, g) for g in chosen], axis=1).any(axis=1)]
    if hide_explicit:
        res = res[~res["explicit"]]
    res = res.sort_values(sort_by, ascending=False)

    PAGE = 10
    pages = max(1, -(-len(res) // PAGE))
    page = st.number_input(f"Page (of {pages:,})", 1, pages, 1)
    st.caption(f"{len(res):,} matching tracks")
    for _, row in res.iloc[(page - 1) * PAGE: page * PAGE].iterrows():
        track_card(row, "lib")

# ---------- Playlists ----------
with tab_playlists:
    st.subheader("Your playlists")
    with st.form("new_playlist", clear_on_submit=True):
        n1, n2 = st.columns([4, 1], vertical_alignment="bottom")
        new_name = n1.text_input("New playlist name", placeholder="Study session, Road trip…")
        if n2.form_submit_button("Create", use_container_width=True) and new_name:
            if db.create_playlist(user, new_name) is None:
                st.error("That name is already used.")
            else:
                st.rerun()

    smart = {"❤️ Favorites": ("smart", favs), "🔥 Most listened": ("smart", db.most_played_ids(user))}
    options = {**smart, **{f"📁 {name}": ("custom", pid) for pid, name in db.list_playlists(user)}}
    label = st.radio("Choose a playlist", list(options), horizontal=True)
    kind, ref = options[label]
    ids = ref if kind == "smart" else db.playlist_track_ids(ref)
    pl = tracks_from_ids(ids)

    if pl.empty:
        st.info("Nothing here yet. Use 🤍 to favorite songs, ▶ to log listens, or ＋ to add to a playlist.")
    else:
        s1, s2, s3 = st.columns(3)
        s1.markdown(f'<div class="stat"><div class="n">{len(pl)}</div><div class="l">tracks</div></div>',
                    unsafe_allow_html=True)
        s2.markdown(f'<div class="stat"><div class="n">{pl["minutes"].sum():.0f} min</div>'
                    f'<div class="l">total length</div></div>', unsafe_allow_html=True)
        s3.markdown(f'<div class="stat"><div class="n">{pl["energy"].mean():.0%}</div>'
                    f'<div class="l">average energy</div></div>', unsafe_allow_html=True)
        st.write("")
        for _, row in pl.iterrows():
            track_card(row, "pl")
            if kind == "custom":
                st.button("Remove from playlist", key=f"rm_{ref}_{row['track_id']}",
                          on_click=db.remove_from_playlist, args=(ref, row["track_id"]))
        st.download_button("⬇️ Export as CSV",
                           pl[["track_name", "artists", "album_name", "popularity"]].to_csv(index=False),
                           file_name="playlist.csv", mime="text/csv")
    if kind == "custom":
        st.button("🗑️ Delete this playlist", on_click=db.delete_playlist, args=(ref,))

# ---------- Personality ----------
with tab_persona:
    st.subheader("Your music personality")
    profile = md.build_profile(tracks, counts, favs)
    if profile is None:
        st.info("Favorite (🤍) or listen to (▶) a few songs and your personality will appear here. "
                "It's calculated from the audio features of what you actually pick, not from a quiz.")
    else:
        emoji, name, desc = md.archetype(profile["avg"])
        st.markdown(f'<div class="persona"><div class="emoji">{emoji}</div><h2>{name}</h2>'
                    f'<p>{desc}</p></div>', unsafe_allow_html=True)
        left, right = st.columns(2)
        with left:
            st.markdown("##### Your sound")
            feat = pd.DataFrame({"Level": {k.title(): profile["avg"][k] for k in md.FEATURES}})
            st.bar_chart(feat, horizontal=True, color="#1DB954")
            st.caption(f"Average tempo {profile['avg']['tempo']:.0f} BPM · "
                       f"mainstream score {profile['avg']['popularity']:.0f}/100")
        with right:
            st.markdown("##### Top genres")
            st.write(" · ".join(f"**{g}**" for g, _ in profile["genres"]))
            st.markdown("##### Top artists")
            st.write(" · ".join(f"**{a}**" for a, _ in profile["artists"]))
            st.caption(f"Based on {profile['n_tracks']} songs and {profile['n_plays']} logged listens "
                       "(a favorite counts as 3 listens).")