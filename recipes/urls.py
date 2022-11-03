from django.urls import path

from recipes.views import *

urlpatterns = [
    path('', RecipeListView.as_view(), name='home'),
    path('detail/<int:pk>/', RecipeDetailView.as_view(), name='detail'),
    path('update/<int:pk>/', RecipeUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', RecipeDeleteView.as_view(), name='delete'),
    path('create/', RecipeCreateView.as_view(), name='create'),
]