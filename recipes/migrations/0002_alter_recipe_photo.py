# Generated by Django 4.1.3 on 2022-11-02 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="photo",
            field=models.ImageField(
                height_field=100, upload_to="images/recipes", width_field=100
            ),
        ),
    ]
