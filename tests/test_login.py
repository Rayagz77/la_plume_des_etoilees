import os
import unittest

os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite://")

from app import create_app
from models import db, User

class TestLoginWelcome(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            u = User(
                user_firstname="John",
                user_lastname="Doe",
                user_email="john@example.com",
            )
            u.set_password("Securepassword123!")
            db.session.add(u)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_welcome_message(self):
        resp = self.client.post(
            "/auth/login",
            data={"user_email": "john@example.com", "user_password": "Securepassword123!"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        self.assertIn("Bienvenue John !", body)

if __name__ == "__main__":
    unittest.main()
