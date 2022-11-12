import os
import telebot
from flask import Flask, request
import logging
from custom_admin.management.commands.bot_handlers import bot
from django.conf import settings


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Telegram Bot"

    def handle(self, *args, **options):
        pass


# Deploy on heroku
if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

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