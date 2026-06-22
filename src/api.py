"""Main FastAPI application."""

from fastapi import FastAPI

from . import routes_multiplayer, routes_legacy

app = FastAPI(
    title="Dominos API",
    description="Multiplayer Dominos game API with local persistence and token authentication.",
    version="1.0.0"
)

# Mount routers
app.include_router(routes_multiplayer.router)
app.include_router(routes_legacy.router)


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "message": "Dominos Multiplayer API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "multiplayer": "POST /games, POST /games/{game_id}/join, etc.",
        "legacy": "POST /start, GET /state, POST /move, etc.",
    }
