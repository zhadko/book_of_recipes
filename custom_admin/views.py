from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView

from custom_admin.forms import RecipeForm
from custom_admin.models import User, Recipe

__all__ = (
    'UsersListView', 'RecipeDetailView', 'RecipeCreateView', 'RecipeUpdateView',
    'RecipeDeleteView', 'RecipeListView'
)


class UsersListView(LoginRequiredMixin, ListView):
    paginate_by = 10
    model = User
    template_name = 'custom_admin/home_users.html'


class RecipeDetailView(LoginRequiredMixin, DetailView):
    queryset = Recipe.objects.all()
    template_name = 'custom_admin/detail.html'


class RecipeCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'custom_admin/create.html'
    success_url = reverse_lazy('custom_admin:home_recipes')
    success_message = "The Recipe was created successfully"


class RecipeUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'custom_admin/update.html'
    success_url = reverse_lazy('custom_admin:home_recipes')
    success_message = "The Recipe was updated successfully"


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy('custom_admin:home_recipes')

    def get(self, request, *args, **kwargs):
        messages.success(request, 'The Recipe was deleted successfully')
        return self.post(request, *args, **kwargs)


class RecipeListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    model = Recipe
    template_name = 'custom_admin/home_recipes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = RecipeForm()
        context['form'] = form
        return context
