from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from recipe_bot.views import TutorialBotView

urlpatterns = [
    path('run/', csrf_exempt(TutorialBotView.as_view()), name='run_bot'),
]