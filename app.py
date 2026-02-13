# Doing all imports
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'rolsa_secure_key'

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Checks your login credentials
def check_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = check_login(username, password)
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['first_name'] = user[4]
        session['surname'] = user[5]
        session['dob'] = user[6]
        return redirect(url_for('welcome'))
    else:
        flash('Invalid Username or Password.')
        return redirect(url_for('index'))

def username_exists(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email'].strip()
        confirm_email = request.form['confirm_email'].strip()
        first_name = request.form['first_name']
        surname = request.form['surname']
        dob = request.form['dob']

        if email != confirm_email:
            flash('Emails do not match, Please try again.')
            return redirect(url_for('signup'))

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            flash('Invalid email format, Please use a valid email address.')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match, Please try again.')
            return redirect(url_for('signup'))

        if (len(password) < 8 or
            not any(c.isupper() for c in password) or
            not any(c.isdigit() for c in password) or
            not any(c in '!@#$%^&*()_+' for c in password)):
            flash('Password must be: 8+ chars, 1 uppercase, 1 number, and 1 special character (!@#$%^&*)')
            return redirect(url_for('signup'))

        conn = sqlite3.connect('users.db')
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password, email, first_name, surname, dob) VALUES(?,?,?,?,?,?)",
                           (username, password, email, first_name, surname, dob))
            conn.commit()
            flash('Sign up Successful, Please login.')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.')
            return redirect(url_for('signup'))
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if 'username' not in session:
        return redirect(url_for('index'))

    user_info = {
        'username': session['username'],
        'first_name': session['first_name'],
        'surname': session['surname'],
        'dob': session['dob'],
    }

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rolsa_carbon WHERE user_id = ?', (session['user_id'],))
    rolsa_carbon = cursor.fetchall()

    cursor.execute('SELECT * FROM appointments WHERE user_id = ?', (session['user_id'],))
    appointments = cursor.fetchall()
    conn.close()

    return render_template('welcome.html', user_info=user_info, rolsa_carbons=rolsa_carbon, appointments=appointments)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        service_type = request.form['service_type']
        selected_date = request.form['selected_date']
        selected_time = request.form['selected_time']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appointments (user_id, service_type, date, time)
            VALUES (?,?,?,?)
        """, (session['user_id'], service_type, selected_date, selected_time))
        conn.commit()
        conn.close()

        flash('Appointment Successfully Scheduled.')
        return redirect(url_for('view_appointments'))
    return render_template('schedule.html')

@app.route('/view_appointments')
def view_appointments():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM appointments WHERE user_id = ? ORDER BY date, time', 
                  (session['user_id'],))
    appointments = cursor.fetchall()
    conn.close()
    
    return render_template('view_appointments.html', appointments=appointments)

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM appointments WHERE id = ? AND user_id = ?', 
                  (appointment_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Appointment cancelled successfully.')
    return redirect(url_for('view_appointments'))

@app.route('/energy')
def energy():
    return render_template('energy.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/FAQs')
def FAQs():
    return render_template('FAQs.html')

@app.route('/Aboutus')
def Aboutus():
    return render_template('Aboutus.html')

@app.route('/energy_calc')
def energy_calc():
    return render_template('energy_calc.html')

@app.route('/log_carbon', methods=['GET', 'POST'])
def log_carbon():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        date = request.form['date']
        activity_name = request.form['activity_name']
        carbon_output = float(request.form['carbon_output'])

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rolsa_carbon (user_id, date, activity_name, carbon_output) VALUES(?,?,?,?)",
                       (session['user_id'], date, activity_name, carbon_output))
        conn.commit()
        conn.close()
        flash('Activity successfully added.')
        return redirect(url_for('welcome'))
    return render_template('log_carbon.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)