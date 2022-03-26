from django.db import models
from django.urls import reverse


class ExchangeData(models.Model):
    dollar_rate = models.FloatField(max_length=10, help_text="Dollar exchange rate")
    euro_rate = models.FloatField(max_length=10, help_text="Euro exchange rate")
    yen_rate = models.FloatField(max_length=10, help_text="Yen exchange rate")
    yuan_rate = models.FloatField(max_length=10, help_text="Yuan exchange rate")
    time_rate = models.DateTimeField(help_text="Time when rate was obtained")

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])

    def __datetime__(self):
        return self.time_rate

    def __float__(self):
        return self.dollar_rate, self.euro_rate, self.yen_rate, self.yuan_rate


class TelebotUsers(models.Model):
    username = models.CharField(max_length=1000, help_text="Username of the person that using this bot")
    join_date = models.DateTimeField(help_text="Date when user started to use bot")
    sending_status = models.BooleanField(help_text="True if user wants to get messages "
                                                   "from this bot about changes in exchange rate")
    percent_user = models.IntegerField(default=5, help_text="Percents that user wants to use in check_rate")
    user_currency = models.CharField(max_length=1000, help_text="Currencies that user selected for automessages",
                                     default="dollar_rate")

    def __datetime__(self):
        return self.join_date

    def __str__(self):
        return self.username, self.user_currency

    def __bool__(self):
        return self.sending_status

    def __int__(self):
        return self.percent_user
