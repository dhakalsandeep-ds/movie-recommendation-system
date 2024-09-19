from django.urls import path
from . import views



urlpatterns = [
    path('change/',views.change,name="change"),
    path('profile/',views.profiles,name="profile"),
    path('', views.index, name='index'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('<int:movie_id>/', views.detail, name='detail'),
    path('watch/', views.watch, name='watch'),
    path('recommend/', views.cosine_recommend, name='recommend'),
    # path('rmovies/', views.rmovies, name='lame'),
    path('try/',views.try_view, name="try"),
    # path('reo/',views.user_recommendations),
   path('auto/',views.autosuggestion,name="auto"),
   path('search/',views.search,name='search')]
