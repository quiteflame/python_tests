from flask import Flask, session, request, redirect, url_for
from flask.templating import render_template

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    if not session.get("email"):
        return redirect(url_for('login'))
    return render_template('index.html', name=session.get("email"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['email'] = request.form['email']
        return redirect(url_for('index'))
    return render_template(
        "credentials.html", 
        title="Please Sign In",
        primary_title="Sign In", 
        primary_action=url_for('login'),
        secondary_title="Sign Up", 
        secondary_action=url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['email'] = request.form['email']
        return redirect(url_for('index'))
    elif session.get('email'):
        return redirect(url_for('index'))

    return render_template(
        "credentials.html", 
        title="Please Sign Up",
        primary_title="Sign Up", 
        primary_action=url_for('register'),
        secondary_title="Sign In", 
        secondary_action=url_for('login'))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()