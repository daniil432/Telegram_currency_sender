import os
import telebot
from datetime import datetime, timedelta
import re
import ExchangeRate.graphs
from ExchangeRate.messages import Currency


def TeleBot():
    # Запускаем бота. Благодаря bot.polling() не выключается и пользователь может общаться сколько угодно с ним.
    bot = telebot.TeleBot('5275070623:AAFx6eA6usYCq2DBCifGWtEru2DuYCUAwQI', parse_mode=None)
    print("Bot started to do it's bot things")

    # Обрабатываем различные запросы пользователя.
    @bot.message_handler(commands=['start', 'help'])
    def start_message(message):
        # Основная информация о боте и о том, как отправлять запросы.
        bot.send_message(message.chat.id, 'Hello, i am a new telegram bot.\n'
                                          'Print /rate in the chat to see current exchange rate.\n'
                                          'If you want to receive messages about changes in exchange rate print /send\n'
                                          'If you dont want to receive messages about changes in exchange rate print /forget\n'
                                          'You can select currency that will be tracked for you (default: dollars).'
                                          'Print /add_(currency that you want to check) or /del_'
                                          '(currency that you dont want to check). Available options: '
                                          'dollar, euro, yen, yuan. Example: /add_yen, /del_dollar.'
                                          'You can choose what size of changes in the exchange rate should be tracked '
                                          '(default: 5% against the current exchange rate). Print /percent_(your value) '
                                          'to change it. After that you will receive messages when the rate changes by '
                                          'that percentage from the rate that was recorded when previous message about '
                                          'changes was sent.\n\n'
                                          'If you want to receive graph with exchange rate during some time diapason'
                                          'print /graph_(currency you want to check)_(time range that you want '
                                          'to check. You can choose default options such as 1, 2, 3, 5, 7, 14, 30 '
                                          'to see exchange rate for this amount of days. Also you can select your own'
                                          'time range, for this purpose print time as 2020y7m24d17h30min.'
                                          'You can remove some part of your date and print it as 2020y17h for example. '
                                          'In this case month, day and min will automatically be set to the same as today.\n'
                                          'Examples: /graph_dollar_14, /graph_euro_2021y12m15d14h30m, /graph_yuan_4m1d,'
                                          '/graph_yen_2021y\n\n'
                                          'If you have any suggestions or comments, you can send your feedback by '
                                          'writing /feedback_(message text)')
        from TeleBot.models import TelebotUsers
        new_user = message.chat.id
        user_db = TelebotUsers()
        check_number = 0
        # Извлекаем из БД имя всех пользователей и проверяем, если ли написавший сообщение пользователь среди них.
        # Если нет, заносим его в БД и задаем стандартные значения в поля.
        for i in range(len(list(TelebotUsers.objects.values('username')))):
            if str(new_user) != list(TelebotUsers.objects.values('username'))[i]['username']:
                pass
            else:
                check_number += 1
        if check_number == 0:
            user_db.username = new_user
            user_db.join_date = datetime.now().replace(second=0, microsecond=0)
            user_db.sending_status = False
            user_db.percent_user = 5
            user_db.user_currency = 'dollar_rate'
            user_db.save()
        else:
            pass

    @bot.message_handler(commands=['rate', 'Rate'])
    def current_exchange(message):
        # Присылаем значения текущего курса всех доступных валют.
        bot.send_message(message.chat.id, f'Current Dollar Exchange Rate is: {Currency().get_currency_price()[0]},\n'
                                          f'Current Euro Exchange Rate is: {Currency().get_currency_price()[1]},\n'
                                          f'Current Yen Exchange Rate is: {Currency().get_currency_price()[2]},\n'
                                          f'Current Yuan Exchange Rate is: {Currency().get_currency_price()[3]},\n')

    @bot.message_handler(commands=['send', 'Send'])
    def change_sending_status(message):
        # Меняем статус пользователя - он хочет получать авто сообщения.
        from TeleBot.models import TelebotUsers
        if list(TelebotUsers.objects.filter(username=message.chat.id).values('sending_status'))[0]['sending_status'] is False:
            TelebotUsers.objects.filter(username=message.chat.id).update(sending_status=True)
            bot.send_message(message.chat.id, 'Now you will receive messages about changes in exchange rate')
        else:
            # Сообщение о том, что он уже получает сообщения когда условия отправки выполняются.
            bot.send_message(message.chat.id, 'You are already receiving messages about changes in course')

    @bot.message_handler(commands=['forget', 'Forget'])
    def change_sending_status(message):
        # Меняем статус пользователя - он не хочет получать авто сообщения.
        from TeleBot.models import TelebotUsers
        if list(TelebotUsers.objects.filter(username=message.chat.id).values('sending_status'))[0]['sending_status'] is True:
            TelebotUsers.objects.filter(username=message.chat.id).update(sending_status=False)
            bot.send_message(message.chat.id, 'Now you wont receive messages about changes in exchange rate')
        else:
            # Сообщение о том, что он и так не получает сообщения.
            bot.send_message(message.chat.id, 'You havent tracked any currency anyway')

    @bot.message_handler(
        commands=['add_dollar', 'add_dollars', 'add_euro', 'add_euros', 'add_yen', 'add_yens', 'add_yuan', 'add_yuans'])
    def add_currency_to_db(message):
        # Добавляем пользователю в БД новые валюты, которые он решил отслеживать.
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
            # Если он уже отслеживает данную валюту, пишем ему об этом.
            test = re.search(correct_currency, before)[0]
            bot.send_message(message.chat.id, f'You are already tracking {correct_currency.replace("_", " ")}')
        except:
            TelebotUsers.objects.filter(username=message.chat.id).update(user_currency=before + ',' + correct_currency)
            bot.send_message(message.chat.id, f'Now you will receive messages about changes in {correct_currency.replace("_", " ")}')

    @bot.message_handler(
        commands=['del_dollar', 'del_dollars', 'del_euro', 'del_euros', 'del_yen', 'del_yens', 'del_yuan', 'del_yuans'])
    def del_currency_from_db(message):
        # Удаляем пользователю из БД валюты, которые он решил больше не отслеживать.
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
            # Если он и так не отслеживает данную валюту, пишем ему об этом.
            bot.send_message(message.chat.id, f'You havent tracked {correct_currency.replace("_", " ")} anyway.')

    @bot.message_handler(content_types=['text'])
    def other_commands(message):
        # Обработка всех прочих поступающих команд. Доступна постройка графиков, отправка отзыва или жалобы, изменение
        # процента, который используется при отслеживании скачков в курсе валют.
        # На всё остальное бот отвечает, что не понял пользователя.
        if message.text[0:6] == '/plot_':
            send_graph(message, bot)
        elif message.text[0:10] == '/feedback_':
            feedback(message, bot)
        elif message.text[0:9] == '/percent_':
            percent_change(message, bot)
        else:
            bot.send_message(message.chat.id, 'I dont understand what you are saying:( ')

    bot.polling(none_stop=True, interval=0)


