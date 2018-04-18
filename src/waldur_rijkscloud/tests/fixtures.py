from django.utils.functional import cached_property

from waldur_core.structure.tests.fixtures import ProjectFixture

from . import factories


class RijkscloudFixture(ProjectFixture):
    @cached_property
    def service_settings(self):
        return factories.ServiceSettingsFactory(customer=self.customer)

    @cached_property
    def service(self):
        return factories.ServiceFactory(customer=self.customer, settings=self.service_settings)

    @cached_property
    def spl(self):
        return factories.ServiceProjectLinkFactory(project=self.project, service=self.service)
