from django.apps import AppConfig
import TeleBot.telebot_commands


class TelebotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TeleBot'

    def ready(self):
        # Запуск бота. Пока бот работает, Django сервер до конца не поднимется. Но, тем не менее, все необходимые для
        # бота модули уже загрузились. Если когда-нибудь будут возникать ошибки, найду другое решение.
        TeleBot.telebot_commands.TeleBot()
