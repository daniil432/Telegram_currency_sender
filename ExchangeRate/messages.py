from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re


class Currency(object):
    # Ссылки, с которых берем информацию о текущем курсе валют
    DOLLAR_RUB = 'https://www.google.com/search?sxsrf=ALeKk01NWm6viYijAo3HXYOEQUyDEDtFEw%3A1584716087546&source=hp&ei=N9l0XtDXHs716QTcuaXoAg&q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+&gs_l=psy-ab.3.0.35i39i70i258j0i131l4j0j0i131l4.3044.4178..5294...1.0..0.83.544.7......0....1..gws-wiz.......35i39.5QL6Ev1Kfk4'
    EURO_RUB = 'https://www.google.com/search?q=евро+к+рублю&ei=P4s-YpiCL6GSxc8Pm8CIgAo&ved=0ahUKEwjYnZfC7eL2AhUhSfEDHRsgAqAQ4dUDCA0&uact=5&oq=евро+к+рублю&gs_lcp=Cgdnd3Mtd2l6EAMyDwgAELEDEIMBEEMQRhCCAjIFCAAQgAQyBQgAEIAEMgsIABCABBCxAxCDATIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDoGCAAQBxAeOggIABAHEAoQHjoECAAQDUoECEEYAEoECEYYAFAAWKwOYIQRaABwAXgAgAFoiAGPBJIBAzUuMZgBAKABAcABAQ&sclient=gws-wiz'
    "Заголовки для передачи вместе с URL"
    YEN_RUB = 'https://www.google.com/search?q=йена+к+рублю&ei=RYs-YrSLCN2Oxc8P99G9mAY&ved=0ahUKEwj0wd7E7eL2AhVdR_EDHfdoD2MQ4dUDCA0&uact=5&oq=йена+к+рублю&gs_lcp=Cgdnd3Mtd2l6EAMyEAgAEIAEELEDEIMBEEYQggIyBQgAEIAEMgQIABBDMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgQIABAeOgcIABBHELADOgoIABBHELADEMkDOggIABCSAxCwAzoHCAAQsAMQQzoGCAAQBxAeOgQIABANOgkIABANEEYQggI6BAgAEAo6CwgAEIAEELEDEIMBOg8IABCxAxCDARAKEEYQggI6CAgAEAcQChAeSgQIQRgASgQIRhgAUOAOWNQ3YPg4aAFwAXgAgAHlAYgBvAaSAQU3LjAuMZgBAKABAcgBCsABAQ&sclient=gws-wiz'
    YUAN_RUB ='https://www.google.com/search?q=юань+к+рублю&ei=XYs-YrK8G6uPxc8Pn7CAyAk&ved=0ahUKEwjy3qrQ7eL2AhWrR_EDHR8YAJkQ4dUDCA0&uact=5&oq=юань+к+рублю&gs_lcp=Cgdnd3Mtd2l6EAMyEAgAEIAEELEDEIMBEEYQggIyBQgAEIAEMgQIABBDMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDoGCAAQBxAeSgQIQRgASgQIRhgAUABYugdglAxoAHABeACAAWKIAfECkgEBNJgBAKABAcABAQ&sclient=gws-wiz'
    # Необходимые заголовки для запроса
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

    def get_currency_price(self):
        "Парсим всю страницу"
        full_page_dollar = requests.get(self.DOLLAR_RUB, headers=self.headers)
        full_page_euro = requests.get(self.EURO_RUB, headers=self.headers)
        full_page_yen = requests.get(self.YEN_RUB, headers=self.headers)
        full_page_yuan = requests.get(self.YUAN_RUB, headers=self.headers)
        # Разбираем через BeautifulSoup
        soup_dollar = BeautifulSoup(full_page_dollar.content, 'html.parser')
        soup_euro = BeautifulSoup(full_page_euro.content, 'html.parser')
        soup_yen = BeautifulSoup(full_page_yen.content, 'html.parser')
        soup_yuan = BeautifulSoup(full_page_yuan.content, 'html.parser')
        # Получаем нужное для нас значение курса валют и возвращаем его
        convert_dollar = soup_dollar.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        convert_euro = soup_euro.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        convert_yen = soup_yen.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        convert_yuan = soup_yuan.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        return convert_dollar[0].text, convert_euro[0].text, convert_yen[0].text, convert_yuan[0].text


