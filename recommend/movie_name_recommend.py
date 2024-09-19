import math

def preprocess_features(movie):
    """
    Extract features from a movie instance and return them as a list.
    """
    # + movie.actors.split(', ') + [movie.director]
    return movie.genre.split(', ') 

def create_feature_matrix(movies):
    """
    Create a feature matrix for a list of movies. Each movie's features are represented
    as a binary vector.
    """
    features = [preprocess_features(movie) for movie in movies]
    
    # Get a unique list of all features
    unique_features = set(feature for sublist in features for feature in sublist)
    
    # Create a mapping from feature to index
    feature_to_index = {feature: idx for idx, feature in enumerate(unique_features)}
    
    # Create binary vectors for each movie
    vectors = []
    for feature_list in features:
        vector = [0] * len(unique_features)
        for feature in feature_list:
            vector[feature_to_index[feature]] = 1
        vectors.append(vector)
    
    return vectors, feature_to_index

def dot_product(vector1, vector2):
    """
    Compute the dot product of two vectors.
    """
    return sum(a * b for a, b in zip(vector1, vector2))

def magnitude(vector):
    """
    Compute the magnitude (Euclidean norm) of a vector.
    """
    return math.sqrt(sum(a * a for a in vector))

def cosine_similarity(vector1, vector2):
    """
    Compute the cosine similarity between two vectors.
    """
    dot_prod = dot_product(vector1, vector2)
    mag1 = magnitude(vector1)
    mag2 = magnitude(vector2)
    if mag1 == 0 or mag2 == 0:  # To handle zero magnitude vectors
        return 0.0
    return dot_prod / (mag1 * mag2)

def calculate_similarity(vectors):
    """
    Calculate the cosine similarity matrix for a list of vectors.
    """
    n_movies = len(vectors)
    similarity_matrix = [[0.0] * n_movies for _ in range(n_movies)]
    for i in range(n_movies):
        for j in range(n_movies):
            similarity_matrix[i][j] = cosine_similarity(vectors[i], vectors[j])
    return similarity_matrix

def get_recommendations(movie_title, movies, similarity_matrix):
    """
    Get a list of movie recommendations based on a given movie title.
    """
    movie_titles = [movie.title for movie in movies]
    movie_titles_lower = [title.lower() for title in movie_titles]
    print(movie_titles_lower)
    print(movie_titles)
    print(movie_title.lower())
    if movie_title.lower() not in movie_titles_lower:
        return []

    idx = movie_titles.index(movie_title)
    print(idx)
    # Get similarity scores for the given movie
    sim_scores = list(enumerate(similarity_matrix[idx]))
    
    # Sort the scores in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    print(sim_scores)
    
    # Get the indices of the top 10 most similar movies (excluding the movie itself)
    sim_scores = sim_scores[1:11]  # Skip the first one because it's the movie itself
    
    movie_indices = [i[0] for i in sim_scores]
    
    return [movies[i] for i in movie_indices]
