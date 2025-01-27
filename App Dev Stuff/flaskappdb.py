import psycopg2
import time
import threading

from os import (
        system as sys,
        _exit as stop_program,
        name as osname
    )

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_cors import CORS

class FlaskDB:
    """
    Creates a `FlaskDB` instance. This class can generate database URIs and check database connections.
    """
    def __init__(self,
                 name: str | None = None,
                 username: str | None = None,
                 pw: str | None = None,
                 host: str | None = None,
                 port: str | None = '5432',
                 db: str | None = None,
                 ):
        """
        Initializes the `FlaskDB` class.
        :param name: An optional name for the instance
        :param username: The username for the database user
        :param pw: the password for the database user
        :param host: the hostname of the device on which teh database is hosted
        :param port: the port on which the database is hosted. Defaults to 5432, the default port for PostgreSQL database hosting
        :param db: the name of the database to be accessed
        """
        self.name = name
        self.username = username
        self.password = pw
        self.hostname = host
        self.port = port
        self.database = db
        
        # Start the countdown in a separate thread
        timer_thread = threading.Thread(target=countdown, args=(10,))
        timer_thread.start()

        # Attempt to connect to the database
        connection = self.check_connection()

        # Wait for the timer thread to finish (optional)
        timer_thread.join()
        self.conn_active = True if connection else False

    def make_uri(self) -> str:
        """
        Derives a database URI given the attributes of the instance.
        Database URI takes the form 'dbtype://username:password@host:port/database'
        """
        return f'postgresql+psycopg2://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}'

    def check_connection(self) -> bool:
        """
        Checks if the database connection is active by attempting to make a `psycopg2` connection
        """
        print(f'Checking connection to database \'{self.database}\' at host \'{self.hostname}\'')
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host=self.hostname,
                database=self.database,
                user=self.username,
                password=self.password ,
                port=self.port,
                connect_timeout=10
            )
            print("Connection check passed!")
            conn.close()
            return True
        except psycopg2.Error as e:
            print(f"Connection check failed: {str(e)}")
            return False


def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        print(f"Attempting to connect... {remaining} seconds left", end="\r")
        time.sleep(1)
    print(" " * 40, end="\r")  # Clear the countdown line

    

