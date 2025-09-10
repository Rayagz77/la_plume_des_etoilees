import unittest
from app import create_app
from models import db, User

class TestRegisterRoute(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        # IMPORTANT : base de données éphémère en mémoire
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite://",
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
            'user_password': 'securepassword123',
            'user_phone': '+1234567890'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Inscription réussie", self.body(response))
        with self.app.app_context():
            user = User.query.filter_by(user_email='johndoe@example.com').first()
            self.assertIsNotNone(user)

    def test_register_invalid_email(self):
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'invalid-email',
            'user_password': 'securepassword123',
            'user_phone': '+1234567890'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Veuillez entrer une adresse email valide", self.body(response))

    def test_register_short_password(self):
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'janedoe@example.com',
            'user_password': 'short',
            'user_phone': '+1234567890'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Le mot de passe doit contenir au moins 12 caractères.", self.body(response))

    def test_register_duplicate_email(self):
        with self.app.app_context():
            u = User(
                user_firstname="John",
                user_lastname="Doe",
                user_email="johndoe@example.com",
                user_phone="+1234567890"
            )
            u.set_password("securepassword123")
            db.session.add(u)
            db.session.commit()

        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'johndoe@example.com',
            'user_password': 'securepassword123',
            'user_phone': '+1234567890'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cet email est déjà utilisé.", self.body(response))

    def test_register_invalid_phone(self):
        response = self.client.post('/register', data={
            'user_firstname': 'Jane',
            'user_lastname': 'Doe',
            'user_email': 'janedoe@example.com',
            'user_password': 'securepassword123',
            'user_phone': 'invalid-phone'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Veuillez entrer un numéro de téléphone valide.", self.body(response))

    def test_register_missing_fields(self):
        response = self.client.post('/register', data={
            'user_firstname': '',
            'user_lastname': '',
            'user_email': '',
            'user_password': '',
            'user_phone': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Le prénom et le nom doivent contenir au moins 3 caractères.", self.body(response))

if __name__ == '__main__':
    unittest.main()
