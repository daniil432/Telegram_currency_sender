import telebot
from TelegramApp.celery import app
from datetime import datetime
from ExchangeRate import messages


@app.task
def create_record(dollar_rate, euro_rate, yen_rate, yuan_rate):
    # Периодическая задача.
    # Создаём записи в базе данных о текущем курсе валют, а также о времени создания этих записей.
    from TeleBot.models import ExchangeData
    data = ExchangeData()
    data.dollar_rate = dollar_rate
    data.euro_rate = euro_rate
    data.yen_rate = yen_rate
    data.yuan_rate = yuan_rate
    data.time_rate = datetime.now().replace(second=0, microsecond=0)
    # Сохраняем запись.
    data.save()


@app.task
def check_rate(dollar_rate, euro_rate, yen_rate, yuan_rate):
    # Периодическая задача.
    # Сравниваем текущий курс валют с предыдущими, формируем сообщение для пользователя если необходимые
    # условия выполнены.
    from TeleBot.models import TelebotUsers
    bot = telebot.TeleBot('5275070623:AAFx6eA6usYCq2DBCifGWtEru2DuYCUAwQI', parse_mode=None)
    # Достаём данные о пользователе из БД.
    user_data = list(TelebotUsers.objects.values('id', 'username', 'sending_status', 'percent_user', 'user_currency'))
    # Словарь с текущими курсами валют.
    current_dict = {"dollar_rate": dollar_rate, "euro_rate": euro_rate, "yen_rate": yen_rate, "yuan_rate": yuan_rate}

    # Проверяем статус пользователей, если они согласны получать авто сообщения, то вызываем сборщика сообщений и даем
    # ему данные пользователей.
    for ind in range(len(user_data)):
        if user_data[ind]['sending_status'] is True:
            # Список отслеживаемых пользователем валют
            user_currency = user_data[ind]['user_currency'].split(",")
            # Процент, выбранный пользователем. При росте или падении рубля больше чем на заданный процент
            # присылается сообщение.
            percent = user_data[ind]["percent_user"]
            # Собранное сообщение об изменениях курса валют. Если изменений значительных не было, то оно будет пустое и
            # не будет присылаться.
            final_message = messages.CreateMessage(user_data[ind]['id'], current_dict, user_currency, percent).message_assembler()
            if final_message == '':
                pass
            else:
                bot.send_message(user_data[ind]['username'], final_message)
