import os

from django.http import HttpResponse
import telebot
from datetime import datetime, timedelta
import re
import ExchangeRate.graphs
from ExchangeRate.messages import Currency


def TeleBotPage(request):
    TeleBotTest(request)
    return HttpResponse('<h>BOTAPP</h>')


def TeleBotTest(request):
    bot = telebot.TeleBot('5275070623:AAFx6eA6usYCq2DBCifGWtEru2DuYCUAwQI', parse_mode=None)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, 'Hello, i am a new telegram bot.\n'
                                          'Print /rate in the chat to see current exchange rate.\n'
                                          'If you want to receive messages about changes in exchange rate print /send\n'
                                          'If you dont want to receive messages about changes in exchange rate print /forget\n'
                                          'You can select currency that will be tracked for you (default: dollars).'
                                          'Print /add_+(currency that you want to check) or /del_+'
                                          '(currency that you dont want to check). Available options: '
                                          'dollar, euro, yen, yuan')
        from TeleBot.models import TelebotUsers
        new_user = message.chat.id
        user_db = TelebotUsers()
        check_number = 0
        for i in range(len(list(TelebotUsers.objects.values('username')))):
            if str(new_user) != list(TelebotUsers.objects.values('username'))[i]['username']:
                pass
            else:
                check_number += 1
        if check_number == 0:
            user_db.username = new_user
            user_db.join_date = datetime.now().replace(second=0, microsecond=0)
            user_db.sending_status = False
            user_db.save()
        else:
            pass

    @bot.message_handler(commands=['rate', 'Rate'])
    def current_exchange(message):
        bot.send_message(message.chat.id, f'Current Dollar Exchange Rate is: {Currency().get_currency_price()[0]},\n'
                                          f'Current Euro Exchange Rate is: {Currency().get_currency_price()[1]}')

    @bot.message_handler(commands=['send', 'Send'])
    def change_sending_status(message):
        from TeleBot.models import TelebotUsers
        TelebotUsers.objects.filter(username=message.chat.id).update(sending_status=True)
        bot.send_message(message.chat.id, 'Now you will receive messages about changes in exchange rate')

    @bot.message_handler(commands=['forget', 'Forget'])
    def change_sending_status(message):
        from TeleBot.models import TelebotUsers
        TelebotUsers.objects.filter(username=message.chat.id).update(sending_status=False)
        bot.send_message(message.chat.id, 'Now you wont receive messages about changes in exchange rate')

    @bot.message_handler(content_types=['text'])
    def send_graph(message):
        if message.text[0:6] == '/plot_':
            cur_check = re.findall(r'/plot_(\w+)_', message.text)
            try:
                time_check = re.findall(f'/plot_{cur_check[0]}_(\w+)', message.text)
                try:
                    year = re.search(r'([0-9]+)y', time_check[0]).group(0).replace('y', '')
                except:
                    year = datetime.now().year
                try:
                    month = re.search(r'([0-9]+)m', time_check[0]).group(0).replace('m', '')
                except:
                    month = datetime.now().month
                try:
                    day = re.search(r'([0-9]+)d', time_check[0]).group(0).replace('d', '')
                except:
                    day = datetime.now().day
                try:
                    hour = re.search(r'([0-9]+)h', time_check[0]).group(0).replace('h', '')
                except:
                    hour = datetime.now().hour
                try:
                    minute = re.search(r'([0-9]+)min', time_check[0]).group(0).replace('min', '')
                except:
                    minute = datetime.now().minute
                start_date = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute))
                try:
                    print('заглушка')
                except:
                    bot.send_message(message.chat.id, 'You typed something wrong, please check if currency that '
                                                      'you want is available')
            except:
                bot.send_message(message.chat.id, 'You typed something wrong, please check if date format is correct')
            cur_sql = cur_check[0] + '_rate'
            plt = ExchangeRate.graphs.create_plot(cur_sql, start_date)
            plt.savefig(os.curdir + f"{message.chat.id}{cur_check}{time_check}.png")
            img = open(os.curdir + f"{message.chat.id}{cur_check}{time_check}.png", 'rb')
            bot.send_photo(message.chat.id, img, caption=f'{cur_check}_{time_check}')
            img.close()
            os.remove(os.curdir + f"{message.chat.id}{cur_check}{time_check}.png")
        else:
            bot.send_message(message.chat.id, 'I dont understand what you are saying:( ')

    @bot.message_handler(
        commands=['add_dollar', 'add_dollars', 'add_euro', 'add_euros', 'add_yen', 'add_yens', 'add_yuan', 'add_yuans'])
    def add_currency_to_db(message):
        from TeleBot.models import TelebotUsers
        before = str(list(TelebotUsers.objects.filter(username=message.chat.id).values('user_currency'))[0]['user_currency'])
        message_text = re.findall(r'/add_(\w+)', message.text)[0]
        if message_text[-1] == 's':
            correct_currency = message_text.rstrip(message_text[-1]) + '_rate'
            correct_currency = correct_currency.replace(' ', '')
        else:
            correct_currency = message_text + '_rate'
            correct_currency = correct_currency.replace(' ', '')
        try:
            test = re.search(correct_currency, before)[0]
            bot.send_message(message.chat.id, f'You are already tracking {correct_currency.replace("_", " ")}')
        except:
            TelebotUsers.objects.filter(username=message.chat.id).update(user_currency=before + ',' + correct_currency)
            bot.send_message(message.chat.id, f'Now you will receive messages about changes in {correct_currency.replace("_", " ")}')

    @bot.message_handler(
        commands=['del_dollar', 'del_dollars', 'del_euro', 'del_euros', 'del_yen', 'del_yens', 'del_yuan', 'del_yuans'])
    def del_currency_from_db(message):
        from TeleBot.models import TelebotUsers
        before = str(
            list(TelebotUsers.objects.filter(username=message.chat.id).values('user_currency'))[0]['user_currency'])
        message_text = re.findall(r'/del_(\w+)', message.text)[0]
        if message_text[-1] == 's':
            correct_currency = message_text.rstrip(message_text[-1]) + '_rate'
            correct_currency = correct_currency.replace(' ', '')
        else:
            correct_currency = message_text + '_rate'
            correct_currency = correct_currency.replace(' ', '')
        try:
            test = re.search(correct_currency, before)[0]
            new_currency = before.replace(f',{correct_currency}', '')
            TelebotUsers.objects.filter(username=message.chat.id).update(user_currency=new_currency)
            bot.send_message(message.chat.id, f'You wont track {correct_currency.replace("_", " ")} anymore.')
        except:
            bot.send_message(message.chat.id, f'You havent tracked {correct_currency.replace("_", " ")} anyway.')

    bot.polling(none_stop=True, interval=0)
    return HttpResponse('<h>BOT CLOSED</h>')
