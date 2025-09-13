import os
import unittest

# Configurer l'app pour utiliser SQLite en mémoire **avant** l'import
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite://")

from app import create_app
from models import db, User

class TestRegisterRoute(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def body(self, response):
        return response.get_data(as_text=True)

    def test_register_success(self):
        response = self.client.post('/register', data={
            'user_firstname': 'John',
            'user_lastname': 'Doe',
            'user_email': 'johndoe@example.com',
            'user_password': 'Securepassword123!',
            'user_phone': '+1234567890',
            'consent_data': 'on'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(user_email='johndoe@example.com').first()
            self.assertIsNotNone(user)

    def test_register_invalid_email(self):
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'invalid-email',
            'user_password': 'Securepassword123!',
            'user_phone': '+1234567890',
            'consent_data': 'on'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(user_email='invalid-email').first()
            self.assertIsNone(user)

    def test_register_short_password(self):
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'janedoe@example.com',
            'user_password': 'short',
            'user_phone': '+1234567890',
            'consent_data': 'on'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(user_email='janedoe@example.com').first()
            self.assertIsNone(user)

    def test_register_duplicate_email(self):
        with self.app.app_context():
            u = User(
                user_firstname="John",
                user_lastname="Doe",
                user_email="johndoe@example.com",
                user_phone="+1234567890"
            )
            u.set_password("Securepassword123!")
            db.session.add(u)
            db.session.commit()

        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'johndoe@example.com',
            'user_password': 'Securepassword123!',
            'user_phone': '+1234567890',
            'consent_data': 'on'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            count = User.query.filter_by(user_email='johndoe@example.com').count()
            self.assertEqual(count, 1)

    def test_register_invalid_phone(self):
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'janedoe@example.com',
            'user_password': 'Securepassword123!',
            'user_phone': 'invalid-phone',
            'consent_data': 'on'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(user_email='janedoe@example.com').first()
            self.assertIsNone(user)

    def test_register_missing_fields(self):
        response = self.client.post('/register', data={
            'user_firstname': '',
            'user_lastname': '',
            'user_email': '',
            'user_password': '',
            'user_phone': '',
            'consent_data': 'on'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            users = User.query.all()
            self.assertEqual(len(users), 0)

if __name__ == '__main__':
    unittest.main()
