from telebot import AdvancedCustomFilter
from telebot.handler_backends import State

from telebot import types

from custom_admin.models import User


class StateFilter(AdvancedCustomFilter):
    """
    Filter to check state.
    .. code-block:: python3
        :caption: Example on using this filter:

        @bot_package.message_handler(state=1)
        # your function
    """

    def __init__(self, bot):
        self.bot = bot

    key = 'state'

    def check(self, message, text):
        """
        :meta private:
        """
        if text == '*': return True

        # needs to work with callbackquery
        if isinstance(message, types.Message):
            chat_id = message.chat.id
            user_id = message.from_user.id

        if isinstance(message, types.CallbackQuery):
            chat_id = message.message.chat.id
            user_id = message.from_user.id
            message = message.message

        if isinstance(text, list):
            new_text = []
            for i in text:
                if isinstance(i, State): i = i.name
                new_text.append(i)
            text = new_text
        elif isinstance(text, State):
            text = text.name

        if message.chat.type in ['group', 'supergroup']:
            group_state = self.bot.current_states.get_state(chat_id, user_id)
            if group_state == text:
                return True
            elif type(text) is list and group_state in text:
                return True

        else:
            user = User.objects.filter(user_id=user_id).last()
            user_state = user.user_state
            if user_state == text:
                return True
            elif type(text) is list and user_state in text:
                return True
