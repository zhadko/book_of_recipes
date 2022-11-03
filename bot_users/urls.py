from django.urls import path

from bot_users.views import UsersListView

urlpatterns = [
    path('', UsersListView.as_view(), name='home'),
]