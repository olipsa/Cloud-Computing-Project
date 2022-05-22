from flask import Flask, render_template, request, redirect, jsonify
import firebase_admin
from firebase_admin import auth, credentials, firestore
# from label_detect import detect
from reCaptcha import ReCaptcha

from config import *

app = Flask(__name__)
app.config['RECAPTCHA_SITE_KEY'] = RECAPTCHA_SITE_KEY
app.config['RECAPTCHA_SECRET_KEY'] = RECAPTCHA_SECRET_KEY
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

recaptcha = ReCaptcha(app)


@app.route('/')
def hello():
    return redirect('register')


@app.route('/memes')
def memes():
    return 'Here is your meme'


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = str()
    response = str()
    if request.method == 'POST':
        if recaptcha.verify():
            message = 'Thanks for filling out the form! Check your email in order to verify your account.'
            password = request.form['password']
            email = request.form['email']
            try:
                auth.create_user(email=email, password=password)
            except auth.EmailAlreadyExistsError:
                message = 'Email already registered, try logging in.'
            except ValueError:
                message = 'Password must be at least 6 characters long.'
        else:
            message = 'Please fill out the ReCaptcha!'

    return render_template('register.html', logging=response, message=message)


@app.route('/form', methods=['GET', 'POST'])
def get_input():
    return render_template('form.html')

@app.route('/analyse', methods=['GET', 'POST'])
def vision():
    message = detect()
    return render_template('analyse.html',message=message)

@app.route("/payment")
def payment():
    return render_template("payment.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088, debug=True)