def send_graph(message, bot):
    # Обработчик запроса о постройке графика курса валют за заданный промежуток времени.
    # Извлекаем название валюты после ключевой фразы.
    cur_check = re.findall(r'/plot_(\w+)_', message.text)
    try:
        # Извлекаем текст после ключевой фразы и валюты.
        time_check = re.findall(f'/plot_{cur_check[0]}_(\w+)', message.text)
        default_choose = [1, 2, 3, 5, 7, 14, 30, 60]
        start_date = datetime.now().replace(second=0, microsecond=0)
        # Проверяем не ввёл ли пользователь один из стандартных запросов.
        for num in range(len(default_choose)):
            if time_check == [f'{default_choose[num]}']:
                user_choose = timedelta(days=default_choose[num])
                start_date = start_date - user_choose
            else:
                pass
        # Если введён не стандартный запрос, обрабатываем полученный текст и превращаем его в нужный datetime объект.
        if start_date == datetime.now().replace(second=0, microsecond=0):
            # При отсутствии какого-либо из ключевых символов в запросе отсутствующая информация о желаемом элементе
            # даты заменяется на равную сегодняшней (т.е., например, при отсутствии элемента m месяц в datetime объекте
            # будет выбираться равным текущему месяцу).
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
            # Пробуем сформировать дату из отфильтрованных объектов, а также сформировать запрос к БД с выбранным
            # курсом валют. Если такой валюты нет в БД или не удается сформировать дату, присылается сообщение-ошибка.
            try:
                start_date = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour),
                                      minute=int(minute))
                cur_sql = cur_check[0] + '_rate'
                plt = ExchangeRate.graphs.create_plot(cur_sql, start_date)
            except:
                bot.send_message(message.chat.id,
                                 'You typed something wrong, please check if currency that '
                                 'you want is available or time is typed correctly')
        # Если введён стандартный запрос, то формируется только запрос к БД о курсе валют, затем вызывается
        # строитель графиков.
        else:
            try:
                cur_sql = cur_check[0] + '_rate'
                plt = ExchangeRate.graphs.create_plot(cur_sql, start_date)
            except:
                bot.send_message(message.chat.id,
                                 'You typed something wrong, please check if currency that '
                                 'you want is available')
    except:
        pass

    # Проверяем, не произошло ли ошибки. Если в качестве даты, посылаемой конструктору графиков, выступает текущее
    # время - пользователь ввёл что-то не так. Если из конструктора вернулась строка, значит пользователь решил
    # заглянуть в будущее. Если всё хорошо, присылается график с курсом валют за выбранный промежуток времени.
    if start_date == datetime.now().replace(second=0, microsecond=0):
        bot.send_message(message.chat.id,
                         'You typed something wrong, please check if date format is correct')
    elif type(plt) == str():
        bot.send_message(message.chat.id, plt)
    else:
        plt.savefig(os.curdir + f"{message.chat.id}{cur_check}{time_check}.png")
        img = open(os.curdir + f"{message.chat.id}{cur_check}{time_check}.png", 'rb')
        bot.send_photo(message.chat.id, img, caption=f'{cur_check[0]}_{time_check[0]}')
        img.close()
        os.remove(os.curdir + f"{message.chat.id}{cur_check}{time_check}.png")


