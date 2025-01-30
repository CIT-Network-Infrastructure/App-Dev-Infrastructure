import subprocess
import sys
import os
import ctypes
import getpass

from flaskappdb import FlaskAppDB, FlaskDB

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

SETTINGS = 'custom'

if SETTINGS == 'default':
    usr_install = input('Do you want to install the required packages? (yes/no) ')

    if 'HAS_REQS' in os.environ or usr_install in ['yes', 'y']:
        # Call the function
        install_requirements()

SERVER_MODE = os.getenv("SERVER_MODE") if "SERVER_MODE" in os.environ else input ('What is the server mode? ')
print(f'Server mode: {os.getenv("SERVER_MODE")}')
print(f'{os.getenv("DB_UN")}:{os.getenv("DB_PW")}'+\
	f'@{os.getenv("SERVER_HOSTNAME")}'+\
	f':5432/{os.getenv("DB_NAME")}')
def set_credentials(mode=SERVER_MODE, hostname=None):
    if mode == 'verdict':
        un = os.getenv("DB_UN")
        pw = os.getenv("DB_PW")
        hostnameServer = os.getenv("SERVER_HOSTNAME")
        db = os.getenv("DB_NAME")
    elif mode == 'home':
        un = 'postgres'
        pw = '12pg345'
        hostnameServer = '127.0.0.1'
        db = 'postgres'

    if hostname:
        hostnameServer = hostname
    port = '5432'

    print('Credintials set.')
    flaskdb = FlaskDB('AppDevDB', un, pw, hostnameServer, port, db)
    return flaskdb

CONFIG_MODE = 'dev'

APP_CREDENTIALS = set_credentials()

#App configuration dictionary
APP_CONFIG =    {
    'SQLALCHEMY_DATABASE_URI': APP_CREDENTIALS.make_uri(),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': os.urandom(24)
}

flaskapp = FlaskAppDB(
    name='AppDev-Development',
    config_mode=CONFIG_MODE,
    app_config=APP_CONFIG,
    flaskdb=APP_CREDENTIALS
    )
