from django.db import models


# Create your models here.
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
