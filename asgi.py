from app.app_factory import create_app

application = create_app(include_worker=False)
