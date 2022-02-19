import invoke


@invoke.task
def run_api(c):
    raw_commands = []

    raw_commands.append("uvicorn")
    raw_commands.append("beeapi.api.app:app")
    raw_commands.append("--reload")

    run_command = " ".join(raw_commands)
    c.run(run_command)


if __name__ == '__main__':
    context = invoke.Context()
    run_api(context)
