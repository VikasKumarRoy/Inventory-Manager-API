from django.apps import AppConfig


class ItemConfig(AppConfig):
    name = 'item'

    def ready(self):
        import item.signals
