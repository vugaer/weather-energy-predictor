from flask import Flask, render_template, request, redirect, url_for, flash, session
import mixed  # Assuming mixed.py is accessible and in the same directory
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Login credentials
USERNAME = 'demo'
PASSWORD = '12345'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Either username or password is incorrect.")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    current_values, tomorrow_values, current_sum, tomorrow_sum = [], [], 0, 0

    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        
        current_values = mixed.calculate_power_values(period='current')
        tomorrow_values = mixed.calculate_power_values(period='tomorrow')
        current_sum = sum(current_values)
        tomorrow_sum = sum(tomorrow_values)

    return render_template('dashboard.html', current_values=current_values, tomorrow_values=tomorrow_values,
                           current_sum=current_sum, tomorrow_sum=tomorrow_sum)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
