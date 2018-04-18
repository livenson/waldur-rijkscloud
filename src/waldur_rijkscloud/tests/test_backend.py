from django.core.exceptions import ObjectDoesNotExist
from rest_framework import test
from six.moves import mock

from . import factories, fixtures
from .. import models
from ..backend import RijkscloudBackend


class FlavorPullTest(test.APITransactionTestCase):
    def setUp(self):
        super(FlavorPullTest, self).setUp()

        patcher = mock.patch('waldur_rijkscloud.backend.RijkscloudClient')
        patcher.start()

        self.fixture = fixtures.RijkscloudFixture()
        self.backend = RijkscloudBackend(settings=self.fixture.service_settings)

    def tearDown(self):
        super(FlavorPullTest, self).tearDown()
        mock.patch.stopall()

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


class VolumeImportTest(test.APITransactionTestCase):
    def setUp(self):
        super(VolumeImportTest, self).setUp()

        patcher = mock.patch('waldur_rijkscloud.backend.RijkscloudClient')
        patcher.start()

        self.fixture = fixtures.RijkscloudFixture()
        self.backend = RijkscloudBackend(settings=self.fixture.service_settings)

    def tearDown(self):
        super(VolumeImportTest, self).tearDown()
        mock.patch.stopall()

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
