from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.http import Http404
from .models import Movie, Myrating, MyList
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Case, When
from .cosine_similarity import recommend_movies
from django.contrib.auth.decorators import login_required
from .trie import Trie
from django.contrib.auth.forms import AuthenticationForm


_trie_instance = None 

_content_based_filtering_trie = None

def set_content_based_filtering_trie(trie):
    global _content_based_filtering_trie
    _content_based_filtering_trie = trie

def set_trie_instance(trie):
    global _trie_instance 
    _trie_instance = trie

# def try_view(request):
#     movies = Movie.objects.all()
#     return render(request,"recommend/test2.html",{"movies":movies})




# def search(request):
#     query = request.GET.get('q','')
#     if query:
#         movies = Movie.objects.filter(title__icontains=query)
#     else: 
#         movies = Movie.objects.none()
#     return render(request,"recommend/search_result.html",{"movies":movies,"query":query})

def autosuggestion(request):
    global _trie_instance 
    if _trie_instance is None:
        return HttpResponse("Trie not initlaized")
    prefix = request.GET.get('q','')
    # page_number = request.GET.get('p',1)
    # print("*********page**********")
    # print(request.GET.get('page',"otherwise no page number"),request.GET)
    search_results = _trie_instance.search(prefix.lower())
    print('*******************search+results***********')
    print(search_results)
    context ={
        'movies':search_results
    }
    return render(request,"recommend/search_result.html",context)

   
def search(request):
    global _content_based_filtering_trie
    if _content_based_filtering_trie is None:
        return HttpResponse("Trie not initlaized")
    prefix = request.GET.get('q','')
    page_number = request.GET.get('p',1)
    print("*********page**********")
    print(request.GET.get('page',"otherwise no page number"),request.GET)
    search_results = _content_based_filtering_trie.search(prefix.lower())
    context ={
        'movies':search_results
    }
    return render(request,"recommend/search_result.html",context)

def try_view(request):
    movies = Movie.objects.all()
    return render(request,"recommend/test2.html",{"movies":movies})


def custom_admin_login(request):
    if request.method == 'GET' and request.user.is_active and request.user.is_staff:
        return redirect('/admin/')
    # if (request.user):
    #     return redirect('/admin/')
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            username = user.username 
            user = authenticate(request,username=username,password=password)

            if user is not None:
                login(request,user)
                return redirect('/admin/')
            else:
                messages.error(request,"Invalid login credentials")
        except User.DoesNotExist:
            messages.error(request,"No user with that email")
    form = AuthenticationForm()
    context = {
        'form':form,
        'site_header':"movie recommendation adminstration",
        'site_title':"moie recommendation site admin",
        'subtitle':'login'
    }

    return render(request,'admin/login.html',context)





def index(request):
    movies = Movie.objects.all()
    query = request.GET.get('q')
    page_number = int(request.GET.get('p', 1))
    items_per_page = 12

    if query:
        movies = Movie.objects.filter(
    Q(title__icontains=query) |
    Q(genre__icontains=query) |
    Q(directors__icontains=query) |
    Q(actors__icontains=query)
).distinct()

    total_movies = movies.count()
    num_pages = (total_movies + items_per_page - 1) // items_per_page  # Total number of pages

    # Slicing movies for the current page
    start = (page_number - 1) * items_per_page
    end = start + items_per_page
    movies = movies[start:end]

    # Generate page_range for pagination links
    if num_pages <= 5:
        page_range = range(1, num_pages + 1)
    else:
        if page_number <= 3:
            page_range = range(1, 6)
        elif page_number >= num_pages - 2:
            page_range = range(num_pages - 4, num_pages + 1)
        else:
            page_range = range(page_number - 2, page_number + 3)
    print("movies",movies)
    context = {
        'movies': movies,
        'page_number': page_number,
        'page_range': page_range,
        'num_pages': num_pages
    }
    print("request.user  >>>>>>>>>,<<<<<<<<<<<<<", request.user,type(request.user),dir(request.user),"user name ",request.user.is_anonymous)
    return render(request, 'recommend/list.html', context)


def recommendations_view(request):
    recommend_movies = recommend_movies(request.user)
    return render(request, 'recommend/recommendations.html',{'movies':recommend_movies})


