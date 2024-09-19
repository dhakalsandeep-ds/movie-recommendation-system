from django.apps import AppConfig
from .trie import Trie


class RecommendConfig(AppConfig):
    name = 'recommend'

    def ready(self):
        
        from .models import Movie  # Import inside the ready method
        from .views import set_trie_instance, set_content_based_filtering_trie
        trie = Trie()  # Initialize Trie instance
        content_trie = Trie()
        movies = Movie.objects.all()
        for movie in movies:
            trie.insert(movie.title.lower())
            content_trie.insert(movie.title.lower())
            for genre in movie.genre.split(','):
                content_trie.insert(genre.strip().lower())
    
    # Insert directors
            for director in movie.directors.split(','):
                content_trie.insert(director.strip().lower())
    
            # Insert actors
            for actor in movie.actors.split(','):
                content_trie.insert(actor.strip().lower())
        set_trie_instance(trie)
        set_content_based_filtering_trie(content_trie)
        print("**********************************content_trie*************************************")
        content_trie.print_all_words()