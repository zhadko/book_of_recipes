from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, \
    ListView

from recipes.forms import RecipeForm
from recipes.models import Recipe

__all__ = (
    'RecipeDetailView', 'RecipeCreateView', 'RecipeUpdateView',
    'RecipeDeleteView', 'RecipeListView'
)


class RecipeDetailView(LoginRequiredMixin, DetailView):
    queryset = Recipe.objects.all()
    template_name = 'recipes/detail.html'


class RecipeCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/create.html'
    success_url = reverse_lazy('recipes:home')
    success_message = "Город успешно создан"


class RecipeUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/update.html'
    success_url = reverse_lazy('recipes:home')
    success_message = "Город успешно отредактирован"


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    # template_name = 'cities/delete.html'
    success_url = reverse_lazy('recipes:home')

    def get(self, request, *args, **kwargs):
        messages.success(request, 'Город успешно удален')
        return self.post(request, *args, **kwargs)


class RecipeListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    model = Recipe
    template_name = 'recipes/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = RecipeForm()
        context['form'] = form
        return context