# Show details of the movie
def detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    movies = get_object_or_404(Movie, id=movie_id)
    movie = Movie.objects.get(id=movie_id)
    
    temp = list(MyList.objects.all().values().filter(movie_id=movie_id,user=request.user))
    if temp:
        update = temp[0]['watch']
    else:
        update = False
    if request.method == "POST":

        # For my list
        if 'watch' in request.POST:
            watch_flag = request.POST['watch']
            if watch_flag == 'on':
                update = True
            else:
                update = False
            if MyList.objects.all().values().filter(movie_id=movie_id,user=request.user):
                MyList.objects.all().values().filter(movie_id=movie_id,user=request.user).update(watch=update)
            else:
                q=MyList(user=request.user,movie=movie,watch=update)
                q.save()
            if update:
                messages.success(request, "Movie added to your list!")
            else:
                messages.success(request, "Movie removed from your list!")

            
        # For rating
        else:
            rate = request.POST['rating']
            if Myrating.objects.all().values().filter(movie_id=movie_id,user=request.user):
                Myrating.objects.all().values().filter(movie_id=movie_id,user=request.user).update(rating=rate)
            else:
                q=Myrating(user=request.user,movie=movie,rating=rate)
                q.save()

            messages.success(request, "Rating has been submitted!")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    out = list(Myrating.objects.filter(user=request.user.id).values())

    # To display ratings in the movie detail page
    movie_rating = 0
    rate_flag = False
    for each in out:
        if each['movie_id'] == movie_id:
            movie_rating = each['rating']
            rate_flag = True
            break
    
    recommend_movies = Movie.objects.get(id=movie_id).get_recommendations()
    context = {'movies': movies,'movie_rating':movie_rating,'rate_flag':rate_flag,'update':update,'recommend':recommend_movies}
    return render(request, 'recommend/detail.html', context)


# MyList functionality
def watch(request):

    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    movies = Movie.objects.filter(mylist__watch=True,mylist__user=request.user)
    query = request.GET.get('q')

    if query:
        movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
        return render(request, 'recommend/watch.html', {'movies': movies})

    return render(request, 'recommend/watch.html', {'movies': movies})


