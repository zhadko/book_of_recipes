import telebot
from django.http import JsonResponse
from django.views import View
from recipe_bot.main import bot
from recipe_bot.messages import *
from recipe_bot.markups import *
import traceback
from custom_admin.models import Recipe, User


class TelegramWebhookHandlerView(View):
    def post(self, request, *args, **kwargs):
        print(request)
        if request.headers.get("content-type") == "application/json":
            json_string = request.body.decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return JsonResponse(status=200, data={"status": "true"})
        return JsonResponse(status=403, data={"status": "false"})


@bot.message_handler(state='*', commands=['start'])
def start(message):
    if User.objects.filter(user_id=message.from_user.id).exists():
        bot.send_message(message.from_user.id, WELCOME)
        user = User.objects.filter(user_id=message.from_user.id).last()
        User.objects.filter(user_id=message.from_user.id).last()
        if user.user_state == 1:
            bot.send_message(message.from_user.id, NAME_QUESTION)
        elif user.user_state == 2:
            bot.send_message(message.from_user.id, MAIN_MENU, reply_markup=menu)
        elif user.user_state == 3:
            bot.send_message(message.from_user.id, CHOOSE_RECIPE, reply_markup=recipes_markup())
    else:
        User.objects.create(user_id=message.from_user.id,
                            username=message.from_user.username,
                            first_name=message.from_user.first_name,
                            last_name=message.from_user.last_name,
                            user_state=1)
        bot.send_message(message.from_user.id, "Hello! " + NAME_QUESTION)


@bot.message_handler(state=1)
def get_name(message):
    if message.text.isalpha():
        User.objects.filter(user_id=message.from_user.id).update(name_from_form=message.text)
        bot.send_message(message.from_user.id, GENDER_QUESTION, reply_markup=gender_markup)
    else:
        bot.send_message(message.from_user.id, INVALID_NAME)
        bot.send_message(message.from_user.id, ENTER_VALID_NAME)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'Man' or call.data == 'Woman':
                gender = call.data
                gender_id = 1 if gender == 'Man' else 2

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=THANKS,
                                      reply_markup=None)
                User.objects.filter(user_id=call.message.chat.id).update(user_gender=gender_id, user_state=2)

                bot.send_message(call.message.chat.id, USER_CREATED, reply_markup=menu)

                User.objects.filter(user_id=call.message.chat.id).update(user_state=2)
    except Exception as e:
        bot.send_message(call.message.chat.id, CALL_ERROR,
                         reply_markup=start)
        print('Error:\n', traceback.format_exc())


@bot.message_handler(state=2)
def handled_text(message):
    if message.text == ABOUT:
        user = User.objects.filter(user_id=message.chat.id).last()
        gender = 'Man' if user.user_gender == 1 else 'Woman'
        bot.send_message(message.from_user.id,
                         f"Your name is {user.name_from_form} and you are a {gender} :)")
    elif message.text == RECIPES:
        user = User.objects.filter(user_id=message.chat.id)
        bot.send_message(message.from_user.id, CHOOSE_RECIPE, reply_markup=recipes_markup())
        user.update(user_state=3)
    elif message.text == RE_ENTER:
        user = User.objects.filter(user_id=message.chat.id)
        bot.send_message(message.from_user.id, NAME_QUESTION)
        user.update(user_state=1)


@bot.message_handler(state=3)
def recipe_view(message):
    if message.text == BACK:
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
            User.objects.filter(user_id=message.chat.id).update(user_state=3)

# # Restart notification
# @bot.message_handler(state=None)
# def notification(message):
#     bot.send_message(message.chat.id, RESTART_NOTIFICATION)
#
#
# # Restart notification when genderform is not finished
# @bot.callback_query_handler(state=None, func=lambda call: True)
# def notification_genderform(call):
#     bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                           text=RESTART_NOTIFICATION,
#                           reply_markup=None)
