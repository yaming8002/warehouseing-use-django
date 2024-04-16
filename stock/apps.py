from django.apps import AppConfig


class WhseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock'
    
    # def ready(self):
    #     from .middleware.update_stock import stock_pre_save_receiver