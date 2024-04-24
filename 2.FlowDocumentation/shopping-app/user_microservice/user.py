from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

current_file_location = os.path.dirname(__file__)

DATABASE = os.path.join(current_file_location, 'users.db')

def create_users_table(reset=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if reset:
        cursor.execute('''DROP TABLE IF EXISTS users''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT UNIQUE NOT NULL,
                       email TEXT UNIQUE NOT NULL,
                       password TEXT NOT NULL,
                       full_name TEXT NOT NULL,
                       registration_date TEXT NOT NULL,
                       account_status TEXT NOT NULL,
                       role TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def populate_users_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # List of hardcoded user data
    user_data = [
    # id, username,  email,              password,        full_name, registration_date,   account_status, role
        ("john_doe", "john@example.com", "password123", "John Doe", "2022-01-01 12:00:00", "active", "admin"),
        ("jane_smith", "jane@example.com", "pass123", "Jane Smith", "2022-01-02 14:30:00", "active", "user"),
        ("alex_123", "alex@example.com", "alexpass", "Alex Johnson", "2022-01-03 10:15:00", "active", "user"),
        ("emily_456", "emily@example.com", "emilypass", "Emily Brown", "2022-01-04 09:45:00", "inactive", "user"),
        ("mike_789", "mike@example.com", "mikepass", "Mike Taylor", "2022-01-05 11:20:00", "active", "user"),
        ("sara_111", "sara@example.com", "sarapass", "Sara Williams", "2022-01-06 13:10:00", "active", "admin"),
        ("adam_222", "adam@example.com", "adampass", "Adam Smith", "2022-01-07 15:30:00", "inactive", "user"),
        ("lisa_333", "lisa@example.com", "lisapass", "Lisa Johnson", "2022-01-08 16:45:00", "active", "user"),
        ("chris_444", "chris@example.com", "chrispass", "Chris Brown", "2022-01-09 18:00:00", "active", "user"),
        ("mary_555", "mary@example.com", "marypass", "Mary Taylor", "2022-01-10 20:20:00", "inactive", "user"),
        ("peter_666", "peter@example.com", "peterpass", "Peter Wilson", "2022-01-11 22:45:00", "active", "user"),
        ("laura_777", "laura@example.com", "laurapass", "Laura Davis", "2022-01-12 09:30:00", "active", "user"),
        ("steve_888", "steve@example.com", "stevepass", "Steve Johnson", "2022-01-13 11:40:00", "inactive", "user"),
        ("julia_999", "julia@example.com", "juliapass", "Julia Smith", "2022-01-14 14:00:00", "active", "user"),
        ("david_101", "david@example.com", "davidpass", "David Brown", "2022-01-15 16:20:00", "active", "admin"),
        ("amy_202", "amy@example.com", "amypass", "Amy Taylor", "2022-01-16 18:45:00", "active", "user"),
        ("brian_303", "brian@example.com", "brianpass", "Brian Wilson", "2022-01-17 20:10:00", "inactive", "user"),
        ("kate_404", "kate@example.com", "katepass", "Kate Davis", "2022-01-18 22:30:00", "active", "user"),
        ("ryan_505", "ryan@example.com", "ryanpass", "Ryan Johnson", "2022-01-19 09:15:00", "active", "user"),
    ]

    # Insert hardcoded user data into the database
    for user in user_data:
        cursor.execute('''INSERT INTO users (username, email, password, full_name, registration_date, account_status, role)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''', user)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

create_users_table(reset=True)
populate_users_table()

@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    account_status = 'active'  # Default to active upon registration
    role = 'user'  # Default role for new users

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO users (username, email, password, full_name, registration_date, account_status, role)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (username, email, password, full_name, registration_date, account_status, role))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username or email already exists'}), 400

@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM users WHERE username=? AND password=?''', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[4],
            'registration_date': user[5],
            'account_status': user[6],
            'role': user[7]
        }
        return jsonify(user_data), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

# Function to retrieve user information by user ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Retrieve user data from the database by user ID
    cursor.execute('''SELECT * FROM users WHERE id=?''', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        # If user exists, return user data
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[4],
            'registration_date': user[5],
            'account_status': user[6],
            'role': user[7]
        }
        return jsonify(user_data), 200
    else:
        # If user does not exist, return error message
        return jsonify({'error': 'User not found'}), 404
    
# Function to retrieve user information by username
@app.route('/users/username/<string:username>', methods=['GET'])
def get_user_by_username(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM users WHERE username=?''', (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[4],
            'registration_date': user[5],
            'account_status': user[6],
            'role': user[7]
        }
        return jsonify(user_data), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# Function to retrieve all users
@app.route('/users', methods=['GET'])
def get_all_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM users''')
    users = cursor.fetchall()
    conn.close()

    user_list = []
    for user in users:
        user_data = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[4],
            'registration_date': user[5],
            'account_status': user[6],
            'role': user[7]
        }
        user_list.append(user_data)

    return jsonify(user_list), 200

# Function to update user information
@app.route('/users/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json

    # Check if user exists
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE id=?''', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Update user information
    try:
        cursor.execute('''UPDATE users SET 
                          username=?, email=?, password=?, full_name=? 
                          WHERE id=?''',
                       (data.get('username', user[1]), data.get('email', user[2]), 
                        data.get('password', user[3]), data.get('full_name', user[4]), 
                        user_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User information updated successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# Function to delete a user
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Check if user exists
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE id=?''', (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Delete user
    try:
        cursor.execute('''DELETE FROM users WHERE id=?''', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User deleted successfully'}), 200
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=9050, debug=True)