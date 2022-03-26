from django.http import HttpResponse
import telebot
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


def TeleBotPage(request):
    TeleBotTest(request)
    return HttpResponse('<h>BOTAPP</h>')


def TeleBotTest(request):
    bot = telebot.TeleBot('5275070623:AAFx6eA6usYCq2DBCifGWtEru2DuYCUAwQI', parse_mode=None)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, 'Hello, i am a new telegram bot.\n'
                                          'Print /A in the chat to see current exchange rate.\n'
                                          'If you want to receive messages about changes in exchange rate print /B\n'
                                          'If you dont want to receive messages about changes in exchange rate print /C\n'
                                          'You can select currency that will be tracked for you (default: dollars).'
                                          'Print /add_ + (currency that you want to check) or /del_ + '
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

    @bot.message_handler(commands=['A'])
    def current_exchange(message):
        bot.send_message(message.chat.id, f'Current Dollar Exchange Rate is: {Currency().get_currency_price()[0]},\n'
                                          f'Current Euro Exchange Rate is: {Currency().get_currency_price()[1]}')

    @bot.message_handler(commands=['B'])
    def change_sending_status(message):
        from TeleBot.models import TelebotUsers
        TelebotUsers.objects.filter(username=message.chat.id).update(sending_status=True)
        bot.send_message(message.chat.id, 'Now you will receive messages about changes in exchange rate')

    @bot.message_handler(commands=['C'])
    def change_sending_status(message):
        from TeleBot.models import TelebotUsers
        TelebotUsers.objects.filter(username=message.chat.id).update(sending_status=False)
        bot.send_message(message.chat.id, 'Now you wont receive messages about changes in exchange rate')

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
            bot.send_message(message.chat.id, f'You are already tracking {correct_currency}')
        except:
            TelebotUsers.objects.filter(username=message.chat.id).update(user_currency=before + ',' + correct_currency)
            bot.send_message(message.chat.id, f'Now you will receive messages about changes in {correct_currency}')

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
            bot.send_message(message.chat.id, f'You wont track {correct_currency} anymore.')
        except:
            bot.send_message(message.chat.id, f'You havent tracked {correct_currency} anyway.')

    bot.polling(none_stop=True, interval=0)
    return request


class Currency(object):
    DOLLAR_RUB = 'https://www.google.com/search?sxsrf=ALeKk01NWm6viYijAo3HXYOEQUyDEDtFEw%3A1584716087546&source=hp&ei=N9l0XtDXHs716QTcuaXoAg&q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+&gs_l=psy-ab.3.0.35i39i70i258j0i131l4j0j0i131l4.3044.4178..5294...1.0..0.83.544.7......0....1..gws-wiz.......35i39.5QL6Ev1Kfk4'
    EURO_RUB = 'https://www.google.com/search?q=tdhj+к+рублю&ei=q0M2YuPCMK6qrgSN2YzwBQ&ved=0ahUKEwijxNCQiNP2AhUulYsKHY0sA14Q4dUDCA0&uact=5&oq=tdhj+к+рублю&gs_lcp=Cgdnd3Mtd2l6EAMyCggAELEDEIMBEEMyBAgAEAoyBAgAEAoyBAgAEAoyCggAELEDEIMBEAoyBAgAEAoyBAgAEAoyBAgAEAoyBAgAEAoyBAgAEAo6BggAEAcQHjoICAAQBxAKEB46CggAEAcQChAeECo6BAgAEA1KBAhBGABKBAhGGABQAFiDBGC9BmgAcAF4AIABPYgB6gGSAQE0mAEAoAEBwAEB&sclient=gws-wiz'
    "Заголовки для передачи вместе с URL"
    YEN_RUB = 'https://www.google.com/search?client=opera&q=qtys+d+he%2Ckb&sourceid=opera&ie=UTF-8&oe=UTF-8'
    YUAN_RUB ='https://www.google.com/search?q=.fym+в+рубли&client=opera&hs=Lcq&ei=mOw9YvLPGoWyrgTvmrKoBw&ved=0ahUKEwjy-6Ob1uH2AhUFmYsKHW-NDHUQ4dUDCA0&uact=5&oq=.fym+в+рубли&gs_lcp=Cgdnd3Mtd2l6EAMyDAgAELEDEIMBEAoQKjIECAAQCjIECAAQCjoGCAAQBxAeOggIABAHEAoQHjoKCAAQBxAFEAoQHjoICAAQChABECpKBAhBGABKBAhGGABQAFjZB2DqCWgAcAF4AIABYYgB_wKSAQE0mAEAoAEBwAEB&sclient=gws-wiz'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    current_converted_price_dollar = 0
    current_converted_price_euro = 0
    difference = 5

    def __init__(self):
        self.current_converted_price_dollar = float(self.get_currency_price()[0].replace(",", "."))
        self.current_converted_price_euro = float(self.get_currency_price()[1].replace(",", "."))

    def get_currency_price(self):
        "Парсим всю страницу"
        full_page_dollar = requests.get(self.DOLLAR_RUB, headers=self.headers)
        full_page_euro = requests.get(self.EURO_RUB, headers=self.headers)
        "Разбираем через BeautifulSoup"
        soup_dollar = BeautifulSoup(full_page_dollar.content, 'html.parser')
        soup_euro = BeautifulSoup(full_page_euro.content, 'html.parser')
        "Получаем нужное для нас значение и возвращаем его"
        convert_dollar = soup_dollar.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        convert_euro = soup_euro.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        return convert_dollar[0].text, convert_euro[0].text


    "Проверка изменения валюты"
    def check_currency(self):
        currency_dollar = float(self.get_currency_price()[0].replace(",", "."))
        if currency_dollar >= self.current_converted_price_dollar + self.difference:
            print("Курс сильно вырос, может пора что-то делать?")
        elif currency_dollar <= self.current_converted_price_dollar - self.difference:
            print("Курс сильно упал, может пора что-то делать?")
        print("Сейчас курс: 1 доллар = " + str(currency_dollar))
        return str(currency_dollar)



