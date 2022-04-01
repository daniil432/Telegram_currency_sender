from datetime import datetime
import matplotlib.pyplot as plt


def create_plot(currency, start_date):
    from TeleBot.models import ExchangeData
    x = list(ExchangeData.objects.filter(time_rate__range=(
        f'{start_date}',
        f'{datetime.now().replace(second=0, microsecond=0)}')).values_list('time_rate', flat=True))
    y = list(ExchangeData.objects.filter(time_rate__range=(
        f'{start_date}',
        f'{datetime.now().replace(second=0, microsecond=0)}')).values_list(f'{currency}', flat=True))

    fig = plt.figure(figsize=(7, 5), dpi=100)
    fig.patch.set_facecolor('xkcd:mint green')
    ax = fig.add_subplot(111)
    ax.set_title(f'Graph of rouble to {currency.replace("_rate", "")} exchange rate', fontsize=15)
    ax.set_ylabel('Exchange rate', fontsize=15)
    ax.grid(alpha=0.6)
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    ax.plot(x, y, linewidth=3, color='#4cc94c', zorder=1)
    ax.scatter(x=x, y=y, s=15, zorder=2)
    plt.tight_layout()
    return plt