class CreateMessage(object):
    def __init__(self, user_id, current_dict, user_currency, percent):
        """Сборщик сообщений, формирует периодические сообщения для пользователей, согласившихся их принимать."""
        # ID пользователя.
        self.user_id = user_id
        # Список валют, которые пользователь хочет получать в рассылке.
        self.user_currency = user_currency
        # Словарь со всеми текущими курсами валют.
        self.current_dict = current_dict
        # Процент, который подставляется в формулу для сравнений.
        self.percent = percent

    def message_assembler(self):
        # Метод проверяет, изменился ли курс по отношению к максимальному и минимальному курсу за последние 7 дней для
        # новых пользователей, и если курс упал или вырос на выбранный пользователем процент, то присылается сообщение,
        # а текущий курс, сравнивавшийся с минимальным и максимальным, записывается для данного пользователся. Для уже
        # получавших такое сообщение пользователей текущий курс сравнивается с записанным для него ранее.'
        data_delta = timedelta(days=7)
        # словарь для более удобного создания сообщений.
        text_templates = {"dollar_rate": "доллару", "euro_rate": "евро", "yen_rate": "йене", "yuan_rate": "юаню"}
        final_message = ''
        # Обращаемся к БД, чтобы достать значения курса валют.
        from TeleBot.models import ExchangeData
        from TeleBot.models import UserPreviousMessages
        # Формируем фрагмент сообщения отдельно для каждой валюты из выбранных пользователем.
        for currency in self.user_currency:
            prev_req = re.findall('(\w+)_', currency)[0] + '_prev'
            time_prev = 'time_' + re.findall('(\w+)_', currency)[0]
            # Словарь, который будет использоваться для обновления записей в БД.
            attribute_dict = {prev_req: self.current_dict[currency],
                              time_prev: datetime.now().replace(second=0, microsecond=0)}
            # Обращаемся к БД, чтобы выяснить, хранит ли уже пользователь в ней записи.
            check_if_exist = UserPreviousMessages.objects.filter(user_id=self.user_id).values(prev_req)

            # Если это первое авто сообщение для пользователя, создаём ему запись с нулями вместо курса и текущей датой.
            if list(check_if_exist) == []:
                record = UserPreviousMessages(user_id=self.user_id, dollar_prev=0, euro_prev=0, yen_prev=0, yuan_prev=0,
                                              time_dollar=datetime.now().replace(second=0, microsecond=0, tzinfo=None),
                                              time_euro=datetime.now().replace(second=0, microsecond=0, tzinfo=None),
                                              time_yen=datetime.now().replace(second=0, microsecond=0, tzinfo=None),
                                              time_yuan=datetime.now().replace(second=0, microsecond=0, tzinfo=None), )
                record.save()
            else:
                pass

            # Если у пользователя вместо курса стоит ноль, то текущий курс сравнивается с максимальным и минимальным
            # за 7 предыдущих дней.
            if list(check_if_exist)[0][prev_req] == 0:
                # Обращаемся к БД с записями курса валют и находим максимумы и минимумы.
                max_value = list(ExchangeData.objects.filter(time_rate__range=(
                    f'{datetime.now().replace(second=0, microsecond=0) - data_delta}',
                    f'{datetime.now().replace(second=0, microsecond=0)}')).order_by(f'-{currency}').values('id', f'{currency}', 'time_rate'))[0]
                min_value = list(ExchangeData.objects.filter(time_rate__range=(
                    f'{datetime.now().replace(second=0, microsecond=0) - data_delta}',
                    f'{datetime.now().replace(second=0, microsecond=0)}')).order_by(f'{currency}').values('id', f'{currency}', 'time_rate'))[0]

                # Проверка ситуации, когда за выбранный промежуток времени курс и вырос, и упал на выбранный
                # пользователем процент.
                if ((self.current_dict[currency] / max_value[currency]) * 100 - 100 <= -self.percent) and (
                        (self.current_dict[currency] / min_value[currency]) * 100 - 100 >= self.percent):

                    # Случай, когда сначала был рост рубля, а потом падение.
                    if max_value['id'] <= min_value['id']:
                        final_message = final_message + str(f'Курс рубля к {text_templates[currency]} вырос больше чем на {self.percent}% '
                              f'по сравнению с курсом на {max_value["time_rate"].replace(tzinfo=None).strftime("%Y-%m-%d, %H:%M")},'
                              f' рубль вырос на {abs(round(((self.current_dict[currency] / max_value[currency]) * 100 - 100), 3))}%, '
                              f'значение курса изменилось с {max_value[currency]} до {self.current_dict[currency]}\n\n')
                        # Обновляем для пользователя запись о курсе, используя ранее созданный словарь.
                        UserPreviousMessages.objects.filter(user_id=self.user_id).update(**attribute_dict)

                    # Случай, когда сначала было падение рубля, а потом рост.
                    elif max_value['id'] >= min_value['id']:
                        final_message = final_message + str(f'Курс рубля к {text_templates[currency]} упал больше чем на {self.percent}% '
                              f'по сравнению с курсом на {min_value["time_rate"].replace(tzinfo=None).strftime("%Y-%m-%d, %H:%M")},'
                              f' рубль упал на {round(((self.current_dict[currency] / min_value[currency]) * 100 - 100), 3)}%, '
                              f'значение курса изменилось с {min_value[currency]} до {self.current_dict[currency]}\n\n')
                        # Обновляем для пользователя запись о курсе, используя ранее созданный словарь.
                        UserPreviousMessages.objects.filter(user_id=self.user_id).update(**attribute_dict)

                # Проверка ситуации, когда за выбранный промежуток времени курс вырос и при этом сильно не падал.
                elif ((self.current_dict[currency] / max_value[currency]) * 100 - 100 <= -self.percent) \
                        and ((self.current_dict[currency] / min_value[currency]) * 100 - 100 < self.percent):
                    final_message = final_message + str(f'Курс рубля к {text_templates[currency]} вырос больше чем на {self.percent}% '
                          f'по сравнению с курсом на {max_value["time_rate"].replace(tzinfo=None).strftime("%Y-%m-%d, %H:%M")}, '
                          f'рубль вырос на {abs(round(((self.current_dict[currency] / max_value[currency]) * 100 - 100), 3))}%, '
                          f'значение курса изменилось с {max_value[currency]} до {self.current_dict[currency]}\n\n')
                    # Обновляем для пользователя запись о курсе, используя ранее созданный словарь.
                    UserPreviousMessages.objects.filter(user_id=self.user_id).update(**attribute_dict)

                # Проверка ситуации, когда за выбранный промежуток времени курс упал и при этом сильно не вырастал.
                elif ((self.current_dict[currency] / max_value[currency]) * 100 - 100 > -self.percent) and (
                        (self.current_dict[currency] / min_value[currency]) * 100 - 100 >= self.percent):
                    final_message = final_message + str(f'Курс рубля к {text_templates[currency]} упал больше чем на {self.percent}% '
                          f'по сравнению с курсом на {min_value["time_rate"].replace(tzinfo=None).strftime("%Y-%m-%d, %H:%M")}, '
                          f'рубль упал на {round(((self.current_dict[currency] / min_value[currency]) * 100 - 100), 3)}%, '
                          f'значение курса изменилось с {min_value[currency]} до {self.current_dict[currency]}\n\n')
                    # Обновляем для пользователя запись о курсе, используя ранее созданный словарь.
                    UserPreviousMessages.objects.filter(user_id=self.user_id).update(**attribute_dict)
                else:
                    pass
            else:
                # У пользователя уже есть записи в БД, так что требуется текущий курс сравнить с ними и при
                # необходимости обновить.
                prev_curr = list(UserPreviousMessages.objects.filter(user_id=self.user_id).values(f'{prev_req}'))[0][f'{prev_req}']
                # Проверяем, не вырос ли рубль по сравнению с курсом, который был прислан в предыдущем сообщении.
                if ((self.current_dict[currency] / prev_curr) * 100 - 100) <= -self.percent:
                    final_message = final_message + str(f'Курс рубля к {text_templates[currency]} вырос больше чем на '
                                                        f'{self.percent}% по сравнению с курсом на '
                                                        f'{list(UserPreviousMessages.objects.filter(user_id=self.user_id).values(f"{time_prev}"))[0][f"{time_prev}"]}, '
                                                        f'когда была сделана предыдущая запись. Рубль вырос на '
                                                        f'{abs(round(((self.current_dict[currency] / prev_curr) * 100 - 100), 3))}%, '
                                                        f'значение курса изменилось с {prev_curr} '
                                                        f'до {self.current_dict[currency]}\n\n')
                    # Обновляем для пользователя запись о курсе, используя ранее созданный словарь.
                    UserPreviousMessages.objects.filter(user_id=self.user_id).update(**attribute_dict)

                # Проверяем, не упал ли рубль по сравнению с курсом, который был прислан в предыдущем сообщении.
                elif ((self.current_dict[currency] / prev_curr) * 100 - 100) >= self.percent:
                    final_message = final_message + str(f'Курс рубля к {text_templates[currency]} упал больше чем на '
                                                        f'{self.percent}% по сравнению с курсом на '
                                                        f'{list(UserPreviousMessages.objects.filter(user_id=self.user_id).values(f"{time_prev}"))[0][f"{time_prev}"]}, '
                                                        f'когда была сделана предыдущая запись. Рубль упал на '
                                                        f'{round(((self.current_dict[currency] / prev_curr) * 100 - 100), 3)}%, '
                                                        f'значение курса изменилось с {prev_curr} '
                                                        f'до {self.current_dict[currency]}\n\n')
                    # Обновляем для пользователя запись о курсе, используя ранее созданный словарь.
                    UserPreviousMessages.objects.filter(user_id=self.user_id).update(**attribute_dict)
                else:
                    pass
        # Возвращаем сформированное сообщение, если были значительные изменения в курсе, либо пустую строку, если нет.
        return final_message
