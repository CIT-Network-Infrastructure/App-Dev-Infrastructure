import hashlib
from sqlalchemy import Sequence
import psycopg2
import sqlalchemy.exc as se

from config import FlaskAppDB


flask = FlaskAppDB('AppDev-Development')

app = flask.app
db = flask.database

# Create a sequence for ports
port_sequence = Sequence('port_sequence', start=4000)

class User(db.Model):
    """User model for database"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    port = db.Column(db.Integer, nullable=False, unique=True,  default=lambda: User.get_next_port())

    def __init__(self, name, username, password):
        """
        Initialize a new user
        
        :param username: User's username
        :param password: User's password
        """

        self.name = name
        self.username = username
        self.password_hash = self._hash_password(password)

    @staticmethod
    def get_next_port():
        last_record = User.query.order_by(User.port.desc()).first()
        return 4000 if not last_record else last_record.port + 1

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

flask.init_db()

def createDummy(name, username: str, password):
    print('Creating dummy user...')
    newuser = User(name=name, username=username, password=password) 
    with app.app_context():
        try:
            db.session.add(newuser)
            db.session.commit()
            print("Successfully added user to database")
        except psycopg2.OperationalError:
            return "Cannot connect to server (TCP/IP)"
        except AttributeError as err:
            return f"AttributeError: {err}"
        except se.IntegrityError as err:
            if isinstance(err.orig, psycopg2.errors.UniqueViolation):
                return f"Unique Viloation: User with username {username} already exists."
            return f"se.IntegrityError: {err}"
        finally:
            db.session.rollback()
         
    try:
        newuser = User.query.filter_by(username=username).first()
        id = newuser.id
        return id
    except AttributeError as err:
        return err

print(createDummy("John Doe", "doej", "23456"))


