import os
from celery import Celery
from celery.schedules import crontab
from ExchangeRate.messages import Currency


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TelegramApp.settings')
app = Celery('TelegramApp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

"Делаем записи в базу данных о курсе валюты"
# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html
app.conf.beat_schedule = {'create_record_task': {'task': 'TeleBot.tasks.create_record',
                                                 'schedule': crontab(minute='*/1'), 'args':
                                                     (float(Currency().get_currency_price()[0].replace(",", ".")),
                                                      float(Currency().get_currency_price()[1].replace(",", ".")),
                                                      float(Currency().get_currency_price()[2].replace(",", ".")),
                                                      float(Currency().get_currency_price()[3].replace(",", ".")),)
                                                 },
                          'create_rate_task': {'task': 'TeleBot.tasks.check_rate',
                                               'schedule': crontab(minute='*/1'), 'args':
                                                     (float(Currency().get_currency_price()[0].replace(",", ".")),
                                                      float(Currency().get_currency_price()[1].replace(",", ".")),
                                                      float(Currency().get_currency_price()[2].replace(",", ".")),
                                                      float(Currency().get_currency_price()[3].replace(",", ".")),)
                                               }
                          }
