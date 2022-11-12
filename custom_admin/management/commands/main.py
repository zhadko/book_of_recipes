import telebot
from telebot import custom_filters
from telebot.handler_backends import CancelUpdate, BaseMiddleware, State, StatesGroup

# States storage
from telebot.storage import StateMemoryStorage

from django.conf import settings

# Main Variables
state_storage = StateMemoryStorage()

bot = telebot.TeleBot(settings.TOKEN,
                      parse_mode=None,
                      use_class_middlewares=True,
                      num_threads=5,
                      state_storage=state_storage)
print(bot.get_me())


# Classes
# State class
class MyStates(StatesGroup):
    reg = State()
    main_menu = State()
    recipes_menu = State()


bot.add_custom_filter(custom_filters.StateFilter(bot))


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
