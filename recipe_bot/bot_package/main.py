import telebot
from telebot.handler_backends import CancelUpdate, BaseMiddleware

# States storage
from .StateManager import StateFilter
from django.conf import settings


# Main Variables

bot = telebot.TeleBot(settings.TOKEN,
                      parse_mode=None,
                      use_class_middlewares=True,
                      num_threads=5)
print(bot.get_me(), '\n')

bot.add_custom_filter(StateFilter(bot))


# Antiflood class
class SimpleMiddleware(BaseMiddleware):
    def __init__(self, limit) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message']

    def pre_process(self, message, data):
        if not message.from_user.id in self.last_time:
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            bot.send_message(message.chat.id, 'You are making request too often :|')
            return CancelUpdate()
        self.last_time[message.from_user.id] = message.date

    def post_process(self, message, data, exception):
        pass


bot.setup_middleware(SimpleMiddleware(2))
