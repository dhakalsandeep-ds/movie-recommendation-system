from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from math import sqrt

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
     
    directors = models.CharField(max_length=255,default="default")
    movie_logo = models.FileField()
   
    actors = models.CharField(max_length=255,default="default")

    def get_recommendations(self):
        # Query all movies excluding the current one
        all_movies = Movie.objects.exclude(id=self.id).all()

        # Calculate cosine similarity for all movies
        movie_similarities = []
        for movie in all_movies:
            similarity = self.calculate_cosine_similarity(movie)
            movie_similarities.append((movie, similarity))

        # Sort movies by similarity in descending order
        movie_similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top 10 recommendations
        top_recommendations = movie_similarities[:10]

        return top_recommendations

    def calculate_cosine_similarity(self, other_movie):
        # Normalize and split genres, directors, and actors
        genres1 = set(self.genre.lower().strip().split(','))
        genres2 = set(other_movie.genre.lower().strip().split(','))
        directors1 = set(self.directors.lower().strip().split(',')) if self.directors != "default" else set()
        directors2 = set(other_movie.directors.lower().strip().split(',')) if other_movie.directors != "default" else set()
        actors1 = set(self.actors.lower().strip().split(',')) if self.actors != "default" else set()
        actors2 = set(other_movie.actors.lower().strip().split(',')) if other_movie.actors != "default" else set()

        # Calculate cosine similarity for genres
        genre_intersection = len(genres1.intersection(genres2))
        genre_similarity = genre_intersection / sqrt(len(genres1) * len(genres2))

        # Calculate cosine similarity for directors
        director_intersection = len(directors1.intersection(directors2))
        director_similarity = director_intersection / sqrt(len(directors1) * len(directors2))

        # Calculate cosine similarity for actors
        actor_intersection = len(actors1.intersection(actors2))
        actor_similarity = actor_intersection / sqrt(len(actors1) * len(actors2))

        # Combine similarities using average or weighted average
        combined_similarity = (genre_similarity + director_similarity + actor_similarity) / 3.0

        return combined_similarity

    def __str__(self):
        return self.title


    # def get_recommendations(self):
    #     # Query all movies excluding the current one
    #     all_movies = Movie.objects.exclude(id=self.id).all()

    #     # Function to calculate cosine similarity based on genres, directors, and actors
    #     def calculate_cosine_similarity(movie1, movie2):
    #         # Combine genres, directors, and actors into lists
    #         genres1 = set(movie1.genre.split(','))
    #         genres2 = set(movie2.genre.split(','))
    #         directors1 = set(movie1.directors.split(','))
    #         directors2 = set(movie2.directors.split(','))
    #         actors1 = set(movie1.actors.split(','))
    #         actors2 = set(movie2.actors.split(','))

    #         # Calculate cosine similarity for genres
    #         genre_intersection = len(genres1.intersection(genres2))
    #         genre_union = len(genres1.union(genres2))
    #         genre_similarity = genre_intersection / genre_union if genre_union != 0 else 0

    #         # Calculate cosine similarity for directors
    #         director_intersection = len(directors1.intersection(directors2))
    #         director_union = len(directors1.union(directors2))
    #         director_similarity = director_intersection / director_union if director_union != 0 else 0

    #         # Calculate cosine similarity for actors
    #         actor_intersection = len(actors1.intersection(actors2))
    #         actor_union = len(actors1.union(actors2))
    #         actor_similarity = actor_intersection / actor_union if actor_union != 0 else 0

    #         # Combine similarities using average or weighted average
    #         combined_similarity = (genre_similarity + director_similarity + actor_similarity) / 3.0
    #         return combined_similarity

    #     # Calculate similarities for all movies
    #     movie_similarities = [(movie, calculate_cosine_similarity(self, movie)) for movie in all_movies]

    #     print("***************movie_similariteis**************")
    #     print(movie_similarities)
    #     # Sort movies by similarity in descending order
    #     movie_similarities = sorted(movie_similarities, key=lambda x: x[1], reverse=True)
    #     print("*****************sorted**************")
    #     print(movie_similarities)
    #     # Get top 10 recommendations
    #     top_recommendations = [movie for movie, similarity in movie_similarities[:10]]

    #     return movie_similarities[:10]

    # def __str__(self):
    #     return self.title


class Myrating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])


class MyList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watch = models.BooleanField(default=False)

# class UserMoviePreference(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
#     liked = models.BooleanField()

#     def __str__(self):
#         return f"{self.user.username} - {self.movie.title} - {'liked' if self.liked else 'Disklied'}"
