import random
import string

from userdb import User
from userdb import db
from sqlalchemy.exc import IntegrityError


# Generate random names for the example
first_names = ["John", "Jane", "Alice", "Bob", "Chris", "Dana", "Eve", "Frank", "Grace", "Hank"]
last_names = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]

def generate_username(first, last):
    return (last[:5] + first[0]).lower()

def generate_password(length=5):
    return ''.join(random.choices(string.digits, k=length))
# Generate the data array
data = []
for _ in range(50):
    first = random.choice(first_names)
    last = random.choice(last_names)
    full_name = f"{first} {last}"
    username = generate_username(first, last)
    password = generate_password()
    data.append([full_name, username, password])

# Save to a .txt file in table format
with open("user_table.txt", "w") as file:
    file.write(f"{'Full Name':<20}{'Username':<15}{'Password':<10}\n")
    file.write("-" * 45 + "\n")
    for entry in data:
        file.write(f"{entry[0]:<20}{entry[1]:<15}{entry[2]:<10}\n")
        new_user = User(entry[0], entry[1], entry[2])
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            new_user = User(entry[0], entry[1], entry[2])
            db.session.add(new_user)
            db.session.commit()

print("Data has been written to user_table.txt.")
