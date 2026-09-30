"""Start the API and attach admin and PIN verify routes."""

import uvicorn

from app.admin_pages import router as admin_router
from app.main import app
from app.pin_api import router as pin_router

if not any(getattr(route, "path", None) == "/admin" for route in app.routes):
    app.include_router(admin_router)
if not any(getattr(route, "path", None) == "/api/v1/verify" for route in app.routes):
    app.include_router(pin_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
