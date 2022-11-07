from django import forms

from custom_admin.models import Recipe


class RecipeForm(forms.ModelForm):
    name = forms.CharField(label='Recipe name', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Input name of recipe'
    }))

    photo = forms.ImageField(label='Photo', required=False)
    description = forms.CharField(label='Description of the recipe', widget=forms.Textarea(attrs={"rows": "5"}))

    class Meta:
        model = Recipe
        fields = '__all__'
