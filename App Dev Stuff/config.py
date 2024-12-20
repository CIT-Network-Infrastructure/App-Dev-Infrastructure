import subprocess
import sys

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_cors import CORS

def install_requirements(requirements_file="requirements.txt"):
    try:
        # Run the pip install command
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print(f"Successfully installed packages from {requirements_file}.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing packages: {e}")
    except FileNotFoundError:
        print(f"File {requirements_file} not found. Please ensure it exists.")

# Call the function
install_requirements()

# Create Flask application
app = Flask(__name__)

un = 'postgres'
pw = '12pg345'
hostnameServer = 'crabby06'
db = 'postgres'

# un = 'verdict'
# pw = 'student'
# hostnameServer = '10.180.98.28'
# db = 'verdict'
# 
port = '5432'
app.config['SECRET_KEY'] = os.urandom(24)

# Database URI takes the form 'postgresql://username:password@host:port/database'
URI = f'postgresql+psycopg2://{un}:{pw}@{hostnameServer}:{port}/{db}'
print('App config complete.')

# app_context = app.app_context()
# app_context.push()

# # Initialize extensions
# db = SQLAlchemy(app)
# CORS(app)

CONFIG_MODE = 'dev'

#App configuration dictionary
APP_CONFIG =    {
    'SQLALCHEMY_DATABASE_URI': URI,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': os.urandom(24)
}

class FlaskAppDB:
    """Creates a `Flask` app instance with a `SQLAlchemy` database session.
    """
    def __init__(
                self, 
                 name: str, 
                 uri: str | None = URI, 
                 flask_app: Flask | None = None, 
                 database: SQLAlchemy | None = None,
                 app_context = None
                 ) -> None:
        self.name = f"{name}-{CONFIG_MODE}"
        self.app = flask_app
        self.database =  database
        self.uri = uri
        self.app_context = None
        self.config = None
        self.is_configured = False
        self.app_context = app_context
        self.has_context = False
        self.make_app()
    
    # App configuration method
    def configure_app(
            self,
            config_dict: dict[str, any]
            ) -> None:
        for variable, value in config_dict.items():
            self.app.config[variable] = value
        
        self.uri = config_dict['SQLALCHEMY_DATABASE_URI']
        self.config = config_dict
        self.is_configured = True
        print('App configured.')

    # Set context
    def set_app_context(self) -> None:
        app_context = self.app.app_context()
        app_context.push()
        self.app_context = app_context
        self.has_context = True
        print('App context set.')

    # App creation method
    def make_app(
            self, 
            CONFIG_DICT: dict[str, any]=APP_CONFIG
        ) -> None:

        # Create a Flask app
        self.app = Flask(__name__)
        
        # Set app.config variables
        self.configure_app(CONFIG_DICT)
        
        self.database = SQLAlchemy(self.app)

        if self.uri is not None:
            print (f"Connected to database at URI '{self.uri}'")
            return
        else:
            raise ValueError("'SQLALCHEMY_DATABASE_URI' must be set in order to connect to a database")
        
    def init_db(self, schema=None, create=True,  drop=False, insert=False, **kwargs):
        
        self.set_app_context()
        if self.app:
            CORS(self.app)
        if schema:
            with self.app_context:
                self.database.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                return schema
        
        with self.app_context:
            if create:

                if drop:
                    print('d')
                    self.database.drop_all()
                    print('Dropped all tables')
                print('c')
                self.database.create_all()
                print('Successfully created tables')
        
        if insert:
            for key, value in kwargs.items():
                self.database.session.add_all(value)
                self.database.session.commit()
                print(f"Successfully added {key} to database")