from litestar import Router, get, post
from app.api_handlers import api_controller

api_router = Router(
    path="/api",
    route_handlers=[
        post(path="/process-document")(api_controller.process_document),
        post(path="/verify-document")(api_controller.verify_document)
    ]
)

root_router = Router(
    path="/",
    route_handlers=[
        get(path="/")(api_controller.health_check)
    ]
)

routers = [root_router, api_router]
