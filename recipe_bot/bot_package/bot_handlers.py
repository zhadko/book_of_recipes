from .main import bot
from .messages import *
from .markups import *
import traceback

from custom_admin.models import User, Recipe


@bot.message_handler(state='*', commands=['start'])
def start(message):
    if User.objects.filter(user_id=message.from_user.id).exists():
        bot.send_message(message.from_user.id, WELCOME)
        user = User.objects.filter(user_id=message.from_user.id).last()
        User.objects.filter(user_id=message.from_user.id).last()
        if user.user_state == "name_form":
            bot.send_message(message.from_user.id, NAME_QUESTION)
        elif user.user_state == "gender_form":
            bot.send_message(message.from_user.id, GENDER_QUESTION, reply_markup=gender_markup)
        elif user.user_state == "main_menu":
            bot.send_message(message.from_user.id, MAIN_MENU, reply_markup=menu)
        elif user.user_state == "recipe_menu":
            bot.send_message(message.from_user.id, CHOOSE_RECIPE, reply_markup=recipes_markup())
    else:
        User.objects.create(user_id=message.from_user.id,
                            username=message.from_user.username,
                            first_name=message.from_user.first_name,
                            last_name=message.from_user.last_name,
                            user_state="name_form")
        bot.send_message(message.from_user.id, HELLO_MESS)


@bot.message_handler(state="name_form")
def get_name(message):
    if message.text.isalpha():
        User.objects.filter(user_id=message.from_user.id).update(name_from_form=message.text, user_state="gender_form")
        bot.send_message(message.from_user.id, GENDER_QUESTION, reply_markup=gender_markup)
    else:
        bot.send_message(message.from_user.id, INVALID_NAME)
        bot.send_message(message.from_user.id, ENTER_VALID_NAME)


@bot.callback_query_handler(state="gender_form", func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == GENDER['man'] or call.data == GENDER['woman']:
                gender = call.data
                gender_id = 1 if gender == GENDER['man'] else 2

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=THANKS,
                                      reply_markup=None)
                User.objects.filter(user_id=call.message.chat.id).update(user_gender=gender_id, user_state="main_menu")

                bot.send_message(call.message.chat.id, USER_CREATED, reply_markup=menu)
    except Exception as e:
        bot.send_message(call.message.chat.id, CALL_ERROR,
                         reply_markup=start)
        print('Error:\n', traceback.format_exc())


@bot.message_handler(state="main_menu")
def handled_text(message):
    if message.text == ABOUT:
        user = User.objects.filter(user_id=message.chat.id).last()
        gender = GENDER['man'] if user.user_gender == 1 else GENDER['woman']
        bot.send_message(message.from_user.id, ABOUT_ANSWER.format(name=user.name_from_form, gender=gender))
    elif message.text == RECIPES:
        user = User.objects.filter(user_id=message.chat.id)
        bot.send_message(message.from_user.id, CHOOSE_RECIPE, reply_markup=recipes_markup())
        user.update(user_state="recipe_menu")
    elif message.text == RE_ENTER:
        user = User.objects.filter(user_id=message.chat.id)
        bot.send_message(message.from_user.id, NAME_QUESTION)
        user.update(user_state="name_form")


@bot.message_handler(state="recipe_menu")
def recipe_view(message):
    if message.text == BACK:
        bot.send_message(message.from_user.id, MAIN_MENU, reply_markup=menu)
        User.objects.filter(user_id=message.chat.id).update(user_state="main_menu")
    else:
        if Recipe.objects.filter(name=message.text).exists():
            recipe = Recipe.objects.filter(name=message.text).last()
            bot.send_chat_action(message.from_user.id, 'upload_photo')
            if recipe.photo:
                bot.send_photo(message.from_user.id, recipe.photo)
                bot.send_message(message.from_user.id, recipe.description)
            else:
                bot.send_message(message.from_user.id, recipe.description)
            recipes_markup()
        else:
            bot.send_message(message.from_user.id, INVALID_RECIPE)
            User.objects.filter(user_id=message.chat.id).update(user_state="recipe_menu")
