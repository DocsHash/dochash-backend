from litestar import Router, get, post
from .api_handlers import api_controller

# API routes
api_router = Router(
    path="/api",
    route_handlers=[
        post(path="/process-document")(api_controller.process_document),
        post(path="/verify-document")(api_controller.verify_document)
    ]
)

# Root routes
root_router = Router(
    path="/",
    route_handlers=[
        get(path="/")(api_controller.health_check)
    ]
)

# Combined routes
routers = [root_router, api_router]