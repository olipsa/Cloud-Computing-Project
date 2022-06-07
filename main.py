from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
import stripe
from firebase_admin import auth, credentials

from functions import sendEmail
from label_detect import detect
from reCaptcha import ReCaptcha
from config import *

app = Flask(__name__)
app.config['RECAPTCHA_SITE_KEY'] = RECAPTCHA_SITE_KEY
app.config['RECAPTCHA_SECRET_KEY'] = RECAPTCHA_SECRET_KEY
app.secret_key = FLASK_SECRET
stripe.api_key = STRIPE
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
                session['email'] = email
                return redirect(url_for('get_form_input'))
            except auth.EmailAlreadyExistsError:
                message = 'Email already registered, try logging in.'
            except ValueError:
                message = 'Password must be at least 6 characters long.'
        else:
            message = 'Please fill out the ReCaptcha!'

    return render_template('register.html', logging=response, message=message)


@app.route('/form', methods=['GET', 'POST'])
def get_form_input():
    if request.method == 'POST':
        session['company'] = request.form['company_name']
        session['vibe'] = request.form['meme_vibe']
        session['text'] = request.form['optional_text']
        print(session['text'])
        return make_payment()
    else:
        return render_template('form.html')


@app.route('/analyse', methods=['GET', 'POST'])
def vision():
    message = detect()
    return render_template('analyse.html', message=message)


@app.route("/payment")
def make_payment():
    get_meme()
    return render_template("payment.html")


def get_meme():
    text = session['text']
    # response = requests.get(f"http://40.87.145.211:40404/memes?string='{text}'")
    # print(response.json())
    service = sendEmail.get_service()
    text = "Here is your personalized meme"
    # # print(session['email'])
    gmail_message = sendEmail.create_message('cc.homework.3@gmail.com', session['email'], 'Your personalized meme', text
                                             , 'meme.jpg')
    sendEmail.send_message(service, 'me', gmail_message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088, debug=True)
