from django.db import models


# Create your models here.

# bot_users model
class User(models.Model):
    first_name = models.CharField(max_length=50,
                                  blank=True,
                                  null=True)
    last_name = models.CharField(max_length=50,
                                 blank=True,
                                 null=True)
    username = models.CharField(max_length=100,
                                unique=True,
                                blank=True,
                                null=True)
    name_from_form = models.CharField(max_length=50)

    GENDERS = [
        (1, "man"),
        (2, "woman"),
    ]
    user_gender = models.PositiveSmallIntegerField(choices=GENDERS, unique=False)
    user_id = models.PositiveIntegerField(primary_key=True, unique=True)

    STATES = [
        (1, "start_form"),
        (2, "main_menu"),
        (3, "recipe_menu"),
    ]
    user_state = models.PositiveSmallIntegerField(choices=STATES)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']


# bot_recipes models
class Recipe(models.Model):
    name = models.CharField(max_length=100,
                            unique=True)
    photo = models.ImageField(upload_to='images/recipes',
                              max_length=100,
                              null=True,
                              blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['name']