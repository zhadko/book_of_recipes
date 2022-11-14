import telebot
import os
from rest_framework.response import Response
from django.http import HttpResponse
from django.views import View
from flask import Flask, request
import logging
from recipe_bot.main import bot, MyStates
from recipe_bot.messages import *
from recipe_bot.markups import *
import traceback
from django.conf import settings
from custom_admin.models import Recipe, User


class UpdateBot(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Бот запусчен и работает.")

    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])

        return Response({'code': 200})


@bot.message_handler(state='*', commands=['start'])
def start(message):
    if User.objects.filter(user_id=message.from_user.id).exists():
        bot.send_message(message.from_user.id, WELCOME)
        user = User.objects.filter(user_id=message.from_user.id).last()
        if user.user_state == 1:
            bot.set_state(message.from_user.id, MyStates.reg, message.chat.id)
            bot.send_message(message.from_user.id, NAME_QUESTION)
        elif user.user_state == 2:
            bot.set_state(message.from_user.id, MyStates.main_menu, message.chat.id)
            bot.send_message(message.from_user.id, MAIN_MENU, reply_markup=menu)
        elif user.user_state == 3:
            bot.set_state(message.from_user.id, MyStates.recipes_menu, message.chat.id)
            bot.send_message(message.from_user.id, CHOOSE_RECIPE, reply_markup=recipes_markup())
    else:
        bot.set_state(message.from_user.id, MyStates.reg, message.chat.id)
        bot.send_message(message.from_user.id, "Hello! " + NAME_QUESTION)


@bot.message_handler(state=MyStates.reg)
def get_name(message):
    if message.text.isalpha():
        bot.send_message(message.from_user.id, GENDER_QUESTION, reply_markup=gender_markup)
        with bot.retrieve_data(message.chat.id) as data:
            data['name'] = message.text
            data['current_user'] = message.from_user
    else:
        bot.send_message(message.from_user.id, INVALID_NAME)
        start_again(message)


def start_again(message):
    bot.send_message(message.from_user.id, ENTER_VALID_NAME)
    bot.set_state(message.from_user.id, MyStates.reg, message.chat.id)


@bot.callback_query_handler(state=MyStates.reg, func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'Man' or call.data == 'Woman':
                gender = call.data
                gender_id = 1 if gender == 'Man' else 2
                with bot.retrieve_data(call.message.chat.id) as data:
                    data['gender'] = gender
                    data['gender_id'] = gender_id
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=THANKS,
                                      reply_markup=None)
                with bot.retrieve_data(call.message.chat.id) as data:
                    user, created = User.objects.update_or_create(user_id=data['current_user'].id,
                                                                  username=data['current_user'].username,
                                                                  first_name=data['current_user'].first_name,
                                                                  last_name=data['current_user'].last_name,
                                                                  defaults=dict(name_from_form=data['name'],
                                                                                user_gender=data['gender_id'],
                                                                                user_state=2))
                if created:
                    bot.send_message(data['current_user'].id,
                                     USER_CREATED,
                                     reply_markup=menu)
                else:
                    bot.send_message(data['current_user'].id,
                                     USER_UPDATED,
                                     reply_markup=menu)
                bot.set_state(data['current_user'].id, MyStates.main_menu, call.message.chat.id)
    except Exception as e:
        bot.send_message(call.message.chat.id, CALL_ERROR,
                         reply_markup=start)
        print('Error:\n', traceback.format_exc())


@bot.message_handler(state=MyStates.main_menu)
def handled_text(message):
    if message.text == ABOUT:
        user = User.objects.filter(user_id=message.chat.id).last()
        gender = 'Man' if user.user_gender == 1 else 'Woman'
        bot.send_message(message.from_user.id,
                         f"Your name is {user.name_from_form} and you are a {gender} :)")
    elif message.text == RECIPES:
        user = User.objects.filter(user_id=message.chat.id)
        bot.set_state(message.from_user.id, MyStates.recipes_menu, message.chat.id)
        bot.send_message(message.from_user.id, CHOOSE_RECIPE, reply_markup=recipes_markup())
        user.update(user_state=3)
    elif message.text == RE_ENTER:
        user = User.objects.filter(user_id=message.chat.id)
        bot.set_state(message.from_user.id, MyStates.reg, message.chat.id)
        bot.send_message(message.from_user.id, NAME_QUESTION)
        user.update(user_state=1)


@bot.message_handler(state=MyStates.recipes_menu)
def recipe_view(message):
    if message.text == BACK:
        bot.set_state(message.from_user.id, MyStates.main_menu, message.chat.id)
        bot.send_message(message.from_user.id, MAIN_MENU, reply_markup=menu)
        User.objects.filter(user_id=message.chat.id).update(user_state=2)
    else:
        try:
            recipe = Recipe.objects.filter(name=message.text).last()
            bot.send_chat_action(message.from_user.id, 'upload_photo')
            if recipe.photo:
                bot.send_photo(message.from_user.id, recipe.photo)
                bot.send_message(message.from_user.id, recipe.description)
            else:
                bot.send_message(message.from_user.id, recipe.description)
            recipes_markup()
        except Exception as e:
            bot.send_message(message.from_user.id, INVALID_RECIPE)
            bot.set_state(message.from_user.id, MyStates.recipes_menu, message.chat.id)


# Restart notification
@bot.message_handler(state=None)
def notification(message):
    bot.send_message(message.chat.id, RESTART_NOTIFICATION)


# Restart notification when genderform is not finished
@bot.callback_query_handler(state=None, func=lambda call: True)
def notification_genderform(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=RESTART_NOTIFICATION,
                          reply_markup=None)


if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    logger.setLevel(logging.INFO)

    server = Flask(__name__)

    @server.route('/' + settings.TOKEN, methods=['POST'])
    def get_message():
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://recipes--book.herokuapp.com/' + settings.TOKEN)
        return "?", 200

    if __name__ == "__main__":
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

else:
    bot.remove_webhook()
    bot.polling(none_stop=True)
