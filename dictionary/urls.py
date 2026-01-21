from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('word/<slug:slug>/', views.word_detail, name='word_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('word-letters/<int:count>/', views.words_by_letter_count, name='words_by_letter_count'),
    path('letter/<str:letter>/', views.words_by_letter, name='words_by_letter'),
    path('search/', views.search, name='search'),
]