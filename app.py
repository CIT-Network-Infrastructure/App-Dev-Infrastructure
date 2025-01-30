from flask import session, render_template, request, url_for, redirect, jsonify, flash
from functools import wraps
from userdb import User, app, db


def login_required(f):
    """
    Decorator to require login for specific routes

    :param f: Route function
    :return: Wrapped route function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return  """jsonify({"error": "Unauthorized"})""", 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint

    :return: Registration result
    """

    # Validate input
    if not request.form or not request.form['username'] or not request.form['password']:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Check if user already exists
        existing_user = User.query.filter_by(username=request.form['username']).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 409

        # Create new user
        new_user = User(
            name=request.form['fullname'],
            username=request.form['username'],
            password=request.form['password']
        )

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('signin'))
        # jsonify({
        #     "message": "User registered successfully",
        #     "user_id": new_user.id,
        #     "port": new_user.port
        # }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login endpoint

    :return: Login result
    """

    # Validate input
    if not request.form or not request.form['username'] or not request.form['password']:
        return jsonify({"error": "Username and password are required"}), 400

    # Find user
    user = User.query.filter_by(username=request.form['username']).first()

    # Check credentials
    if user and user.check_password(request.form['password']):
        # Create session
        session['user_id'] = user.id
        return redirect(url_for('get_profile'))# jsonify({"message": "Successfully logged in"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    User logout endpoint

    :return: Logout result
    """
    session.pop('user_id', None)
    return redirect(url_for('index'))#, jsonify({"message": "Logged out successfully"}), 200

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """
    Change user password endpoint

    :return: Password change result
    """
    data = request.get_json()

    # Validate input
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({"error": "Old and new passwords are required"}), 400

    try:
        # Find current user
        user = User.query.get(session['user_id'])

        # Verify old password
        if not user.check_password(data['old_password']):
            return jsonify({"error": "Current password is incorrect"}), 400

        # Update password
        user.password_hash = user._hash_password(data['new_password'])
        db.session.commit()

        return jsonify({"message": "Password changed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Get user profile endpoint

    :return: User profile information
    """
    user = User.query.get(session['user_id'])
    return render_template('home.html', user=user)#  , jsonify({
    #     "id": user.id,
    #     "username": user.username,
    #     "port": user.port
    # }), 200

def create_tables():
    """
    Create database tables
    """
    with app.app_context():
        print('Creating tables...')
        db.create_all()
        print('Successfully created tables.')


# Home page that displays all the events
@app.route('/')
def landing():
    return redirect(url_for('index'))

@app.route('/dashboard')
def index():
    return render_template('index.html')

@app.route('/home/<username>')
def home(username):
    return render_template('home.html', user=username)

# Allows users to sign up for an account
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('login2.html')

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=7000)
