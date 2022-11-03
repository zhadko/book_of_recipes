from django import forms

from recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    name = forms.CharField(label='Recipe name', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Input name of recipe'
    }))

    photo = forms.ImageField(label='Photo', required=False)
    description = forms.CharField(label='Description', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Description'
    }))

    class Meta:
        model = Recipe
        fields = '__all__'
