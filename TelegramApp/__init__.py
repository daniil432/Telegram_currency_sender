from .celery import app as celery_app

# Нужно для Celery
__all__ = ('celery_app',)