class FlaskAppDB:
    """
    Creates a `Flask` app instance with a `SQLAlchemy` database session.
    """
    def __init__(
                self, 
                 name: str | None = None, 
                 uri: str | None = None, 
                 flask_app: Flask | None = None, 
                 flaskdb: FlaskDB | None = None,
                 app_context = None,
                 config_mode = None,
                 app_config = None
                 ) -> None:
        """
        Initializes a `FlaskAppDB` instance.
        :param name: An optional (but recommended) name for the instance
        :param uri: Optionally assign a predetermined database URI
        :param flask_app: Optionally assign a preexisting `Flask` instance
        :param app_context: Optionally assign app context associated with the `Flask` instance was passed as an argument (`flask_app`)
        :param config_mode: Optionally assign a config mode (development/production/testing)
        :param app_config: An optional dictionary of `app.config` settings
        """
        self.name = f"{name}" + (f"-{config_mode}" if config_mode else "")
        self.app = flask_app
        self.flaskdb =  flaskdb
        self.sql_alchemy = None
        self.uri = uri
        self.config = app_config
        self.is_configured = False
        self.app_context = app_context
        self.has_context = False
        self.make_app(self.config)
    
    # App configuration method
    def configure_app(
            self,
            config_dict: dict[str, any]
            ) -> None:
        """
        Configures `app.config` variables and sets up Cross Origin Resource Sharing.
        :param config_dict: A dictionary listing assignments for the `app.config` variables
        """
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
        """
        Sets app context for database access.
        """
        app_context = self.app.app_context()
        app_context.push()
        self.app_context = app_context
        self.has_context = True
        print('App context set.')

    # App creation method
    def make_app(
            self, 
            CONFIG_DICT: dict[str, any] = None
        ) -> None:
        """
        Creates and configures a `Flask` instance for the app, then runs `make_db()` to create a `SQLAlchemy` session. If this method executes without error, the app is ready for use and will indicate as such in the terminal. Exits the program if database connection fails.
        :param config_dict: A dictionary listing assignments for the `app.config` variables
        """
        # Create a Flask app
        self.app = Flask(__name__)

        # Set app.config variables
        self.configure_app(CONFIG_DICT)
        
        #Check database connection
        conn_active = True if self.flaskdb.conn_active else self.make_db()
        
        #Clear console
        if osname == 'nt': sys('cls')
        else: sys('clear')

        #Status update
        if conn_active:
            print("App ready for use.") 
        else:
            print("Connection Failed.")
            stop_program(0)
        
    def make_db(
            self,
            username: str | None = None,
            pw: str | None = None,
            host: str = '127.0.0.1',
            port: str = '5432',
            db: str | None = None
            ) -> bool:
        """
        Creates a `SQLAlchemy` session for the app. This method also instantiates a `FlaskDB` object if not previously defined and sets the `FlaskAppDB`'s `uri` attribute.
        :param username: The username for the database user
        :param pw: the password for the database user
        :param host: the hostname of the device on which teh database is hosted
        :param port: the port on which the database is hosted. Defaults to 5432, the default port for PostgreSQL database hosting
        :param db: the name of the database to be accessed
        """
        
        self.sql_alchemy = SQLAlchemy(self.app)
        if not self.flaskdb:
            print('No FlaskDB instance found. Configuring now.')
            self.flaskdb = FlaskDB('AppDevDB', host=host, username=username, pw=pw, port=port, db=db)
        
        self.uri = self.flaskdb.make_uri()

        if self.uri is not None:
            print (f"URI set: '{self.uri}'")
            pass
        else:
            raise ValueError("'SQLALCHEMY_DATABASE_URI' must be set in order to connect to a database")
        
        return self.flaskdb.conn_active
    
    def init_db(self, schema=None, create=True,  drop=False, insert=False, **kwargs):
        """
        Initializes the database. Sets app context and optionally creates and/or drops tables before optionally inserting values into the databse tables.
        Example use::

            CONFIG_MODE = 'dev'
            flaskdb = FlaskDB('ExampleDB', 'user1', '12345', '127.0.0.1', '5432', 'postgres')

            #App configuration dictionary
            APP_CONFIG =    {
                'SQLALCHEMY_DATABASE_URI': flaskdb.make_uri(),
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                'SECRET_KEY': os.urandom(24)
            }
            flaskapp = FlaskAppDB(name='ExampleApp', config_mode=CONFIG_MODE, app_config=APP_CONFIG, flaskdb=flaskdb)
            
            user1 = User(username='cej', password='12345').
            flaskapp.init_db(insert=True, user1)
            
        :param create: Whether to create the database tables upon launching the database. Defaults to `True`.
        :param drop: Whether to create the database tables upon launching the database. Defaults to `False`. If set to `True`, the database tables will lose all of their data.
        :insert: Whether to insert new objects into the database table. Defaults to `False`. If set to true, the method will attempt to add objects passed as optional keyword argumemnts (`**kwargs`) to the database.
        :param **kwargs: Optional keyword arguments. These should be database table objects, like shown above.
        """
        self.set_app_context()
        if schema:
            with self.app_context:
                self.sql_alchemy.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                return schema
        
        with self.app_context:
            if create:

                if drop:
                    print('Dropping tables...')
                    self.sql_alchemy.drop_all()
                    print('Dropped all tables')
                print('Creating database tables...')
                self.sql_alchemy.create_all()
                print('Successfully created tables.')
        
        if insert:
            for key, value in kwargs.items():
                self.sql_alchemy.session.add_all(value)
                self.sql_alchemy.session.commit()
                print(f"Successfully added {key} to database")
        print("Successfully initialized database.")
        