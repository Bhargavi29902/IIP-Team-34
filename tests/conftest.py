import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.seed import seed_demo


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        seed_demo()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def _login(email="priya@demo.local", password="demo1234"):
        return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
    return _login
