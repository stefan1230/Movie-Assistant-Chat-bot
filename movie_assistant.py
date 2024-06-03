import os
import sys
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import tkinter as tk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load movie data from the movies.csv
movies_df = pd.read_csv(resource_path('movies.csv'))

# Initialize NLTK
nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def preprocess(sentence):
    words = word_tokenize(sentence)
    words = [word.lower() for word in words if word.isalnum()]
    words = [word for word in words if word not in stop_words]
    return words

# Add / Update the movies.csv with new fact
def learn_new_fact(question, answer):
    parts = question.split(":", 1)
    movie_title = parts[0].strip()
    attribute = parts[1].strip().lower()

    if attribute not in movies_df.columns:
        return f"Sorry, the attribute '{attribute}' is not recognized."

    movie_index = movies_df[movies_df['title'].str.lower() == movie_title.lower()].index
    if not movie_index.empty:
        movies_df.at[movie_index[0], attribute] = answer
        response = f"Updated {attribute} for {movie_title}."
    else:
        new_movie = {col: '' for col in movies_df.columns}
        new_movie['title'] = movie_title
        new_movie[attribute] = answer
        movies_df.loc[len(movies_df)] = new_movie
        response = f"Added new movie '{movie_title}' with {attribute}."

    movies_df.to_csv(resource_path('movies.csv'), index=False)
    return response

def find_movie(title):
    movie = movies_df[movies_df['title'].str.lower() == title.lower()]
    return movie if not movie.empty else None

def get_movie_info(title):
    movie = find_movie(title)
    if movie is not None:
        info = f"Title: {movie.iloc[0]['title']}\nYear: {movie.iloc[0]['year']}\nDirector: {movie.iloc[0]['director']}\nCast: {movie.iloc[0]['cast']}\nGenre: {movie.iloc[0]['genre']}\nPlot: {movie.iloc[0]['plot']}\nTrivia: {movie.iloc[0]['trivia']}"
        return info
    else:
        return "Sorry, I couldn't find that movie."

def get_movie_attribute(title, attribute):
    movie = find_movie(title)
    if movie is not None:
        return movie.iloc[0][attribute]
    else:
        return None

def get_recommendations_by_genre(genre, num_recommendations=5):
    genre_movies = movies_df[movies_df['genre'].str.contains(genre, case=False, na=False)]
    if not genre_movies.empty:
        recommendations = genre_movies.sample(min(num_recommendations, len(genre_movies)))
        return recommendations['title'].tolist()
    else:
        return []

def get_movies_by_director(director):
    movies_by_director = movies_df[movies_df['director'].str.contains(director, case=False, na=False)]['title'].tolist()
    if movies_by_director:
        return f"Movies directed by {director.title()} include: {', '.join(movies_by_director)}"
    else:
        return f"Sorry, I couldn't find any movies directed by {director.title()}."

