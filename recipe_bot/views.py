import telebot
from django.http import JsonResponse, HttpResponse
from django.views import View
from .bot_package.bot_handlers import bot


class TelegramWebhookHandlerView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Bot is successfully started :)")

    def post(self, request, *args, **kwargs):
        print(request)
        if request.headers.get("content-type") == "application/json":
            json_string = request.body.decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return JsonResponse(status=200, data={"status": "true"})
        return JsonResponse(status=403, data={"status": "false"})
