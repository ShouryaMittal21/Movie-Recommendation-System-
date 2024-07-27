# import streamlit as st
# import pickle
# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# import time

# # Load data
# movies = pickle.load(open("movies_list.pkl", 'rb'))
# similarity = pickle.load(open("similartiy.pkl", 'rb'))

# movies_list = movies['title'].values

# # Streamlit app header
# st.header("Movies Recommender System")
# selectValue = st.selectbox("Select movie from dropdown", movies_list)

# # Configure session with retries and exponential backoff
# session = requests.Session()
# retry_strategy = Retry(
#     total=3,  # Total number of retries
#     backoff_factor=2,  # Exponential backoff (e.g., 1s, 2s, 4s)
#     status_forcelist=[429, 500, 502, 503, 504],  # Retry for these status codes
# )
# adapter = HTTPAdapter(max_retries=retry_strategy)
# session.mount("https://", adapter)
# session.mount("http://", adapter)

# # Local cache for posters
# poster_cache = {}

# def fetch_poster(movie_id):
#     if movie_id in poster_cache:
#         return poster_cache[movie_id]
    
#     url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=da8894704dc5828d67c1c7976aaf3633&language=en-US"
#     try:
#         response = session.get(url, timeout=5)
#         response.raise_for_status()  # Raise HTTPError for bad responses
#         data = response.json()
#         poster_path = data.get('poster_path')
#         if poster_path:
#             full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
#             poster_cache[movie_id] = full_path
#             return full_path
#         else:
#             st.warning(f"No poster path found for movie ID {movie_id}")
#             return "https://via.placeholder.com/500"
#     except requests.exceptions.RequestException as e:
#         st.error(f"Error fetching poster: {e}")
#         return "https://via.placeholder.com/500"  # Placeholder image in case of error

# def recommend(movie):
#     index = movies[movies['title'] == movie].index[0]
#     distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
#     recommend_movies = []
#     recommend_posters = []
#     for i in distances[1:6]:
#         movie_id = movies.iloc[i[0]].id
#         recommend_movies.append(movies.iloc[i[0]].title)
#         poster_url = fetch_poster(movie_id)
#         recommend_posters.append(poster_url)
#     return recommend_movies, recommend_posters

# # Show recommendations
# if st.button("Show Recommend"):
#     movie_names, movie_posters = recommend(selectValue)
#     cols = st.columns(5)
#     for col, name, poster in zip(cols, movie_names, movie_posters):
#         with col:
#             st.text(name)
#             st.image(poster)


import streamlit as st
import pickle
import requests
import pandas as pd
import sqlite3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Database connection
# conn = sqlite3.connect('movies.db')
# cursor = conn.cursor()

# Load data from database instead of pickle
movies_df = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similartiy.pkl", 'rb'))

movies_list = movies_df['title'].values

# Streamlit app header with custom styling
st.markdown(
    """
    <style>
    .main-header {
        font-size:36px;
        color:#6a1b9a;
        text-align:center;
    }
    .sub-header {
        font-size:24px;
        color:#6a1b9a;
        text-align:center;
    }
    .movie-title {
        font-size:18px;
        font-weight:bold;
        text-align:center;
    }
    .movie-poster {
        display:block;
        margin-left:auto;
        margin-right:auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-header">Movie Recommender System</div>', unsafe_allow_html=True)
selectValue = st.selectbox("Select a movie from the dropdown", movies_list)

# Configure session with retries and exponential backoff
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Local cache for posters
poster_cache = {}

API_KEY = 'da8894704dc5828d67c1c7976aaf3633'  # Replace with your actual TMDB API key

def fetch_poster(movie_id):
    if movie_id in poster_cache:
        return poster_cache[movie_id]
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            poster_cache[movie_id] = full_path
            return full_path
        else:
            st.warning(f"No poster path found for movie ID {movie_id}")
            return "https://via.placeholder.com/500"
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500"

def recommend(movie):
    index = movies_df[movies_df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommend_movies = []
    recommend_posters = []
    for i in distances[1:6]:
        movie_id = movies_df.iloc[i[0]].id
        recommend_movies.append(movies_df.iloc[i[0]].title)
        poster_url = fetch_poster(movie_id)
        recommend_posters.append(poster_url)
    return recommend_movies, recommend_posters

# Show recommendations with loading spinner
if st.button("Show Recommendations"):
    with st.spinner('Fetching recommendations...'):
        movie_names, movie_posters = recommend(selectValue)
        st.markdown('<div class="sub-header">Recommended Movies</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        for col, name, poster in zip(cols, movie_names, movie_posters):
            with col:
                st.image(poster, use_column_width=True)
                st.markdown(f'<div class="movie-title">{name}</div>', unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div style="text-align:center; margin-top: 50px;">
        <p style="font-size:14px;">Developed by Shourya Mittal</p>
    </div>
    """,
    unsafe_allow_html=True
)
