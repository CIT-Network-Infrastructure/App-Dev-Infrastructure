import os
import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import Sequence

# Create Flask application
app = Flask(__name__)
hostnameServer = '10.180.98.17'
# '10.180.98.17'
app.config['SECRET_KEY'] = os.urandom(24)
# Database URI takes the form 'postgresql://username:password@host:port/database'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://verdict:student@'+hostnameServer+':5432/verdict'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print('App config complete.')

app_context = app.app_context()
app_context.push()

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
print('Database variable declared.')
# Create a sequence for ports
port_sequence = Sequence('port_sequence', start=4000)

class User(db.Model):
    """User model for database"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    port = db.Column(db.Integer, server_default=port_sequence.next_value(), unique=True, nullable=False)

    def __init__(self, username, password):
        """
        Initialize a new user
        
        :param username: User's username
        :param password: User's password
        """
        self.username = username
        self.password_hash = self._hash_password(password)

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using SHA-256
        
        :param password: Plain text password
        :return: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        """
        Check if provided password is correct
        
        :param password: Password to check
        :return: True if password is correct, False otherwise
        """
        return self.password_hash == self._hash_password(password)

print("Creating tables...")
db.create_all()
print("Successfully created tables.")

print('Creating dummy user...')
newuser = User("Cameron Joyce", "joycece", "12345")
with app.app_context():
    db.session.add(newuser)
    db.session.commit()
print("Successfully added user to database")

