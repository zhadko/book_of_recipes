"""
WSGI config for book_of_recipes project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from recipe_bot.bot_package.main import bot
from django.conf import settings

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_of_recipes.settings")

application = get_wsgi_application()

# Setting up Webhook
bot.remove_webhook()
print('\n-----Webhook is setted-----\n')
bot.set_webhook(url=f"{settings.BOT_URL + '/webhook/'}")