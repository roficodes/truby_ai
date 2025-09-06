from fastapi import FastAPI

app = FastAPI(
    title="Truby AI: Your Screenwriting Assistant!",
    summary="Having trouble with your screenplay's beats? Truby AI will help you out.",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=None #TODO: Include lifespan for async client and database connections!
)

@app.get("/")
def get_root():
    return {
        "App": "Root Page",
        "Summary": "Having trouble with your screenplay's beats? Truby AI will help you out.",
    }