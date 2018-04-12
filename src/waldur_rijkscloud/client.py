import json

import requests


class RijkscloudClient(object):
    """
    Rijkscloud Python client.
    """

    def __init__(self, apikey, userid):
        self.base_url = 'https://cst.rijkscloud.nl/api'
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': apikey,
            'userid': userid,
        }

    def _get(self, endpoint, key):
        url = '%s/%s' % (self.base_url, endpoint)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        if key:
            return data[key]
        else:
            return data

    def _post(self, endpoint, body):
        url = '%s/%s' % (self.base_url, endpoint)
        response = requests.post(url, headers=self.headers, data=json.dumps(body))
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint):
        url = '%s/%s' % (self.base_url, endpoint)
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def list_flavors(self):
        return self._get('flavors', 'flavors')

    def get_instance(self, instance_name):
        url = 'instances/%s' % instance_name
        return self._get(url, 'instance')

    def list_instances(self):
        instances = self._get('instances', 'instances')
        return [self.get_instance(instance['name']) for instance in instances]

    def create_instance(self, body):
        return self._post('instances', body)

    def delete_instance(self, instance_name):
        return self._delete('instances/%s' % instance_name)

    def get_network(self, network_name):
        subnets = self.list_subnets(network_name)
        return dict(name=network_name, subnets=subnets)

    def list_networks(self):
        networks = self._get('networks', 'networks')
        return [self.get_network(network['name']) for network in networks]

    def list_floatingips(self):
        return self._get('networks/floats', 'floats')

    def get_subnet(self, network_name, subnet_name):
        url = 'networks/%s/subnets/%s' % (network_name, subnet_name)
        subnet = self._get(url, None)
        floatingips = self.list_subnet_floatingips(network_name, subnet_name)
        return dict(name=subnet_name, floatingips=floatingips, **subnet)

    def list_subnet_floatingips(self, network_name, subnet_name):
        url = 'networks/%s/subnets/%s/ips' % (network_name, subnet_name)
        return self._get(url, 'ips')

    def list_subnets(self, network_name):
        url = 'networks/%s/subnets' % network_name
        subnets = self._get(url, 'subnets')
        return [self.get_subnet(network_name, subnet['name']) for subnet in subnets]

    def get_volume(self, volume_name):
        url = 'volumes/%s' % volume_name
        return self._get(url, 'volume')

    def list_volumes(self):
        volumes = self._get('volumes', 'volumes')
        return [self.get_volume(volume['name']) for volume in volumes]

    def create_volume(self, body):
        return self._post('volume', body)

    def delete_volume(self, volume_name):
        return self._delete('volume/%s' % volume_name)
