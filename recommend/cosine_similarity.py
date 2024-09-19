from .models import Movie, Myrating
import math
from django.contrib.auth.models import User 

def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0

def get_user_ratings(user):
    return {rating.movie.id: rating.rating for rating in Myrating.objects.filter(user=user)}

def get_all_users(current_user):
    return User.objects.exclude(id=current_user.id)

def calculate_user_similarity(current_user_ratings, other_user_ratings):
    shared_movies = set(current_user_ratings.keys()).intersection(set(other_user_ratings.keys())) # {movie_id1, movie_id2} n {movie_id3, movie_id1} = {movie_id1}

    if shared_movies:
        current_user_vector = [current_user_ratings[movie_id] for movie_id in shared_movies]
        other_user_vector = [other_user_ratings[movie_id] for movie_id in shared_movies]

        similarity = cosine_similarity(current_user_vector, other_user_vector)
        return similarity, other_user_ratings
    return None, None

def calculate_similarity_scores(current_user_ratings, all_users):
    similarity_scores = []
    for user in all_users:

        other_user_ratings = get_user_ratings(user)
        print("current user rating .......",current_user_ratings)
        similarity, ratings = calculate_user_similarity(current_user_ratings, other_user_ratings)
        print("similarity score for ............", similarity, ratings)
        if similarity is not None:
            similarity_scores.append((similarity, ratings))
    
    similarity_scores.sort(key=lambda x:x[0], reverse=True)
    return similarity_scores

def calculate_movie_scores(similarity_scores, current_user_ratings):
    movie_scores = {}
    for similarity, ratings in similarity_scores:
        for movie_id, rating in ratings.items():
            if movie_id not in current_user_ratings:
                if movie_id not in movie_scores:
                    movie_scores[movie_id] = (0, 0)
                movie_scores[movie_id] = (movie_scores[movie_id][0] + similarity * rating, movie_scores[movie_id][1] + similarity)
    return movie_scores

def get_recommendations(movie_scores):
    recommendations = [
        (Movie.objects.get(id=movie_id), score / weight) 
        for movie_id, (score, weight) in movie_scores.items() 
        if weight > 0
    ]
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations


def recommend_movies(request):
    current_user_ratings = get_user_ratings(request.user) # {movie_id: rating}
    print("current_user_ratings ..................... ", current_user_ratings)
    all_users = get_all_users(request.user) # <QuerySet [<User: prerak>, <User: awesome>]
    print("all users ............ ", all_users)

    similarity_scores = calculate_similarity_scores(current_user_ratings, all_users)
    print("similarity scores .........",similarity_scores)
    movie_scores = calculate_movie_scores(similarity_scores, current_user_ratings)
    print("movie_scores ......... ", movie_scores)
    recommendations = get_recommendations(movie_scores)
    return recommendations