# To get similar movies based on user rating
def get_similar(movie_name,rating,corrMatrix):
    similar_ratings = corrMatrix[movie_name]*(rating-2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    return similar_ratings

# Recommendation Algorithm
# def recommend(request):
#     # return "<p> hello </p>"
   
#     if not request.user.is_authenticated:
#         return redirect("login")
#     if not request.user.is_active:
#         raise Http404

    
#     # print(print(list(Myrating.objects.all().values())))
    
#     movie_rating=pd.DataFrame(list(Myrating.objects.all().values()))
 
#     # print(movie_rating.user_id.unique())
#     new_user=movie_rating.user_id.unique().shape[0]
#     # print(new_user)
#     current_user_id= request.user.id
#     # print(current_user_id)
# 	# if new user not rated any movie
#     if current_user_id>new_user:
#         movie=Movie.objects.get(id=19)
#         q=Myrating(user=request.user,movie=movie,rating=0)
#         q.save()


#     userRatings = movie_rating.pivot_table(index=['user_id'],columns=['movie_id'],values='rating')
#     # print(userRatings)
#     userRatings = userRatings.fillna(0,axis=1)
#     corrMatrix = userRatings.corr(method='pearson')

#     user = pd.DataFrame(list(Myrating.objects.filter(user=request.user).values())).drop(['user_id','id'],axis=1)
#     user_filtered = [tuple(x) for x in user.values]
#     movie_id_watched = [each[0] for each in user_filtered]

#     similar_movies = pd.DataFrame()
#     for movie,rating in user_filtered:
#         similar_movies = pd.concat([similar_movies, get_similar(movie, rating, corrMatrix)], ignore_index=True)

#     # print("similar_movies",similar_movies)
#     movies_id = list(similar_movies.sum().sort_values(ascending=False).index)
#     # print("movies_id",movies_id)
#     movies_id_recommend = [each for each in movies_id if each not in movie_id_watched]
#     # print("movies_id_recommend",movies_id_recommend)
#     preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(movies_id_recommend)])
#     # print("prserved", preserved)
#     movie_list=list(Movie.objects.filter(id__in = movies_id_recommend).order_by(preserved)[:10])
#     # print("movie list*****************",movie_list)
#     context = {'movie_list': movie_list}
#     return render(request, 'recommend/recommend.html', context)


# Register user
def signUp(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.email = email
        user.save()
        user = authenticate(username=user.username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")

    context = {'form': form}

    return render(request, 'recommend/signUp.html', context)


# Login User
def Login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        # username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            user = authenticate(username=user.username, password=password)
            
            if user is not None and user.is_active:
                login(request, user)
                return redirect("index")
            else:
                return render(request, 'recommend/login.html', {'error_message': 'Your account disable'})
        else:
            return render(request, 'recommend/login.html', {'error_message': 'Invalid Login'})

    return render(request, 'recommend/login.html')


# Logout user
def Logout(request):
    logout(request)
    return redirect("login")


# def user_based_collaborative_filtering(request):
#     # Get current user's ratings
#     print(request.user)
#     print(list(Myrating.objects.filter(user=request.user.id).values()))
#     user_ratings = pd.DataFrame(list(Myrating.objects.filter(user=request.user).values()))
#     print("user_ratings",user_ratings)
    
#     # Compute user similarities (example implementation)
#     # Example: calculate similarity matrix based on cosine similarity
#     user_similarity_matrix = compute_user_similarity(user_ratings)
#     print("user_similarity_matrix",user_similarity_matrix)
    
#     # Get recommendations for current user
#     recommendations = get_recommendations(request.user, user_similarity_matrix)
    
#     context = {'recommendations': recommendations}
#     return render(request, 'recommendations.html', context)

# def compute_user_similarity(user_ratings):
#     # Compute similarity matrix (example implementation)
#     # Example: using pandas and numpy to compute cosine similarity
#     user_ratings_pivot = user_ratings.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
#     print("user_ratings_pivot",user_ratings_pivot)
#     similarity_matrix = user_ratings_pivot.corr(method='pearson')
    
#     return similarity_matrix

# def get_recommendations(user, similarity_matrix):
#     # Get recommendations for the user based on similarity matrix
#     # Example: recommend items based on highest similarity with other users
  
#     similar_users = similarity_matrix[user.id].sort_values(ascending=False).index[1:]  # Exclude self
#     recommendations = []
    
#     for user_id in similar_users:
#         similar_user_ratings = Myrating.objects.filter(user_id=user_id).exclude(movie__in=user.myrating_set.values_list('movie_id', flat=True))
#         for rating in similar_user_ratings:
#             recommendations.append(rating.movie)
#         if len(recommendations) >= 10:
#             break
    
#     return recommendations[:10]
from django.urls import reverse

@login_required
def cosine_recommend(request):
    print("cosine _recommend ....................")
    title = request.GET.get('q',None)
    print("*************title**********")
    print(title)
    if title == None: 
        suggestions = recommend_movies(request)


    
        user = User.objects.get(id=request.user.id)
        context = {
            'user': user,
            'movie_list': suggestions
        }
        print("request user >>>>>>>>>>>>>>>>>>", request.user)
        return render(request, 'recommend/recommend.html', context)

    # Query the Movie model to get the movie object by title
    # movie = get_object_or_404(Movie, Q(title__iexact=title))
    movie = Movie.objects.filter(Q(title__iexact=title)).first()
    if movie is None:
        recommendations = "no similar movies"
        find = False
    else:
        recommendations = movie.get_recommendations()
        find = True
        # Get recommendations using the get_recommendations() method
    # recommendations = movie.get_recommendations()
    print("i am here...............")
    # print(recommendations)
    context = {'movie_list': recommendations, find:find}
    print("request user .>>>>>>>>>>>>>>>>>" ,request.user)
    return render(request, 'recommend/recommend.html', context)
    



    

from .movie_name_recommend import create_feature_matrix, calculate_similarity, get_recommendations

from django.db.models import Q

@login_required
def rmovies(request):
    # print(movie_title)
    title = request.GET.get('q',"avatar")
    # title = request.GET.get('title', None)
        
    if title:
        # Query the Movie model to get the movie object by title
        movie = get_object_or_404(Movie, Q(title__iexact=title))
        
        # Get recommendations using the get_recommendations() method
        recommendations = movie.get_recommendations()
    print(recommendations)
    context = {'movie_list': recommendations}
    return render(request, 'recommend/recommend.html', context)


def profiles(request):
    print(request.user.email)
    print(request.user.username)
    return render(request, "recommend/profile.html")

def change(request):
    
    return render(request,"recommend/change.html")