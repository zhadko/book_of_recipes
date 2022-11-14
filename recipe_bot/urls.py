from django.urls import path

from recipe_bot.views import run_bot

urlpatterns = [
    path('run/', run_bot, name='run_bot'),
]