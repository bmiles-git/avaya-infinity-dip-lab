"""Start the API and attach admin routes.

This exists so a container built from GitHub still gets /admin
even if app/main.py is an older copy.
"""

import uvicorn

from app.admin_pages import router as admin_router
from app.main import app

if not any(getattr(route, "path", None) == "/admin" for route in app.routes):
    app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
