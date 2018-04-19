from django.core.exceptions import ObjectDoesNotExist
from rest_framework import test
from six.moves import mock

from . import factories, fixtures
from .. import models
from ..backend import RijkscloudBackend


class BaseBackendTest(test.APITransactionTestCase):
    def setUp(self):
        super(BaseBackendTest, self).setUp()

        patcher = mock.patch('waldur_rijkscloud.backend.RijkscloudClient')
        patcher.start()

        self.fixture = fixtures.RijkscloudFixture()
        self.backend = RijkscloudBackend(settings=self.fixture.service_settings)

    def tearDown(self):
        super(BaseBackendTest, self).tearDown()
        mock.patch.stopall()


class FlavorPullTest(BaseBackendTest):
    def test_new_flavors_are_created(self):
        self.backend.client.list_flavors.return_value = [
            {
                'name': 'general.8gb',
                'vcpus': 4,
                'ram': 8192
            },
            {
                'name': 'general.4gb',
                'vcpus': 2,
                'ram': 4096
            },
            {
                'name': 'general.2gb',
                'vcpus': 1,
                'ram': 2048
            }
        ]
        self.backend.pull_flavors()
        self.assertEqual(models.Flavor.objects.count(), 3)

    def test_old_flavors_are_removed(self):
        old_flavor = factories.FlavorFactory(settings=self.fixture.service_settings, name='stale')
        self.backend.client.list_flavors.return_value = [
            {
                'name': 'general.8gb',
                'vcpus': 4,
                'ram': 8192
            },
        ]
        self.backend.pull_flavors()
        self.assertEqual(models.Flavor.objects.count(), 1)
        self.assertRaises(ObjectDoesNotExist, old_flavor.refresh_from_db)


class VolumeImportTest(BaseBackendTest):

    def test_existing_volumes_are_skipped(self):
        factories.VolumeFactory(service_project_link=self.fixture.spl, backend_id='stale')
        self.backend.client.list_volumes.return_value = [
            {
                'attachments': [],
                'description': None,
                'metadata': {},
                'name': 'stale',
                'size': 1,
                'status': 'available'
            },
            {
                'attachments': [],
                'description': None,
                'metadata': {},
                'name': 'new',
                'size': 2,
                'status': 'available'
            }
        ]
        volumes = self.backend.get_volumes_for_import()
        self.assertEqual(len(volumes), 1)
        self.assertEqual(volumes[0].backend_id, 'new')

    def test_import_volume(self):
        self.backend.client.get_volume.return_value = {
            'attachments': [],
            'description': None,
            'metadata': {},
            'name': 'test',
            'size': 2,
            'status': 'available'
        }
        volume = self.backend.import_volume('test', service_project_link=self.fixture.spl)
        self.assertEqual(volume.name, 'test')
        self.assertEqual(volume.size, 2048)
        self.assertEqual(volume.runtime_state, 'available')


class FloatingIpPullTest(BaseBackendTest):
    def setUp(self):
        super(FloatingIpPullTest, self).setUp()
        self.backend.client.list_floatingips.return_value = [
            {
                'available': False,
                'float_ip': '123.21.42.121'
            },
            {
                'available': True,
                'float_ip': '97.21.42.121'
            },
        ]

    def test_new_floating_ips_are_created(self):
        self.backend.pull_floating_ips()
        self.assertEqual(models.FloatingIP.objects.count(), 2)

    def test_old_floating_ips_are_removed(self):
        old_fip = factories.FloatingIPFactory(
            settings=self.fixture.service_settings, backend_id='8.8.8.8')
        self.backend.pull_floating_ips()
        self.assertEqual(models.FloatingIP.objects.count(), 2)
        self.assertRaises(ObjectDoesNotExist, old_fip.refresh_from_db)
