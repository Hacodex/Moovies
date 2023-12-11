import requests
import sqlite3

OMDB_BASE_URL = 'http://www.omdbapi.com/?apikey=8faa82b0&'
CELEBRITY_API_KEY = 'nHHghxL40H3mQFv109Z3OQ==R3zun8V9hvpXqSIX'

def fetch_movie_data(movie_name):
    params = {'t': movie_name}
    response = requests.get(OMDB_BASE_URL, params=params)
    return response.json()

def fetch_celebrity_data(celebrity_name):
    headers = {'X-Api-Key': CELEBRITY_API_KEY}
    CELEBRITY_BASE_URL = 'https://api.api-ninjas.com/v1/celebrity?name={}'.format(celebrity_name)
    response = requests.get(CELEBRITY_BASE_URL, headers=headers)
    return response.json()

conn = sqlite3.connect('movies_actors.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS movies_basic (id INTEGER PRIMARY KEY, name TEXT UNIQUE, genre TEXT, actors TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS movies_ratings (movie_id INTEGER, imdb_rating REAL, rotten_tomatoes_rating TEXT, metacritic_rating TEXT, FOREIGN KEY(movie_id) REFERENCES movies_basic(id))''')
c.execute('''CREATE TABLE IF NOT EXISTS actors (name TEXT PRIMARY KEY, gender TEXT, net_worth INTEGER)''')

def insert_movie_data(movie_info):
    c.execute('SELECT id FROM movies_basic WHERE name = ?', (movie_info['Title'],))
    movie_basic_id = c.fetchone()

    if movie_basic_id is None:
        c.execute('INSERT INTO movies_basic (name, genre, actors) VALUES (?, ?, ?)', (movie_info['Title'], movie_info['Genre'], movie_info['Actors']))
        movie_basic_id = c.lastrowid
    else:
        movie_basic_id = movie_basic_id[0]

    c.execute('SELECT movie_id FROM movies_ratings WHERE movie_id = ?', (movie_basic_id,))
    if c.fetchone() is None:
        ratings = movie_info.get('Ratings', [])
        rotten_tomatoes_rating = None
        metacritic_rating = None

        if len(ratings) > 1:
            rotten_tomatoes_rating = ratings[1].get('Value')
        if len(ratings) > 2:
            metacritic_rating = ratings[2].get('Value')

        c.execute('INSERT INTO movies_ratings (movie_id, imdb_rating, rotten_tomatoes_rating, metacritic_rating) VALUES (?, ?, ?, ?)', (movie_basic_id, movie_info['imdbRating'], rotten_tomatoes_rating, metacritic_rating))

def insert_actor_data(actor_info):
    c.execute('SELECT name FROM actors WHERE name = ?', (actor_info['name'],))
    if c.fetchone() is None:
        c.execute('INSERT INTO actors (name, gender, net_worth) VALUES (?, ?, ?)', 
                  (actor_info['name'], actor_info['gender'], actor_info['net_worth']))

def movie_exists(movie_name):
    c.execute('SELECT id FROM movies_basic WHERE name = ?', (movie_name,))
    return c.fetchone() is not None

def actor_exists(actor_name):
    c.execute('SELECT name FROM actors WHERE name = ?', (actor_name,))
    return c.fetchone() is not None

def process_data():
    movie_count = 0
    actor_count = 0

    c.execute('SELECT COUNT(*) FROM movies_basic')
    movie_count = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM actors')
    actor_count = c.fetchone()[0]

    for movie in movies[movie_count:movie_count+25]:
        movie_info = fetch_movie_data(movie)
        if movie_info and 'Title' in movie_info:
            insert_movie_data(movie_info)

    for actor in actors[actor_count:actor_count+25]:
        actor_info = fetch_celebrity_data(actor)
        if actor_info and actor_info[0]:
            insert_actor_data(actor_info[0])

    conn.commit()

