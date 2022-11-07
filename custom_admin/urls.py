from django.urls import path

from custom_admin.views import *

urlpatterns = [
    path('users/', UsersListView.as_view(), name='home_users'),
    path('recipes/', RecipeListView.as_view(), name='home_recipes'),
    path('detail/<int:pk>/', RecipeDetailView.as_view(), name='detail'),
    path('update/<int:pk>/', RecipeUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', RecipeDeleteView.as_view(), name='delete'),
    path('create/', RecipeCreateView.as_view(), name='create'),
]