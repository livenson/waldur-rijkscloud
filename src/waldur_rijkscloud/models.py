from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from waldur_core.core.fields import JSONField
from waldur_core.logging.loggers import LoggableMixin
from waldur_core.structure import models as structure_models


class RijkscloudService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project,
        related_name='rijkscloud_services',
        through='RijkscloudServiceProjectLink'
    )

    class Meta:
        unique_together = ('customer', 'settings')
        verbose_name = _('Rijkscloud provider')
        verbose_name_plural = _('Rijkscloud providers')

    @classmethod
    def get_url_name(cls):
        return 'rijkscloud'


class RijkscloudServiceProjectLink(structure_models.ServiceProjectLink):

    service = models.ForeignKey(RijkscloudService)

    class Meta(structure_models.ServiceProjectLink.Meta):
        verbose_name = _('Rijkscloud provider project link')
        verbose_name_plural = _('Rijkscloud provider project links')

    @classmethod
    def get_url_name(cls):
        return 'rijkscloud-spl'


class Flavor(LoggableMixin, structure_models.ServiceProperty):
    cores = models.PositiveSmallIntegerField(help_text=_('Number of cores in a VM'))
    ram = models.PositiveIntegerField(help_text=_('Memory size in MiB'))

    @classmethod
    def get_url_name(cls):
        return 'rijkscloud-flavor'

    @classmethod
    def get_backend_fields(cls):
        readonly_fields = super(Flavor, cls).get_backend_fields()
        return readonly_fields + ('cores', 'ram')


class Volume(structure_models.Volume):
    service_project_link = models.ForeignKey(
        RijkscloudServiceProjectLink,
        related_name='volumes',
        on_delete=models.PROTECT
    )
    metadata = JSONField(blank=True)

    @classmethod
    def get_url_name(cls):
        return 'rijkscloud-volume'


class Instance(structure_models.VirtualMachine):
    service_project_link = models.ForeignKey(
        RijkscloudServiceProjectLink,
        related_name='instances',
        on_delete=models.PROTECT
    )
    flavor_name = models.CharField(max_length=255, blank=True)

    @classmethod
    def get_url_name(cls):
        return 'rijkscloud-instance'
