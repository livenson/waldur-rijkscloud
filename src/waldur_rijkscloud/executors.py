from __future__ import unicode_literals

from celery import chain

from waldur_core.core import executors as core_executors
from waldur_core.core import tasks as core_tasks


class VolumePullExecutor(core_executors.ActionExecutor):
    action = 'Pull'

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return core_tasks.BackendMethodTask().si(
            serialized_volume, 'pull_volume',
            state_transition='begin_updating')


class VolumeCreateExecutor(core_executors.CreateExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return chain(
            core_tasks.BackendMethodTask().si(
                serialized_volume,
                'create_volume',
                state_transition='begin_creating'
            ),
            core_tasks.PollRuntimeStateTask().si(
                serialized_volume,
                backend_pull_method='pull_volume_runtime_state',
                success_state='available',
                erred_state='error',
            ).set(countdown=30)
        )


class InstancePullExecutor(core_executors.ActionExecutor):
    action = 'Pull'

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return core_tasks.BackendMethodTask().si(
            serialized_volume, 'pull_instance',
            state_transition='begin_updating')


class InstanceCreateExecutor(core_executors.CreateExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return chain(
            core_tasks.BackendMethodTask().si(
                serialized_volume,
                'create_instance',
                state_transition='begin_creating'
            ),
            core_tasks.PollRuntimeStateTask().si(
                serialized_volume,
                backend_pull_method='pull_instance_runtime_state',
                success_state='available',
                erred_state='error',
            ).set(countdown=30)
        )
