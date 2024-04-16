from django.apps import AppConfig


class TransConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trans'

    # def ready(self):
    #     from .middleware.update_stock import stock_post_save_receiver
