import psycopg2
from psycopg2 import sql
import pandas as pd

# Database connection parameters for the admin user
ADMIN_USER = "verdict"  # Replace with your admin username
ADMIN_PASSWORD = "student"  # Replace with your admin password
HOST = "10.1.10.95"
PORT = "5432"
DATABASE = "verdict"  # Admin database name

# Path to the spreadsheet file
SPREADSHEET_FILE = "students.xlsx"  # Replace with your spreadsheet file path

# Read the spreadsheet to get the list of students
students_df = pd.read_excel(SPREADSHEET_FILE)

# Ensure the spreadsheet has 'username' and 'password' columns
if 'username' not in students_df.columns or 'password' not in students_df.columns:
    raise ValueError("The spreadsheet must contain 'username' and 'password' columns.")

# Convert the DataFrame to a list of dictionaries
students = students_df.to_dict(orient="records")

def create_student_environment():
    try:
        # Connect to the PostgreSQL server as the admin user
        connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=ADMIN_USER,
            password=ADMIN_PASSWORD,
            database=DATABASE
        )
        connection.autocommit = True  # Enable autocommit mode
        cursor = connection.cursor()

        for student in students:
            username = student["username"]
            password = student["password"]
            schema_name = f"schema_{username}"
            database_name = f"db_{username}"

            # 1. Create a new role for the student
            cursor.execute(sql.SQL(
                """
                CREATE ROLE {username} WITH LOGIN PASSWORD %s;
                """
            ).format(username=sql.Identifier(username)), [password])

            print(f"Role created for {username}")

            # 2. Create a new database for the student
            cursor.execute(sql.SQL(
                """
                CREATE DATABASE {database_name} OWNER {username};
                """
            ).format(
                database_name=sql.Identifier(database_name),
                username=sql.Identifier(username)
            ))

            print(f"Database {database_name} created for {username}")

            # 3. Connect to the newly created database and create the schema
            student_connection = psycopg2.connect(
                host=HOST,
                port=PORT,
                user=ADMIN_USER,
                password=ADMIN_PASSWORD,
                database=database_name
            )
            student_connection.autocommit = True
            student_cursor = student_connection.cursor()

            # Create schema
            student_cursor.execute(sql.SQL(
                """
                CREATE SCHEMA {schema_name} AUTHORIZATION {username};
                """
            ).format(
                schema_name=sql.Identifier(schema_name),
                username=sql.Identifier(username)
            ))

            print(f"Schema {schema_name} created for {username}")

            # Close the student database connection
            student_cursor.close()
            student_connection.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the admin connection
        if connection:
            cursor.close()
            connection.close()

# Run the script
if __name__ == "__main__":
    create_student_environment()
