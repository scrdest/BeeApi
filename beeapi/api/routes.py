from beeapi.api.app import get_app

app = get_app()


@app.get("/")
async def root():
    return {"message": "Hello Morkov"}
