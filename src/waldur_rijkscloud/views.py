from __future__ import unicode_literals

import six

from waldur_core.structure import views as structure_views

from . import models, serializers, filters, executors


class ServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.RijkscloudService.objects.all()
    serializer_class = serializers.ServiceSerializer


class ServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.RijkscloudServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer
    filter_class = filters.ServiceProjectLinkFilter


class FlavorViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Flavor.objects.all()
    serializer_class = serializers.FlavorSerializer
    lookup_field = 'uuid'
    filter_class = filters.FlavorFilter


class VolumeViewSet(six.with_metaclass(structure_views.ResourceViewMetaclass,
                                       structure_views.ResourceViewSet)):
    queryset = models.Volume.objects.all()
    serializer_class = serializers.VolumeSerializer
    filter_class = filters.VolumeFilter

    create_executor = executors.VolumeCreateExecutor
    pull_executor = executors.VolumePullExecutor


class InstanceViewSet(six.with_metaclass(structure_views.ResourceViewMetaclass,
                                         structure_views.ResourceViewSet)):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer
    filter_class = filters.InstanceFilter
    pull_executor = executors.InstancePullExecutor
    create_executor = executors.InstanceCreateExecutor
