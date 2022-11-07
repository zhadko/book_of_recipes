import telebot
from telebot import types
from telebot.asyncio_handler_backends import CancelUpdate, BaseMiddleware

from django.conf import settings
from django.core.management.base import BaseCommand

import traceback

from custom_admin.models import Recipe, User

import os
from flask import Flask, request

bot = telebot.TeleBot(settings.TOKEN, parse_mode=None, use_class_middlewares=True, num_threads=5)
server = Flask(__name__)


class Command(BaseCommand):
    help = "Telegram Bot"

    def handle(self, *args, **options):
        bot.enable_save_next_step_handlers(delay=2)  # Сохранение обработчиков
        bot.load_next_step_handlers()  # Загрузка обработчиков
        bot.infinity_polling()


start = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn1 = types.KeyboardButton('/start')
start.add(btn1)

markup = types.InlineKeyboardMarkup(row_width=1)
btn1 = types.InlineKeyboardButton('Man', callback_data='Man')
btn2 = types.InlineKeyboardButton('Woman', callback_data='Woman')
markup.add(btn1, btn2)

menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn1 = types.KeyboardButton('About me')
btn2 = types.KeyboardButton('Recipes')
btn3 = types.KeyboardButton('/start')
menu.add(btn1, btn2, btn3)


class SimpleMiddleware(BaseMiddleware):
    def __init__(self, limit) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message']
        # Always specify update types, otherwise middlewares won't work

    def pre_process(self, message, data):
        if not message.from_user.id in self.last_time:
            # User is not in a dict, so lets add and cancel this function
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            # User is flooding
            bot.send_message(message.chat.id, 'You are making request too often :|')
            return CancelUpdate()
        self.last_time[message.from_user.id] = message.date

    def post_process(self, message, data, exception):
        pass


@bot.message_handler(commands=['start'])
def start(message):
    global user_state
    user_state = 1
    try:
        user = User.objects.filter(user_id=message.from_user.id).last()
        if user.user_state == 1:
            bot.send_message(message.from_user.id, 'Welcome to RecipesBookBot :)')
            msg = bot.send_message(message.from_user.id, "What is your name? ;)")
            bot.register_next_step_handler(msg, get_name)
        elif user.user_state == 2:
            msg = bot.send_message(message.from_user.id, 'Welcome to RecipesBookBot :)', reply_markup=menu)
            bot.register_next_step_handler(msg, handled_text)
        elif user.user_state == 3:
            recipes = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            for el in list(Recipe.objects.all()):
                recipes.add(types.KeyboardButton(el.name))
            recipes.add(types.KeyboardButton('Back to menu'))
            bot.send_message(message.chat.id, 'Welcome to RecipesBookBot :)')
            bot.send_message(message.from_user.id, 'Choose your recipe:', reply_markup=recipes)
            bot.register_next_step_handler(message, recipe_view)
    except Exception as e:
        bot.send_message(message.from_user.id, "Hello! What is your name? ;)")
        bot.register_next_step_handler(message, get_name)


def start_again(message):
    bot.send_message(message.from_user.id, "Please, enter a valid name... ;)")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    if message.text.isalpha():
        global msg
        msg = message
        global form_name
        form_name = msg.text
        bot.send_message(message.from_user.id, 'What is your gender? ;)', reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "This name is invalid! :(")
        start_again(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'Man' or call.data == 'Woman':
                global gender
                gender = call.data
                global gender_id
                gender_id = 1 if gender == 'Man' else 2
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Thank you ;)',
                                      reply_markup=None)
                reg(msg)
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Oh...Something went wrong. Please, try again later :(',
                         reply_markup=start)
        print('Error:\n', traceback.format_exc())


@bot.message_handler(content_types=['text'])
def reg(message):
    current_user = message.from_user
    if User.objects.filter(user_id=current_user.id).last():
        user = User.objects.filter(user_id=current_user.id)
        user.update(user_id=current_user.id,
                    username=current_user.username,
                    first_name=current_user.first_name,
                    last_name=current_user.last_name,
                    name_from_form=form_name,
                    user_gender=gender_id,
                    user_state=user_state)
        bot.send_message(current_user.id,
                         'You were already registered, but we have updated your data :)',
                         reply_markup=menu)
    else:
        User.objects.create(user_id=current_user.id,
                            username=current_user.username,
                            first_name=current_user.first_name,
                            last_name=current_user.last_name,
                            name_from_form=form_name,
                            user_gender=gender_id,
                            user_state=user_state)
        bot.send_message(current_user.id,
                         'Registration completed successfully! :)',
                         reply_markup=menu)
    User.objects.filter(user_id=message.from_user.id).update(user_state=2)
    bot.register_next_step_handler(message, handled_text)


@bot.message_handler(content_types=['text'])
def handled_text(message):
    user = User.objects.filter(user_id=message.chat.id).last()
    user_gender = 'Man' if user.user_gender == 1 else 'Woman'

    if message.text == 'About me':
        bot.send_message(message.from_user.id, f'Your name is {user.name_from_form} and you are a {user_gender} :)')
        bot.register_next_step_handler(message, handled_text)
    elif message.text == 'Recipes':
        User.objects.filter(user_id=message.from_user.id).update(user_state=3)
        recipes_markup(message)
    elif message.text == '/start':
        User.objects.filter(user_id=message.from_user.id).update(user_state=1)
        start(message)


def recipes_markup(message):
    recipes = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for el in list(Recipe.objects.all()):
        recipes.add(types.KeyboardButton(el.name))
    recipes.add(types.KeyboardButton('Back to menu'))
    bot.send_message(message.from_user.id, 'Choose your recipe:', reply_markup=recipes)
    bot.register_next_step_handler(message, recipe_view)


@bot.message_handler(content_types=['text'])
def recipe_view(message):
    if message.text == 'Back to menu':
        bot.send_message(message.from_user.id, 'Main menu :)', reply_markup=menu)
        bot.register_next_step_handler(message, handled_text)
    elif message.text == '/start':
        recipes_markup(message)
    else:
        try:
            recipe = Recipe.objects.filter(name=message.text).last()
            bot.send_chat_action(message.from_user.id, 'upload_photo')
            if recipe.photo:
                bot.send_photo(message.from_user.id, recipe.photo)
                bot.send_message(message.from_user.id, recipe.description)
                recipes_markup(message)
            else:
                bot.send_message(message.from_user.id, recipe.description)
                recipes_markup(message)
        except Exception as e:
            bot.send_message(message.from_user.id, 'I don`t know this recipe :(')
            bot.register_next_step_handler(message, recipe_view)


bot.setup_middleware(SimpleMiddleware(2))


@server.route('/' + settings.TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://recipes--book.herokuapp.com/' + settings.TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

