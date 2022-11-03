from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView


from bot_users.models import User


# Create your views here.
class UsersListView(LoginRequiredMixin, ListView):
    paginate_by = 10
    model = User
    template_name = 'bot_users/home.html'
