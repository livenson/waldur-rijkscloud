from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from waldur_core.core import serializers as core_serializers
from waldur_core.structure import serializers as structure_serializers
from . import models


class ServiceSerializer(core_serializers.ExtraFieldOptionsMixin,
                        structure_serializers.BaseServiceSerializer):
    SERVICE_ACCOUNT_FIELDS = {
        'username': '',
        'token': '',
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.RijkscloudService
        extra_field_options = {
            'username': {
                'label': 'User ID',
                'required': True
            },
            'token': {
                'label': 'API key',
                'required': True
            },
        }


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):
    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.RijkscloudServiceProjectLink
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'rijkscloud-detail'},
        }


class FlavorSerializer(structure_serializers.BasePropertySerializer):
    class Meta(structure_serializers.BasePropertySerializer.Meta):
        model = models.Flavor
        fields = ('url', 'uuid', 'name', 'settings', 'cores', 'ram',)
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'settings': {'lookup_field': 'uuid'},
        }


class VolumeSerializer(structure_serializers.BaseResourceSerializer):
    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='rijkscloud-detail',
        read_only=True,
        lookup_field='uuid')
    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='rijkscloud-spl-detail',
        queryset=models.RijkscloudServiceProjectLink.objects.all(),
    )

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Volume
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'size', 'runtime_state')
        read_only_fields = structure_serializers.BaseResourceSerializer.Meta.read_only_fields + (
            'runtime_state',)
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'size',)
        extra_kwargs = dict(
            size={'required': False, 'allow_null': True},
            **structure_serializers.BaseResourceSerializer.Meta.extra_kwargs
        )


class InstanceSerializer(structure_serializers.VirtualMachineSerializer):
    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='rijkscloud-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='rijkscloud-spl-detail',
        queryset=models.RijkscloudServiceProjectLink.objects.all())

    flavor = serializers.HyperlinkedRelatedField(
        view_name='rijkscloud-flavor-detail',
        lookup_field='uuid',
        queryset=models.Flavor.objects.all().select_related('settings'),
        write_only=True)

    class Meta(structure_serializers.VirtualMachineSerializer.Meta):
        model = models.Instance
        fields = structure_serializers.VirtualMachineSerializer.Meta.fields + (
            'flavor',)
        protected_fields = structure_serializers.VirtualMachineSerializer.Meta.protected_fields + (
            'flavor',)
        read_only_fields = structure_serializers.VirtualMachineSerializer.Meta.read_only_fields + (
            'flavor_name',)

    def validate(self, attrs):
        # skip validation on object update
        if self.instance is not None:
            return attrs

        service_project_link = attrs['service_project_link']
        settings = service_project_link.service.settings
        flavor = attrs['flavor']

        if flavor.settings != settings:
            raise serializers.ValidationError(
                _('Flavor must belong to the same service settings as service project link.'))

        return attrs
