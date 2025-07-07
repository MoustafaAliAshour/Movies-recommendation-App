import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import os
import streamlit.components.v1 as components

# Download NLTK stopwords once
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load data
def load_data():
    df = pd.read_csv("movies.csv")
    required_columns = ["genres", "keywords", "overview", "title", "cast", "director", "homepage", "vote_average", "vote_count", "popularity", "status", "tagline"]
    df = df[required_columns].dropna().reset_index(drop=True)
    df['combined'] = df['genres'] + ' ' + df['keywords'] + ' ' + df['overview'] + ' ' + df['cast'] + ' ' + df['director']
    return df

# Preprocess and vectorize text
def create_similarity_matrix(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined'])
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return similarity

# Recommendation logic
def recommend(title, df, similarity):
    if title not in df['title'].values:
        return []
    idx = df[df['title'] == title].index[0]
    scores = list(enumerate(similarity[idx]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]  # top 5
    recommendations = [df.iloc[i[0]]['title'] for i in sorted_scores]
    return recommendations

# Show movie details
def show_movie_details(title, df):
    movie = df[df['title'] == title].iloc[0]
    st.markdown(f"## 🎞️ {movie['title']}")
    if movie['tagline']:
        st.markdown(f"*{movie['tagline']}*")
    st.markdown(f"**Genres:** {movie['genres']}")
    st.markdown(f"**Director:** {movie['director']}")
    st.markdown(f"**Cast:** {movie['cast']}")
    st.markdown(f"**Status:** {movie['status']}")
    st.markdown(f"**Popularity:** {movie['popularity']:.2f}")
    st.markdown(f"**Rating:** {movie['vote_average']} ⭐ (based on {movie['vote_count']} votes)")
    st.markdown(f"**Overview:** {movie['overview']}")
    if movie['homepage']:
        st.markdown("### 🌐 Official Homepage")
        st.markdown(f"[Click here]({movie['homepage']})")

# Main Streamlit app
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Navigation
menu = ["Home", "Recommend"]
choice = st.sidebar.selectbox("Navigation", menu)

# Load data
df = load_data()
similarity = create_similarity_matrix(df)

if choice == "Home":
    st.title("🎬 Welcome to the Movie Recommendation System")
    st.markdown("""
        This app helps you discover movies similar to the ones you love.

        - Browse popular titles
        - Get personalized recommendations
        - Click on a title to view more details
    """)
    st.markdown("---")
    st.markdown("**Made by: Moustafa Ali Ashour**")

    st.subheader("Browse Movies")
    movie_selected = st.selectbox("Select a movie to view details:", df['title'].sort_values())
    if movie_selected:
        show_movie_details(movie_selected, df)

elif choice == "Recommend":
    st.title("🎯 Get Recommendations")
    movie_list = df['title'].sort_values().tolist()
    movie_choice = st.selectbox("Select a movie:", movie_list)

    if st.button("Recommend"):
        with st.spinner("Finding similar movies..."):
            results = recommend(movie_choice, df, similarity)
            if results:
                st.success("Top 5 similar movies:")
                for i, movie in enumerate(results, 1):
                    st.markdown(f"---\n**{i}. {movie}**")
                    show_movie_details(movie, df)
            else:
                st.error("Movie not found in the database.")