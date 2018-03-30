from django.apps import AppConfig


class IndexConfig(AppConfig):
    name = 'home'

    def ready(self):
        import home.signals
