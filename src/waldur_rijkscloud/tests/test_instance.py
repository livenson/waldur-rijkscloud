from rest_framework import status, test

from . import factories, fixtures


class InstanceCreateTest(test.APITransactionTestCase):
    def test_user_can_create_instance(self):
        fixture = fixtures.RijkscloudFixture()
        url = factories.InstanceFactory.get_list_url()
        self.client.force_login(fixture.owner)
        response = self.client.post(url, {
            'name': 'Test Instance',
            'service_project_link': factories.ServiceProjectLinkFactory.get_url(fixture.spl),
            'flavor': factories.FlavorFactory.get_url(fixture.flavor),
            'internal_ip': factories.InternalIPFactory.get_url(fixture.internal_ip),
            'floating_ip': factories.FloatingIPFactory.get_url(fixture.floating_ip),
        })
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_user_can_not_create_instance_if_floating_ip_is_not_available(self):
        fixture = fixtures.RijkscloudFixture()
        fixture.floating_ip.is_available = False
        fixture.floating_ip.save()

        url = factories.InstanceFactory.get_list_url()
        self.client.force_login(fixture.owner)

        response = self.client.post(url, {
            'name': 'Test Instance',
            'service_project_link': factories.ServiceProjectLinkFactory.get_url(fixture.spl),
            'flavor': factories.FlavorFactory.get_url(fixture.flavor),
            'internal_ip': factories.InternalIPFactory.get_url(fixture.internal_ip),
            'floating_ip': factories.FloatingIPFactory.get_url(fixture.floating_ip),
        })
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
