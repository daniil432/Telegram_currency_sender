import telebot
from TelegramApp.celery import app
from datetime import datetime
from ExchangeRate import messages


@app.task
def start_bot():
    from TeleBot.telebot_commands import TeleBot
    TeleBot()


@app.task
def create_record(dollar_rate, euro_rate, yen_rate, yuan_rate):
    # Создаем записи в базу данных о текущем курсе доллара и евро, а также времени создания записи
    from TeleBot.models import ExchangeData
    data = ExchangeData()
    data.dollar_rate = dollar_rate
    data.euro_rate = euro_rate
    data.yen_rate = yen_rate
    data.yuan_rate = yuan_rate
    data.time_rate = datetime.now().replace(second=0, microsecond=0)
    # Сохраняем запись
    data.save()


@app.task
def check_rate(dollar_rate, euro_rate, yen_rate, yuan_rate):
    from TeleBot.models import TelebotUsers
    bot = telebot.TeleBot('5275070623:AAFx6eA6usYCq2DBCifGWtEru2DuYCUAwQI', parse_mode=None)
    user_data = list(TelebotUsers.objects.values('id', 'username', 'sending_status', 'percent_user', 'user_currency'))
    current_dict = {"dollar_rate": dollar_rate, "euro_rate": euro_rate, "yen_rate": yen_rate, "yuan_rate": yuan_rate}

    for ind in range(len(user_data)):
        if user_data[ind]['sending_status'] is True:
            user_currency = user_data[ind]['user_currency'].split(",")
            percent = user_data[ind]["percent_user"]
            final_message = messages.CreateMessage(user_data[ind]['id'], current_dict, user_currency, percent).message_assembler()
            if final_message == '':
                pass
            else:
                bot.send_message(user_data[ind]['username'], final_message)
