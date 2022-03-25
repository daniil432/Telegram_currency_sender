import datetime
import telebot
from django.db.models import Max

from TelegramApp.celery import app
from datetime import timedelta, datetime


@app.task
def create_record(currency_dollar, currency_euro):
    # Создаем записи в базу данных о текущем курсе доллара и евро, а также времени создания записи
    from TeleBot.models import ExchangeData
    data = ExchangeData()
    data.dollar_rate = currency_dollar
    data.euro_rate = currency_euro
    data.time_rate = datetime.now().replace(second=0, microsecond=0)
    print('Success')
    # Сохраняем запись
    data.save()


@app.task
def check_rate(currency_dollar, currency_euro):
    from TeleBot.models import ExchangeData, TelebotUsers
    # Обращаемся к боту для передачиему дальшейших инструкций
    bot = telebot.TeleBot('5275070623:AAFx6eA6usYCq2DBCifGWtEru2DuYCUAwQI', parse_mode=None)
    # Создаём временной диапазон, в котором будет происходить периодическая проверка курса
    data_delta = datetime.now() - datetime(year=2022, month=3, day=22, hour=9, minute=4, second=0)
    check_status = list(TelebotUsers.objects.values('username', 'sending_status', 'percent_user'))
    # Сортируем в порядке убывания и достаём первый элемент


    max_value = list(ExchangeData.objects.filter(time_rate__range=(
        f'{datetime.now().replace(second=0, microsecond=0) - data_delta}',
        f'{datetime.now().replace(second=0, microsecond=0)}')).order_by('-dollar_rate').values('id', 'dollar_rate',
                                                                                               'euro_rate',
                                                                                               'time_rate'))[0]
    min_value = list(ExchangeData.objects.filter(time_rate__range=(
        f'{datetime.now().replace(second=0, microsecond=0) - data_delta}',
        f'{datetime.now().replace(second=0, microsecond=0)}')).order_by('dollar_rate').values('id', 'dollar_rate',
                                                                                              'euro_rate',
                                                                                              'time_rate'))[0]
    print(max_value, min_value)

    for user_true in range(len(check_status)):
        if check_status[user_true]['sending_status'] is True:
            if ((currency_dollar / max_value['dollar_rate']) * 100 - 100 <= -check_status[user_true][
                "percent_user"]) and (
                    (currency_dollar / min_value['dollar_rate']) * 100 - 100 >= check_status[user_true]["percent_user"]):
                if max_value['id'] <= min_value['id']:
                    bot.send_message(TelebotUsers.objects.get(username=check_status[user_true]['username']),
                                     f'Курс рубля к доллару вырос больше чем на {int(check_status[user_true]["percent_user"])}% '
                                     f'по сравнению с курсом на {max_value["time_rate"].replace(tzinfo=None)},'
                                     f' рубль вырос на '
                                     f'{round(((currency_dollar / max_value["dollar_rate"]) * 100 - 100), 3)}%, '
                                     f'значение курса изменилось с {max_value["dollar_rate"]} до {currency_dollar}')
                elif max_value['id'] >= min_value['id']:
                    bot.send_message(TelebotUsers.objects.get(username=check_status[user_true]['username']),
                                     f'Курс рубля к доллару упал больше чем на {int(check_status[user_true]["percent_user"])}% '
                                     f'по сравнению с курсом на {min_value["time_rate"].replace(tzinfo=None)},'
                                     f' рубль упал на '
                                     f'{round(((currency_dollar / min_value["dollar_rate"]) * 100 - 100), 3)}%, '
                                     f'значение курса изменилось с {min_value["dollar_rate"]} до {currency_dollar}')
            elif ((currency_dollar / max_value['dollar_rate']) * 100 - 100 <= -check_status[user_true]["percent_user"]) \
                    and ((currency_dollar / min_value['dollar_rate']) * 100 - 100 < check_status[user_true]["percent_user"]):
                bot.send_message(TelebotUsers.objects.get(username=check_status[user_true]['username']),
                                 f'Курс рубля к доллару вырос больше чем на {int(check_status[user_true]["percent_user"])}% '
                                 f'по сравнению с курсом на {max_value["time_rate"].replace(tzinfo=None)}, '
                                 f'рубль вырос на {round(((currency_dollar / max_value["dollar_rate"]) * 100 - 100), 3)}%, '
                                 f'значение курса изменилось с {max_value["dollar_rate"]} до {currency_dollar}')
            elif ((currency_dollar / max_value['dollar_rate']) * 100 - 100 > -check_status[user_true][
                "percent_user"]) and (
                    (currency_dollar / min_value['dollar_rate']) * 100 - 100 >= check_status[user_true][
                "percent_user"]):
                bot.send_message(TelebotUsers.objects.get(username=check_status[user_true]['username']),
                                 f'Курс рубля к доллару упал больше чем на {int(check_status[user_true]["percent_user"])}% '
                                 f'по сравнению с курсом на {min_value["time_rate"].replace(tzinfo=None)}, '
                                 f'рубль упал на {round(((currency_dollar / min_value["dollar_rate"]) * 100 - 100), 3)}%, '
                                 f'значение курса изменилось с {min_value["dollar_rate"]} до {currency_dollar}')
            else:
                pass
