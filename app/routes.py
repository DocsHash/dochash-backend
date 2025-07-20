from litestar import Router, get, post
from app.api_handlers import APIController

api_router = Router(
    path="/api",
    route_handlers=[
        post(path="/process-document")(APIController.process_document),
        post(path="/verify-document")(APIController.verify_document)
    ]
)

root_router = Router(
    path="/",
    route_handlers=[
        get(path="/")(APIController.health_check)
    ]
)


routers = [root_router, api_router]