movies = ["The Shawshank Redemption", "The Godfather", "The Godfather Part II", "The Dark Knight", "12 Angry Men", "Schindler's List", "The Lord of the Rings: The Return of the King", "Pulp Fiction", "The Good, the Bad and the Ugly", "Fight Club", "Forrest Gump", "Inception", "The Lord of the Rings: The Fellowship of the Ring", "Star Wars: Episode V - The Empire Strikes Back", "The Lord of the Rings: The Two Towers", "Interstellar", "City of God", "Spirited Away", "Saving Private Ryan", "The Green Mile", "Life Is Beautiful", "Se7en", "The Silence of the Lambs", "It's a Wonderful Life", "Parasite", "Avengers: Infinity War", "Whiplash", "The Intouchables", "The Prestige", "The Departed", "The Pianist", "Gladiator", "American History X", "The Usual Suspects", "Léon: The Professional", "Psycho", "Casablanca", "The Lion King", "Back to the Future", "The Empire Strikes Back", "The Matrix", "Goodfellas", "One Flew Over the Cuckoo's Nest", "Seven Samurai", "City Lights", "The Great Dictator", "Cinema Paradiso", "Modern Times", "Apocalypse Now", "Raiders of the Lost Ark", "The Shining", "Amélie", "Alien", "The Lives of Others", "Lawrence of Arabia", "A Clockwork Orange", "Double Indemnity", "Taxi Driver", "Eternal Sunshine of the Spotless Mind", "Rear Window", "The Third Man", "The Treasure of the Sierra Madre", "Dr. Strangelove", "To Kill a Mockingbird", "Vertigo", "North by Northwest", "Full Metal Jacket", "Singin' in the Rain", "Some Like It Hot", "The Bridge on the River Kwai", "Memento", "The Apartment", "Sunset Boulevard", "For a Few Dollars More", "Metropolis", "A Space Odyssey", "The Grand Budapest Hotel", "The Great Escape", "The Gold Rush", "Raging Bull", "Chinatown", "Once Upon a Time in the West", "Das Boot", "The Sting", "Monty Python and the Holy Grail", "Rebel Without a Cause", "The Maltese Falcon", "Jaws", "The Thing", "Rocky", "The Graduate", "The Wizard of Oz", "Toy Story", "Blade Runner", "Fargo", "No Country for Old Men", "The Big Lebowski", "Pan's Labyrinth", "Her", "Mad Max: Fury Road", "Aliens", "Braveheart", "Gone with the Wind", "A Beautiful Mind", "Catch Me If You Can", "La La Land", "Shutter Island", "The Truman Show", "Django Unchained", "The Wolf of Wall Street", "The Social Network", "The Great Gatsby", "Black Swan", "The Imitation Game", "Slumdog Millionaire", "The King's Speech", "Birdman", "Moonlight", "Little Women", "The Shape of Water"]
actors = ["Meryl Streep", "Tom Hanks", "Leonardo DiCaprio", "Oprah Winfrey", "Brad Pitt", "Angelina Jolie", "Johnny Depp", "Jennifer Lawrence", "George Clooney", "Julia Roberts", "Robert De Niro", "Scarlett Johansson", "Morgan Freeman", "Tom Cruise", "Nicole Kidman", "Steven Spielberg", "Halle Berry", "Hugh Jackman", "Cate Blanchett", "Denzel Washington", "Emma Stone", "Ryan Gosling", "Sandra Bullock", "Will Smith", "Natalie Portman", "Matt Damon", "Christian Bale", "Charlize Theron", "Kate Winslet", "Jennifer Aniston", "Chris Hemsworth", "Jessica Chastain", "Matthew McConaughey", "Anne Hathaway", "Bradley Cooper", "Keanu Reeves", "Margot Robbie", "Daniel Day-Lewis", "Al Pacino", "Amy Adams", "Joaquin Phoenix", "Ryan Reynolds", "Emma Watson", "Gwyneth Paltrow", "Daniel Craig", "Sofia Vergara", "Reese Witherspoon", "Jake Gyllenhaal", "Natalie Wood", "Benedict Cumberbatch", "Cameron Diaz", "Sean Connery", "Mila Kunis", "Robert Downey Jr.", "Russell Crowe", "James Franco", "Naomi Watts", "Samuel L. Jackson", "Penelope Cruz", "Harrison Ford", "Michael Fassbender", "Marion Cotillard", "Jennifer Lopez", "Vin Diesel", "Michelle Pfeiffer", "Eddie Murphy", "Arnold Schwarzenegger", "Jamie Foxx", "Julianne Moore", "Mark Wahlberg", "Hugh Grant", "Viola Davis", "Sylvester Stallone", "Sigourney Weaver", "Clint Eastwood", "Diane Keaton", "Adam Sandler", "Uma Thurman", "Bill Murray", "Mel Gibson", "Drew Barrymore", "Ewan McGregor", "Nicolas Cage", "Salma Hayek", "Jessica Lange", "Steve McQueen", "Liam Neeson", "Zoe Saldana", "Kevin Spacey", "Kristen Stewart", "Tommy Lee Jones", "Bruce Willis", "Julie Andrews", "Michael Douglas", "John Travolta", "Woody Allen", "Kirk Douglas", "Grace Kelly", "Frank Sinatra", "Audrey Hepburn", "Lucille Ball", "Marilyn Monroe", "James Dean", "Lauren Bacall", "Bette Davis", "Marlon Brando", "Cary Grant", "Humphrey Bogart", "Elizabeth Taylor"]

process_data()

conn.close()