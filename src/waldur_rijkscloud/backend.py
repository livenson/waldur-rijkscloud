from django.db import transaction
from django.utils import timezone
import requests
import six

from waldur_core.structure import log_backend_action, ServiceBackend, ServiceBackendError
from waldur_core.structure.utils import (
    update_pulled_fields, handle_resource_not_found, handle_resource_update_success)

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

    def ping(self, raise_exception=False):
        try:
            self.client.list_flavors()
        except requests.RequestException as e:
            if raise_exception:
                six.reraise(RijkscloudBackendError, e)
            return False
        else:
            return True

    def sync(self):
        self.pull_flavors()
        self.pull_volumes()
        self.pull_instances()

    def _get_current_properties(self, model):
        return {p.backend_id: p for p in model.objects.filter(settings=self.settings)}

    def pull_flavors(self):
        try:
            flavors = self.client.list_flavors()
        except requests.RequestException as e:
            six.reraise(RijkscloudBackendError, e)

        with transaction.atomic():
            cur_flavors = self._get_current_properties(models.Flavor)
            for backend_flavor in flavors:
                cur_flavors.pop(backend_flavor['name'], None)
                models.Flavor.objects.update_or_create(
                    settings=self.settings,
                    backend_id=backend_flavor['name'],
                    defaults={
                        'name': backend_flavor['name'],
                        'cores': backend_flavor['vcpus'],
                        'ram': backend_flavor['ram'],
                    })

            models.Flavor.objects.filter(backend_id__in=cur_flavors.keys()).delete()

    def pull_volumes(self):
        backend_volumes = self.get_volumes()
        volumes = models.Volume.objects.filter(
            service_project_link__service__settings=self.settings,
            state__in=[models.Volume.States.OK, models.Volume.States.ERRED]
        )
        backend_volumes_map = {backend_volume.backend_id: backend_volume for backend_volume in backend_volumes}
        for volume in volumes:
            try:
                backend_volume = backend_volumes_map[volume.backend_id]
            except KeyError:
                handle_resource_not_found(volume)
            else:
                update_pulled_fields(volume, backend_volume, models.Volume.get_backend_fields())
                handle_resource_update_success(volume)

    def get_volumes(self):
        try:
            backend_volumes = self.client.list_volumes()
        except requests.RequestException as e:
            six.reraise(RijkscloudBackendError, e)
        else:
            return [self._backend_volume_to_volume(backend_volume)
                    for backend_volume in backend_volumes]

    def _backend_volume_to_volume(self, backend_volume):
        return models.Volume(
            name=backend_volume['name'],
            size=backend_volume['size'] * 1024,
            metdata=backend_volume['metdata'],
            runtime_state=backend_volume['status'],
            state=models.Volume.States.OK,
        )

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
