from fastapi import FastAPI

app = None


def get_config():
    options = dict(
        debug=True,
        title="BeeAPI"
    )
    return options


def build_app(config=None):
    _config = config or get_config()
    new_app = FastAPI(**_config)
    return new_app


def get_app(config=None):
    global app

    if config or not app:
        app = build_app(config=config)

    return app
