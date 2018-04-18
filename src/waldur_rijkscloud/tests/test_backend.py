from django.core.exceptions import ObjectDoesNotExist
from rest_framework import test
from six.moves import mock

from . import factories, fixtures
from ..backend import RijkscloudBackendError, RijkscloudBackend
from .. import models


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