def handle_input(user_input):
    tokens = preprocess(user_input)
    user_input_lower = user_input.lower()

    if user_input_lower.startswith("learn:") or user_input_lower.startswith("add fact:"):
        try:
            parts = user_input.split("->")
            question = parts[0].split(":", 1)[1].strip()
            answer = parts[1].strip()
            response = learn_new_fact(question, answer)
            return response
        except Exception as e:
            return "I couldn't understand that. Please use the format 'Learn: [movie_title: attribute] -> [answer]'."

    general_responses = {
        "hi": "Hello! How can I assist you today?",
        "hello": "Hi there! How can I help you with movies?",
        "how are you": "I'm just a bot, but I'm here to assist you with your movie queries!",
        "how can you assist me": "I can provide information about movies, directors, genres, recommendations and more. Just ask me!",
        "what can you do": "I can answer questions about movies, provide plots, director info, genres, recommend movies and more!"
    }
    
    for question, response in general_responses.items():
        if question in user_input_lower:
            return response

    if "directed by" in user_input_lower or "has directed" in user_input_lower:
        try:
            director_index = user_input_lower.index("directed by") + len("directed by")
            director_name = user_input[director_index:].strip()
            return get_movies_by_director(director_name)
        except ValueError:
            try:
                director_index = user_input_lower.index("has directed") + len("has directed")
                director_name = user_input[director_index:].strip()
                return get_movies_by_director(director_name)
            except Exception as e:
                return f"Sorry, I couldn't find any movies directed by that director."

    if "recommend" in user_input_lower or "suggest" in user_input_lower:
        genre_keywords = ['action', 'comedy', 'drama', 'fantasy', 'horror', 'romance']
        for genre in genre_keywords:
            if genre in user_input_lower:
                recommendations = get_recommendations_by_genre(genre)
                return f"I recommend watching: {', '.join(recommendations)}"
        return "Please specify a genre for recommendations."
        
    if ("movies" in tokens or "films" in tokens) and "released" in tokens and any(token.isdigit() for token in tokens):
        year = next(token for token in tokens if token.isdigit())
        movies_in_year = movies_df[movies_df['year'] == int(year)]['title'].tolist()
        if movies_in_year:
            return f"Movies released in {year} include: {', '.join(movies_in_year)}"
        else:
            return f"Sorry, I couldn't find any movies released in {year}."

    if ("movies" in tokens or "films" in tokens) and "released" in tokens and any(token.isdigit() for token in tokens):
        year = next(token for token in tokens if token.isdigit())
        movies_in_year = movies_df[movies_df['year'] == int(year)]['title'].tolist()
        if movies_in_year:
            return f"Movies released in {year} include: {', '.join(movies_in_year)}"
        else:
            return f"Sorry, I couldn't find any movies released in {year}."


    for movie_title in movies_df['title'].str.lower():
        if movie_title in user_input_lower:
            if "plot" in tokens:
                return f"The plot of {movie_title.title()} is: {get_movie_attribute(movie_title, 'plot')}"
            elif "director" in tokens or "directed" in tokens:
                return f"{movie_title.title()} was directed by {get_movie_attribute(movie_title, 'director')}"
            elif "stars" in tokens or "actors" in tokens or "cast" in tokens:
                return f"The main cast of {movie_title.title()} includes: {get_movie_attribute(movie_title, 'cast')}"
            elif "genre" in tokens:
                return f"{movie_title.title()} is a {get_movie_attribute(movie_title, 'genre')} movie"
            elif "trivia" in tokens or "fun fact" in tokens:
                return f"Here's a trivia about {movie_title.title()}: {get_movie_attribute(movie_title, 'trivia')}"
            elif "year" in tokens or "released" in tokens:
                return f"{movie_title.title()} was released in {get_movie_attribute(movie_title, 'year')}"
            else:
                movie_info = get_movie_info(movie_title)
                movie_genre = get_movie_attribute(movie_title, 'genre')
                recommendations = get_recommendations_by_genre(movie_genre)
                additional_msg = f"\nIf you like this, you might also enjoy: {', '.join(recommendations)}"
                return movie_info + additional_msg

    return "I'm not sure how to help with that. Can you ask about a specific movie?"

def send_message():
    user_message = entry.get()
    if user_message.strip() != "":
        create_bubble(user_message, "user")
        response = handle_input(user_message)
        create_bubble(response, "bot")
    entry.delete(0, tk.END)

#GUI creation with tkinker
def create_bubble(message, sender):
    bubble_frame = tk.Frame(chat_log, bg="lightblue" if sender == "bot" else "lightgreen", pady=5, padx=5)
    bubble_label = tk.Label(bubble_frame, text=message, bg="lightblue" if sender == "bot" else "lightgreen", wraplength=400, justify=tk.LEFT if sender == "bot" else tk.RIGHT)
    bubble_label.pack()
    
    chat_log.config(state=tk.NORMAL)
    chat_log.window_create(tk.END, window=bubble_frame)
    chat_log.insert(tk.END, "\n")
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)

root = tk.Tk()
root.title("Movie Assistant Chatbot")

heading_label = tk.Label(root, text="I'm a Movie Expert! Ask me about movies.", font=("Helvetica", 16), pady=10)
heading_label.pack()

chat_frame = tk.Frame(root)
chat_log = tk.Text(chat_frame, state=tk.DISABLED, width=60, height=20, padx=10, pady=10, wrap=tk.WORD)
scrollbar = tk.Scrollbar(chat_frame, command=chat_log.yview)
chat_log['yscrollcommand'] = scrollbar.set

chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

entry_frame = tk.Frame(root)
entry_frame.pack(fill=tk.X, padx=10, pady=10)
entry = tk.Entry(entry_frame, width=50)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(entry_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT)

root.mainloop()
