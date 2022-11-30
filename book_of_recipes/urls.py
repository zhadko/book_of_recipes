from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from book_of_recipes.views import home
from django.views.decorators.csrf import csrf_exempt
from recipe_bot.views import TelegramWebhookHandlerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('custom_admin/', include(('custom_admin.urls', 'custom_admin'))),
    path('', home, name='home'),
    path('accounts/', include(('accounts.urls', 'accounts'))),
    path("webhook/", csrf_exempt(TelegramWebhookHandlerView.as_view()), name='bot_webhook'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
