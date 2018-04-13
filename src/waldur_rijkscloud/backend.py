from django.utils import timezone

from waldur_core.structure import log_backend_action, ServiceBackend, ServiceBackendError
from waldur_core.structure.utils import update_pulled_fields

from . import models
from .client import RijkscloudClient


class RijkscloudBackendError(ServiceBackendError):
    pass


class RijkscloudBackend(ServiceBackend):

    def __init__(self, settings):
        self.settings = settings
        self.client = RijkscloudClient(
            userid=settings.options['username'],
            apikey=settings.options['token'],
        )

    def sync(self):
        self.pull_flavors()
        self.pull_volumes()
        self.pull_instances()

    def pull_flavors(self):
        pass

    def pull_volumes(self):
        pass

    def pull_instances(self):
        pass

    @log_backend_action()
    def pull_volume(self, volume, update_fields=None):
        import_time = timezone.now()
        imported_volume = self.import_volume(volume.backend_id, save=False)

        volume.refresh_from_db()
        if volume.modified < import_time:
            if not update_fields:
                update_fields = models.Volume.get_backend_fields()

            update_pulled_fields(volume, imported_volume, update_fields)

    @log_backend_action()
    def pull_instance(self, instance, update_fields=None):
        import_time = timezone.now()
        imported_instance = self.import_instance(instance.backend_id, save=False)

        instance.refresh_from_db()
        if instance.modified < import_time:
            if update_fields is None:
                update_fields = models.Instance.get_backend_fields()
            update_pulled_fields(instance, imported_instance, update_fields)

    @log_backend_action()
    def create_volume(self, volume):
        pass

    @log_backend_action()
    def create_instance(self, instance):
        pass
