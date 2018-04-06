from django.apps import AppConfig


class RijkscloudConfig(AppConfig):
    name = 'waldur_rijkscloud'
    verbose_name = 'rijkscloud'

    def ready(self):
        pass
