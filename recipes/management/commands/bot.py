import traceback
from unittest.mock import call
from telebot.asyncio_handler_backends import CancelUpdate, BaseMiddleware
import telebot
from django.conf import settings
from telebot import types
from recipes.models import Recipe
from bot_users.models import User
from django.core.management.base import BaseCommand

bot = telebot.TeleBot(settings.TOKEN, parse_mode=None, use_class_middlewares=True, num_threads=5)


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
    global name
    global gender_id
    global gender

    user_state = 1
    try:
        user = User.objects.filter(user_id=message.from_user.id).last()
        name = user.name_from_form
        gender = 'Man' if user.user_gender == 1 else 'Woman'
        gender_id = user.user_gender
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
    except User.DoesNotExist:
        bot.send_message(message.from_user.id, "Hello! What is your name? ;)")
        bot.register_next_step_handler(message, get_name)


def start_again(message):
    bot.send_message(message.from_user.id, "Please, enter a valid name... ;)")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    if message.text.isalpha():
        global msg
        msg = message
        name = message.text
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
    from_user = message.from_user
    if User.objects.filter(user_id=from_user.id).last():
        user = User.objects.filter(user_id=from_user.id)
        user.update(user_id=from_user.id,
                    username=from_user.username,
                    first_name=from_user.first_name,
                    last_name=from_user.last_name,
                    name_from_form=name,
                    user_gender=gender_id,
                    user_state=user_state)
        bot.send_message(from_user.id,
                         'You were already registered, but we have updated your data :)',
                         reply_markup=menu)
    else:
        User.objects.create(user_id=from_user.id,
                            username=from_user.username,
                            first_name=from_user.first_name,
                            last_name=from_user.last_name,
                            name_from_form=name,
                            user_gender=gender_id,
                            user_state=user_state)
        bot.send_message(from_user.id,
                         'Registration completed successfully! :)',
                         reply_markup=menu)
    user = User.objects.filter(user_id=message.from_user.id).update(user_state=2)
    bot.register_next_step_handler(message, handled_text)


@bot.message_handler(content_types=['text'])
def handled_text(message):
    if message.text == 'About me':
        bot.send_message(message.from_user.id, f'Your name is {name} and you are a {gender} :)')
        bot.register_next_step_handler(message, handled_text)
    elif message.text == 'Recipes':
        user = User.objects.filter(user_id=message.from_user.id).update(user_state=3)
        recipes_markup(message)
    elif message.text == '/start':
        user = User.objects.filter(user_id=message.from_user.id).update(user_state=1)
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

bot.polling(none_stop=True)
