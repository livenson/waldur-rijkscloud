from random import randint
import uuid

from django.urls import reverse
import factory

from waldur_core.structure.tests import factories as structure_factories

from .. import models


class ServiceSettingsFactory(structure_factories.ServiceSettingsFactory):
    type = 'Rijkscloud'
    username = 'admin'
    token = 'secret'


class ServiceFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.RijkscloudService

    settings = factory.SubFactory(ServiceSettingsFactory)
    customer = factory.SubFactory(structure_factories.CustomerFactory)

    @classmethod
    def get_url(cls, service=None, action=None):
        if service is None:
            service = ServiceFactory()
        url = 'http://testserver' + reverse('rijkscloud-detail', kwargs={'uuid': service.uuid})
        return url if action is None else url + action + '/'

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('rijkscloud-list')


class ServiceProjectLinkFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.RijkscloudServiceProjectLink

    service = factory.SubFactory(ServiceFactory)
    project = factory.SubFactory(structure_factories.ProjectFactory)

    @classmethod
    def get_url(cls, spl=None, action=None):
        if spl is None:
            spl = ServiceProjectLinkFactory()
        url = 'http://testserver' + reverse('rijkscloud-spl-detail', kwargs={'pk': spl.pk})
        return url if action is None else url + action + '/'

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('rijkscloud-spl-list')


class FlavorFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Flavor

    name = factory.Sequence(lambda n: 'flavor%s' % n)
    settings = factory.SubFactory(structure_factories.ServiceSettingsFactory)

    cores = 2
    ram = 2 * 1024

    backend_id = factory.Sequence(lambda n: 'flavor-id%s' % n)

    @classmethod
    def get_url(cls, flavor=None):
        if flavor is None:
            flavor = FlavorFactory()
        return 'http://testserver' + reverse('rijkscloud-flavor-detail', kwargs={'uuid': flavor.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('rijkscloud-flavor-list')


class VolumeFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Volume

    name = factory.Sequence(lambda n: 'volume%s' % n)
    service_project_link = factory.SubFactory(ServiceProjectLinkFactory)
    size = 10 * 1024
    backend_id = factory.LazyAttribute(lambda _: str(uuid.uuid4()))

    @classmethod
    def get_url(cls, instance=None, action=None):
        if instance is None:
            instance = VolumeFactory()
        url = 'http://testserver' + reverse('rijkscloud-volume-detail', kwargs={'uuid': instance.uuid})
        return url if action is None else url + action + '/'

    @classmethod
    def get_list_url(cls, action=None):
        url = 'http://testserver' + reverse('rijkscloud-volume-list')
        return url if action is None else url + action + '/'


class FloatingIPFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.FloatingIP

    name = factory.Sequence(lambda n: 'floating_ip%s' % n)
    settings = factory.SubFactory(ServiceProjectLinkFactory)
    address = factory.LazyAttribute(lambda o: '.'.join('%s' % randint(0, 255) for _ in range(4)))

    @classmethod
    def get_url(cls, instance=None):
        if instance is None:
            instance = FloatingIPFactory()
        return 'http://testserver' + reverse('rijkscloud-fip-detail', kwargs={'uuid': instance.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('rijkscloud-fip-list')
