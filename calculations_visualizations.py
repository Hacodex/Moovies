import matplotlib.pyplot as plt
import os
import sqlite3
import numpy as np

def calculate_gender_average_net_worth(db, output_file):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("SELECT gender, AVG(net_worth) FROM actors GROUP BY gender")
    result = cur.fetchall()

    average_net_worth_dict = dict(result)

    genders, average_net_worth = zip(*result)
    plt.bar(genders, average_net_worth, color=['orange', 'blue'])
    plt.xlabel('Gender')
    plt.ylabel('Average Net Worth (in hundreds of millions USD)')
    plt.title('Average Net Worth of Actors by Gender')
    plt.show()

    with open(output_file, 'w') as f:
        f.write("Average Net Worth of Actors by Gender (USD):\n")
        for gender, net_worth in average_net_worth_dict.items():
            f.write(f"{gender}: {net_worth:,.2f}\n")


def calculate_genre_average_rating(db, output_file):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute('''
        SELECT mb.genre, mr.imdb_rating
        FROM movies_basic mb
        JOIN movies_ratings mr ON mb.id = mr.movie_id;
    ''')

    genre_imdb_ratings_dict = {}

    for row in cur.fetchall():
        genres, imdb_rating = row
        genre_list = [genre.strip() for genre in genres.split(',')]
        
        for genre in genre_list:
            if genre not in genre_imdb_ratings_dict:
                genre_imdb_ratings_dict[genre] = []
            genre_imdb_ratings_dict[genre].append(imdb_rating)

    conn.close()

    for genre, ratings in genre_imdb_ratings_dict.items():
        valid_ratings = [rating for rating in ratings if rating != 'N/A']
        if valid_ratings:
            average_rating = sum(valid_ratings) / len(valid_ratings)
            genre_imdb_ratings_dict[genre] = round(average_rating, 2)

    sorted_genres = sorted(genre_imdb_ratings_dict, key=genre_imdb_ratings_dict.get, reverse=True)
    sorted_ratings = [genre_imdb_ratings_dict[genre] for genre in sorted_genres]

    plt.figure(figsize=(12, 8))
    plt.bar(sorted_genres, sorted_ratings, color='red')
    plt.title('Average IMDB Ratings by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Average Rating')
    plt.ylim(0, 10) 
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    with open(output_file, 'a') as f:
        f.write("\nAverage IMDb Ratings by Genre:\n")
        for genre, rating in genre_imdb_ratings_dict.items():
            f.write(f"{genre}: {rating}\n")

 
def calculate_actor_average_imdb_net_worth(db, output_file):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
        CREATE TEMPORARY TABLE temp_actor_ratings AS
        SELECT
            a.name AS actor_name,
            mb.name AS movie_name,
            mr.imdb_rating,
            a.net_worth
        FROM
            actors a
        JOIN
            movies_basic mb ON mb.actors LIKE '%' || a.name || '%'
        JOIN
            movies_ratings mr ON mb.id = mr.movie_id
    """)

    cur.execute("""
        SELECT
            actor_name,
            AVG(imdb_rating) AS average_rating,
            net_worth AS net_worth
        FROM (
            SELECT
                actor_name,
                imdb_rating,
                net_worth
            FROM
                temp_actor_ratings
            GROUP BY
                actor_name, movie_name
        ) AS ordered_data
        GROUP BY
            actor_name
    """)

    result = cur.fetchall()

    cur.close()

    actor_dictionary = {actor: (round(average_rating, 2), net_worth) for actor, average_rating, net_worth in result}

    imdb_ratings = [data[0] for data in actor_dictionary.values()]
    net_worths = [data[1] for data in actor_dictionary.values()]

    coefficients = np.polyfit(imdb_ratings, net_worths, 1)
    polynomial = np.poly1d(coefficients)
    x_values = np.linspace(min(imdb_ratings), max(imdb_ratings), 100)
    y_values = polynomial(x_values)

    plt.scatter(imdb_ratings, net_worths, color='black', label='Data Points')
    plt.plot(x_values, y_values, color='red', label='Regression Line')
    plt.title('Actor Average IMDb Rating of Movies vs. Actor Net Worth')
    plt.xlabel('Average IMDb Rating')
    plt.ylabel('Net Worth (in hundreds of millions USD)')
    plt.legend()
    plt.grid(True)
    plt.show()

    with open(output_file, 'a') as f:
        f.write("\nActor Average IMDb Ratings of Movies and Net Worth:\n")
        for actor, data in actor_dictionary.items():
            f.write(f"{actor}: average IMDb rating: {data[0]}, net worth: {data[1]:,.2f}\n")


def calculate_actors_by_genre(db, output_file):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    genre_actor_counts = {}

    cur.execute('''
        SELECT mb.genre, a.gender
        FROM movies_basic mb
        JOIN actors a ON mb.actors LIKE '%' || a.name || '%';
    ''')

    for row in cur.fetchall():
        genres, gender = row
        genre_list = [genre.strip() for genre in genres.split(',')]
        for genre in genre_list:
            if genre not in genre_actor_counts:
                genre_actor_counts[genre] = {'male': 0, 'female': 0}
            if gender.lower() == 'male':
                genre_actor_counts[genre]['male'] += 1
            elif gender.lower() == 'female':
                genre_actor_counts[genre]['female'] += 1

    conn.close()

    genres = list(genre_actor_counts.keys())
    male_counts = [counts['male'] for counts in genre_actor_counts.values()]
    female_counts = [counts['female'] for counts in genre_actor_counts.values()]
    bar_width = 0.35
    index = range(len(genres))
    plt.grid(True)
    plt.bar(index, male_counts, bar_width, label='Male', color='blue')
    plt.bar([i + bar_width for i in index], female_counts, bar_width, label='Female', color='orange')
    plt.xlabel('Genre')
    plt.ylabel('Number of Actors')
    plt.title('Number of Male and Female Actors by Genre')
    plt.xticks([i + bar_width/2 for i in index], genres, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.show()

    with open(output_file, 'a') as f:
        f.write("\nActors by Genre and Gender:\n")
        for genre, counts in genre_actor_counts.items():
            f.write(f"{genre}: Male: {counts['male']}, Female: {counts['female']}\n")


def main():
    source_dir = os.path.dirname(__file__)
    movie_db = os.path.join(source_dir, "movies_actors.db")
    output_file = os.path.join(source_dir, "calculations_output.txt")

    calculate_gender_average_net_worth(movie_db, output_file)
    calculate_genre_average_rating(movie_db, output_file)
    calculate_actor_average_imdb_net_worth(movie_db, output_file)
    calculate_actors_by_genre(movie_db, output_file)


main()

