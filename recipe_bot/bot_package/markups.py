import os

import django
from telebot import types

os.environ['DJANGO_SETTINGS_MODULE'] = 'book_of_recipes.settings'
django.setup()

from custom_admin.models import Recipe

gender_markup = types.InlineKeyboardMarkup(row_width=1)
btn1 = types.InlineKeyboardButton('Man', callback_data='Man')
btn2 = types.InlineKeyboardButton('Woman', callback_data='Woman')
gender_markup.add(btn1, btn2)

menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn1 = types.KeyboardButton('About me')
btn2 = types.KeyboardButton('Recipes')
btn3 = types.KeyboardButton('Re-enter the data')
menu.add(btn1, btn2, btn3)


def recipes_markup():
    recipes = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for el in list(Recipe.objects.all()):
        recipes.add(types.KeyboardButton(el.name))
    recipes.add(types.KeyboardButton('Back to menu'))
    return recipes
