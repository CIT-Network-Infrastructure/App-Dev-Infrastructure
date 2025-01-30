## test python file
import os
try:
	from flask import (
			Flask,
			render_template,
			url_for,
			redirect
			)
	from flask_sqlalchemy import SQLAlchemy
	import psycopg2
	import time, threading
except ImportError:
	print("Imports failed.")
	os._exit(0)

app = Flask(__name__)

host = 'drhscit.org'
database = 'db_cejoy'
user = 'cejoy'
password = '56106'
port = '5432'


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

def countdown(seconds, message=None):
	for remaining in range(seconds, 0, -1):
		print(f"{message}... {remaining} seconds left", end="\r")
		time.sleep(1)
	print(" " * 40, end="\r")  # Clear the countdown line

def check_connection(timeout_limit=10) -> bool:
	"""
	Checks if the database connection is active by attempting to make a `psycopg2` connection
	"""
	print(f'Checking connection to database \'{database}\' at host \'{host}\'')
	timer_thread = threading.Thread(target=countdown, args=(10, "Attempting to connect"))
	timer_thread.start()
	try:
		# Connect to the PostgreSQL database
		conn = psycopg2.connect(
			host=host,
			database=database,
			user=user,
			password=password ,
			port=port,
			connect_timeout=timeout_limit
			)
		print("Connection check passed!")
		conn.close()
		return True
	except psycopg2.Error as e:
		# Wait for the timer thread to finish (optional)
		timer_thread.join()
		print(f"Connection check failed: {str(e)}")
		print("Exiting program in 5 seconds...")
		threading.Thread(target=countdown, args=(5, "Exiting program")).start()
		time.sleep(5)
		os._exit(0)
		return False


# # Start the countdown in a separate thread
# timer_thread = threading.Thread(target=countdown, args=(10, "Attempting to connect"))
# timer_thread.start()

# # Attempt to connect to the database
# connection = check_connection()

# if not connection:
# 	# Wait for the timer thread to finish (optional)
# 	timer_thread.join()

# if connection: print("Continuing...", end="\r")

print("Setting app context...")
app_context = app.app_context()
app_context.push()
print("App context set.")

db = SQLAlchemy(app)

class Student(db.Model):
	__tablename__ = 'students'
	name = db.Column(db.String(100))
	age = db.Column(db.Integer)
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	bio = db.Column(db.Text)

print("Creating database tables.")
db.create_all()
print("Successfully created tables.")

student1 = Student(name='James', age=16, id=2, bio='I love eating bugs.')
student2 = Student(name='Alice', age=12, id=1, bio='I\'m in 5th grade.')
db.session.add_all([student1, student2])
print("Successfully added 2 students to database")


@app.route('/')
def index():
	db_items = Student.query.all()
	return render_template('index.html', records=db_items)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
