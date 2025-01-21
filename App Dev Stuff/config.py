import subprocess
import sys
import os
import ctypes

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_cors import CORS

# Function to check if the script is running as admin on Windows
def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

# Function to run command as admin on Windows
def run_as_admin_windows(command):
    if not is_admin():
        # Re-run the script as admin
        print("Not running as admin, relaunching as administrator...")
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        except OSError:
            print("OSError: Check permissions.")
        except:
            print("Unxepected error")
    else:
        print("Running as default user.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
        # subprocess.run(command, shell=True)

def install_requirements(requirements_file="requirements.txt"):
    with open(requirements_file, 'r') as file:
        packages = file.readlines()
    skipped = []
    # Iterate over each package in the requirements file
    for package in packages:
        package = package.strip()
        if not package:
            continue  # Skip empty lines

        try:
            print(f"Installing {package}...")
            command = [sys.executable, "-m", "pip", "install", package]
            result = subprocess.run(command,  check=True, text=True, capture_output=True)
            if "Requirement already satisfied" in result.stdout:
                print(f"{package} already installed.")

        except subprocess.CalledProcessError as e:
            print(f"Error installing package {package}: {e}")
            if "No matching distribution" in e.stderr:
                print(f"Skipping {package} due to no matching distribution.")
                skipped.append(package)
            elif "Check the permissions." in e.stderr:
                # run_as_admin_windows(command)
                print(f"{package} skipped: missing.")
            else:
                print(f"Standard Output:\n{e.stdout}")
                print(f"Standard Error:\n{e.stderr}")
        except OSError as e:
            if e.errno == 13:
                print("Access denied. Elevated permissions required.")
            else:
                print(f"An unexpected OSError occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while installing package: {e}")

    if not not skipped:
        print((f"{package}, " for package in skipped), "skipped due ot no matching distribution.")
    os.environ['HAS_REQS'] = 'TRUE'
    print(f"Successfully installed packages from {requirements_file}.")


if 'HAS_REQS' not in os.environ:
    # Call the function
    install_requirements()

SERVER_MODE = 'home'

def build_uri(
        mode=SERVER_MODE, 
        hostname=None):
    if mode == 'verdict':
        un = 'verdict'
        pw = 'student'
        hostnameServer = 'verdict'
        db = 'verdict'
    elif mode == 'home':
        un = 'postgres'
        pw = '12pg345'
        hostnameServer = '127.0.0.1'
        db = 'postgres'

    if hostname:
        hostnameServer = hostname
    port = '5432'

    # Database URI takes the form 'postgresql://username:password@host:port/database'
    URI = f'postgresql+psycopg2://{un}:{pw}@{hostnameServer}:{port}/{db}'
    return URI

CONFIG_MODE = 'dev'

#App configuration dictionary
APP_CONFIG =    {
    'SQLALCHEMY_DATABASE_URI': build_uri(),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': os.urandom(24)
}

class FlaskAppDB:
    """Creates a `Flask` app instance with a `SQLAlchemy` database session.
    """
    def __init__(
                self, 
                 name: str, 
                 uri: str | None = build_uri(), 
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
        
        CORS(self.app)
        print('CORS configured.')
        
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
            print("App ready for use.")
            return
        else:
            raise ValueError("'SQLALCHEMY_DATABASE_URI' must be set in order to connect to a database")
        
        
        
    def init_db(self, schema=None, create=True,  drop=False, insert=False, **kwargs):
        
        self.set_app_context()
        if schema:
            with self.app_context:
                self.database.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                return schema
        
        with self.app_context:
            if create:

                if drop:
                    print('Dropping tables...')
                    self.database.drop_all()
                    print('Dropped all tables')
                print('Creating database tables...')
                self.database.create_all()
                print('Successfully created tables.')
        
        if insert:
            for key, value in kwargs.items():
                self.database.session.add_all(value)
                self.database.session.commit()
                print(f"Successfully added {key} to database")
        print("Successfully initialized database.")
        