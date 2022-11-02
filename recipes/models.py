from django.db import models


# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=100,
                            unique=True)
    photo = models.ImageField(upload_to='images/recipes',
                              max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['name']