# Generated by Django 4.1.3 on 2022-11-30 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("custom_admin", "0004_alter_user_name_from_form_alter_user_user_gender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="user_state",
            field=models.PositiveSmallIntegerField(
                choices=[
                    ("start_form", "start_form"),
                    ("main_menu", "main_menu"),
                    ("recipe_menu", "recipe_menu"),
                ]
            ),
        ),
    ]