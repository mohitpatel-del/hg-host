from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        animal TEXT NOT NULL,
                        house TEXT NOT NULL,
                        views_on_magic TEXT NOT NULL)''')
    conn.commit()
    conn.close()


# Root route
@app.route('/')
def home():
    return redirect(url_for('signup'))  # Redirect to signup page by default

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        first_name = data.get('First-name')
        last_name = data.get('Last-name')
        username = data.get('username')
        password = data.get('password')
        animal = data.get('Animals')
        house = data.get('houses')
        views_on_magic = data.get('textarea')

        if not all([first_name, last_name, username, password, animal, house, views_on_magic]):
            return jsonify({'error': 'All fields are required'}), 400

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users 
                              (first_name, last_name, username, password, animal, house, views_on_magic) 
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                           (first_name, last_name, username, hashed_password, animal, house, views_on_magic))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 409
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    return render_template('login.html')

