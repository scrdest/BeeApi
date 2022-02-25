from invoke import Collection, Program
from beeapi import constants
from beeapi.mgmt import tasks

program = Program(
    namespace=Collection.from_module(tasks),
    version=constants.BEEAPI_VERSION,
    name="BeeManage"
)
