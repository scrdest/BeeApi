import datetime
import os
import invoke

import beeapi.constants


@invoke.task
def run_api(c, port=None, workers=None, reload=False, background=False):
    _port = port or beeapi.constants.DEFAULT_API_PORT
    raw_commands = []

    raw_commands.append("python -m")
    raw_commands.append("beeapi.api")
    raw_commands.append(f"--port {_port}")

    if reload:
        raw_commands.append("--reload")

    if workers:
        raw_commands.append("--workers")
        raw_commands.append(workers)

    run_command = " ".join(raw_commands)
    runstate = c.run(run_command, disown=bool(background))
    return runstate


@invoke.task
def run_query(c, query):
    from beeapi.cli.cli import run_app_once
    result = run_app_once(query)
    print(result)
    return


@invoke.task
def run_app(c):
    from beeapi.cli.cli import run_app
    run_app()
    return


@invoke.task
def run_indexing(c, filepath=None, force=False):
    _filepath = filepath or beeapi.constants.DEFAULT_DICT_PATH
    from beeapi.core.parsing import OFFCategoriesDictParser
    parsed = (
        OFFCategoriesDictParser.parse(_filepath) if force
        else OFFCategoriesDictParser.parse_cached(_filepath)
    )
    return parsed


def _build_image(tag=None, dev=False):
    _tag = tag or beeapi.constants.DEFAULT_DOCKER_TAG

    raw_commands = []
    target = "dev" if dev else "prod"

    raw_commands.append("docker build")
    if _tag:
        raw_commands.append(f"-t {_tag}")

    raw_commands.append(f"--target {target}")
    raw_commands.append(".")

    run_command = " ".join(raw_commands)

    return run_command


@invoke.task
def build_image(c, tag=None):
    _tag = tag or beeapi.constants.DEFAULT_DOCKER_TAG

    raw_commands = []
    build_cmd = _build_image(
        tag=tag,
        dev=False
    )

    raw_commands.append(build_cmd)
    if _tag:
        raw_commands.append(f"-t {_tag}")

    run_command = " ".join(raw_commands)
    c.run(run_command)

    return


@invoke.task
def build_dev_image(c, tag=None):
    _tag = tag or beeapi.constants.DEFAULT_DOCKER_TAG

    raw_commands = []
    build_cmd = _build_image(
        tag=tag,
        dev=True
    )

    raw_commands.append(build_cmd)
    if _tag:
        raw_commands.append(f"-t {_tag}")

    run_command = " ".join(raw_commands)
    c.run(run_command)

    return


@invoke.task
def run_image_cmd(c, cmd, tag=None):
    _tag = tag or beeapi.constants.DEFAULT_DOCKER_TAG
    raw_commands = []

    raw_commands.append("docker run")
    raw_commands.append(_tag)
    raw_commands.append(f"-it {cmd}")

    run_command = " ".join(raw_commands)
    c.run(run_command)
    return


@invoke.task
def run_indexing_dockerized(c, tag=None):
    _tag = tag or beeapi.constants.DEFAULT_DOCKER_TAG
    raw_commands = []

    raw_commands.append("docker run")
    raw_commands.append(_tag)
    raw_commands.append(f"inv run-indexing")

    run_command = " ".join(raw_commands)
    c.run(run_command)
    return


@invoke.task
def run_app_dockerized(c, tag=None):
    _tag = tag or beeapi.constants.DEFAULT_DOCKER_TAG
    raw_commands = []

    raw_commands.append("docker run")
    raw_commands.append(_tag)
    raw_commands.append(f"inv run-app")

    run_command = " ".join(raw_commands)
    c.run(run_command)
    return


@invoke.task
def run_api_dockerized(c, tag=None):
    _tag = tag or beeapi.constants.DEFAULT_DOCKER_TAG
    raw_commands = []

    raw_commands.append("docker run")
    raw_commands.append(_tag)
    raw_commands.append(f"inv run-api")

    run_command = " ".join(raw_commands)
    c.run(run_command)
    return


@invoke.task
def unit_test(c):
    raw_commands = []

    raw_commands.append("python -m pytest")
    raw_commands.append(beeapi.constants.UNIT_TESTS_DIR)

    run_command = " ".join(raw_commands)
    c.run(run_command)
    return


@invoke.task
def functional_test(c):
    raw_commands = []

    raw_commands.append("python -m pytest")
    raw_commands.append(beeapi.constants.FUNC_TESTS_DIR)

    run_command = " ".join(raw_commands)
    c.run(run_command)
    return


@invoke.task
def load_test(
    c,
    simple=False,
    workers=None,
    maxusers=None,
    test_time=None,
    port=None,
):

    _workers = None if not workers else int(workers)
    _maxusers = maxusers or 100
    _test_time = test_time or "5m"
    _port = port or beeapi.constants.DEFAULT_API_PORT

    testfile = os.path.join(beeapi.constants.LOAD_TESTS_DIR, "load.py")

    raw_commands = []

    raw_commands.append("locust")
    raw_commands.append(f"-f {testfile}")
    raw_commands.append(f"--host http://localhost:{_port}")

    if simple:
        raw_commands.append("--tags simple")

    raw_commands.append("--headless")
    raw_commands.append(f"--csv reports/load-test-report-{int(datetime.datetime.utcnow().timestamp())}")
    raw_commands.append(f"--users {_maxusers}")
    raw_commands.append(f"--run-time {_test_time}")

    if _workers:
        raw_commands.append("--master")
        raw_commands.append(f"--expect-workers {_workers}")

        worker_cmd = f"locust -f {testfile} --worker"
        for worker_idx in range(_workers):
            c.run(worker_cmd, asynchronous=True)


    run_command = " ".join(raw_commands)
    c.run(run_command, dry=True)

    return