def feedback(message, bot):
    # Отзыв или жалоба пользователя. В качестве отзыва выступает всё, что идёт после ключевой фразы /feedback_,
    # Глуповато, но что-то другое придумывать уже не хочется.
    feedback_message = message.text[10:]
    from TeleBot.models import UserFeedback, TelebotUsers

    check_if_exist = list(UserFeedback.objects.filter(
        user_id=list(TelebotUsers.objects.filter(username=message.chat.id).values('id'))[0]['id']).values('feedback'))
    # Проверяем, есть ли уже какие-то отзывы от пользователя. Если есть, прибавляем к старым отзывам новые.
    if check_if_exist == []:
        UserFeedback.objects.create(user_id=list(TelebotUsers.objects.filter(
            username=message.chat.id).values('id'))[0]['id'], feedback=feedback_message,
                                    feedback_send_time=datetime.now().replace(second=0, microsecond=0, tzinfo=None))
        bot.send_message(message.chat.id, f'Feedback successfully was sent')
    else:
        UserFeedback.objects.filter(
            user_id=list(TelebotUsers.objects.filter(username=message.chat.id).values('id'))[0]['id']).update(
            feedback_send_time=datetime.now().replace(second=0, microsecond=0, tzinfo=None),
            feedback=list(UserFeedback.objects.filter(user_id=list(TelebotUsers.objects.filter(
                username=message.chat.id).values('id'))[0]['id']).values('feedback'))[0]['feedback']
                     + " ||| " + feedback_message)
        bot.send_message(message.chat.id, f'Feedback successfully was sent')


def percent_change(message, bot):
    # Пользователь меняет процент, который подставляется в формулу для отслеживания скачков в курсе валют.
    from TeleBot.models import TelebotUsers
    try:
        TelebotUsers.objects.filter(username=message.chat.id).update(percent_user=float(message.text[9:]))
        bot.send_message(message.chat.id, f'You successfully changed percentage that you want to track')
    except:
        bot.send_message(message.chat.id, f'Something is wrong. Check that you wrote numbers, not letters')