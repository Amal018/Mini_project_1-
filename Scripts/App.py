# ---------------- FULL WORKING CODE ----------------

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import sqlite3

# -------------- PAGE CONFIG (must be first Streamlit command!) --------------
st.set_page_config(page_title="IMDb 2024 Dashboard", layout="wide")

# ----------------- Load and clean data -----------------
@st.cache_data
def load_data():
    file_paths = [
        r"S:\Streamlit\Web scrap\imdb_action_movies_2024.csv",
        r"S:\Streamlit\Web scrap\imdb_adventure_movies_2024.csv",
        r"S:\Streamlit\Web scrap\imdb_animation_movies_2024.csv",
        r"S:\Streamlit\Web scrap\imdb_biography_movies_2024.csv",
        r"S:\Streamlit\Web scrap\imdb_crime_movies_2024.csv"
    ]

    dfs = [pd.read_csv(file) for file in file_paths]
    df = pd.concat(dfs, ignore_index=True)

    # Standardize columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df.rename(columns={
        'movie_title': 'title',
        'rating': 'ratings',
        'vote_count': 'voting_counts',
        'runtime': 'duration'
    }, inplace=True)

    df['ratings'] = pd.to_numeric(df['ratings'], errors='coerce')
    df['voting_counts'] = (
        df['voting_counts']
        .astype(str)
        .str.replace(",", "")
        .str.replace("K", "e3")
        .str.replace("M", "e6")
    )
    df['voting_counts'] = pd.to_numeric(df['voting_counts'], errors='coerce')
    df['duration'] = df['duration'].str.extract(r'(\d+)').astype(float)

    df.dropna(subset=['title', 'genre', 'ratings', 'voting_counts', 'duration'], inplace=True)

    return df

df = load_data()

# ------------------ store dataframe to sqlite ------------------
conn = sqlite3.connect("imdb_movie_data.db")
df.to_sql("movies", conn, if_exists="replace", index=False)
conn.commit()

# ----------------- App Title -----------------
st.title("🎬 IMDb 2024 Movie Dashboard")

# ----------------- Sidebar Navigation -----------------
st.sidebar.title("Navigation")
menu_choice = st.sidebar.radio("Select Section:", ["Visual Insights", "Filtration"])

# ----------------- Visual Insights Section -----------------
if menu_choice == "Visual Insights":

    st.markdown("## Visual Insights")
    tabs = st.tabs([
        "Top Movies", "Genre Distribution", "Avg Duration", "Votes by Genre",
        "Rating Distribution", "Top by Genre", "Popular Genres",
        "Duration Extremes", "Ratings Heatmap", "Ratings vs Votes"
    ])

    with tabs[0]:
        st.subheader("🎯 Top 10 Movies by Rating and Votes")
        top_movies = df.sort_values(by=['ratings', 'voting_counts'], ascending=False).head(10)
        st.dataframe(top_movies[['title', 'genre', 'ratings', 'voting_counts']])

    with tabs[1]:
        st.subheader("📊 Genre Distribution")
        genre_counts = df['genre'].value_counts()
        st.bar_chart(genre_counts)

    with tabs[2]:
        st.subheader("⏱️ Average Duration by Genre")
        avg_duration = df.groupby('genre')['duration'].mean().sort_values(ascending=False)
        st.bar_chart(avg_duration)

    with tabs[3]:
        st.subheader("🗳️ Average Votes by Genre")
        avg_votes = df.groupby('genre')['voting_counts'].mean().sort_values(ascending=False)
        st.bar_chart(avg_votes)

    with tabs[4]:
        st.subheader("🎯 Rating Distribution")
        fig1, ax1 = plt.subplots()
        sns.histplot(df['ratings'], kde=True, ax=ax1, bins=20)
        st.pyplot(fig1)

    with tabs[5]:
        st.subheader("🏆 Top-Rated Movies by Genre")
        top_by_genre = df.loc[df.groupby('genre')['ratings'].idxmax()][['genre', 'title', 'ratings']]
        st.dataframe(top_by_genre)

    with tabs[6]:
        st.subheader("🔥 Most Popular Genres by Total Votes")
        vote_share = df.groupby('genre')['voting_counts'].sum().nlargest(6).reset_index()
        fig2 = px.pie(vote_share, values='voting_counts', names='genre')
        st.plotly_chart(fig2)

    with tabs[7]:
        st.subheader("🕒 Shortest and Longest Movies")
        shortest = df[df['duration'] == df['duration'].min()][['title', 'duration']]
        longest = df[df['duration'] == df['duration'].max()][['title', 'duration']]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Shortest Duration", f"{shortest.iloc[0]['duration']} min")
            st.dataframe(shortest)
        with col2:
            st.metric("Longest Duration", f"{longest.iloc[0]['duration']} min")
            st.dataframe(longest)

    with tabs[8]:
        st.subheader("🌡️ Ratings Heatmap by Genre")
        rating_heat = df.pivot_table(values='ratings', index='genre', aggfunc='mean')
        fig3, ax3 = plt.subplots()
        sns.heatmap(rating_heat, annot=True, cmap="YlGnBu", ax=ax3)
        st.pyplot(fig3)

    with tabs[9]:
        st.subheader("📈 Ratings vs. Votes Correlation")
        fig4 = px.scatter(df, x='voting_counts', y='ratings', hover_data=['title', 'genre'])
        st.plotly_chart(fig4)

# ----------------- Filtration Section from DATABASE -----------------
if menu_choice == "Filtration":

    st.subheader("🔍 Filtered Dataset (from Database)")

    st.sidebar.header("🔧 Filter Options")

    # get distinct genres from db
    genres_query = "SELECT DISTINCT genre FROM movies"
    genres = pd.read_sql(genres_query, conn)['genre'].tolist()

    selected_genres = st.sidebar.multiselect("Select Genres", options=genres, default=genres)
    rating_min = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0)
    # get max voting_counts from db
    max_votes = pd.read_sql("SELECT MAX(voting_counts) as mv FROM movies", conn)['mv'].iloc[0]
    votes_min = st.sidebar.slider("Minimum Votes", 0, int(max_votes), 1000)
    duration_range = st.sidebar.selectbox("Duration Range", ["All", "< 2 hrs", "2–3 hrs", "> 3 hrs"])

    # build SQL query
    sql = """
        SELECT title, genre, ratings, voting_counts, duration
        FROM movies
        WHERE genre IN ({genre_list})
        AND ratings >= {rating_min}
        AND voting_counts >= {votes_min}
    """.format(
        genre_list=",".join(["'{}'".format(g) for g in selected_genres]),
        rating_min=rating_min,
        votes_min=votes_min
    )

    if duration_range == "< 2 hrs":
        sql += " AND duration < 120"
    elif duration_range == "2–3 hrs":
        sql += " AND duration >= 120 AND duration <= 180"
    elif duration_range == "> 3 hrs":
        sql += " AND duration > 180"

    filtered_df = pd.read_sql(sql, conn)

    st.markdown("### Filtered Results")
    st.dataframe(filtered_df)

# close connection
conn.close()
