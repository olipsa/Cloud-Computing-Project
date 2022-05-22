from firebase_admin import auth, credentials
import firebase_admin
import sendEmail


cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

def sendNewsletter(event, context):
    service = sendEmail.get_service()
    text = 'Dear user,\nWe\'ve got a new collection of memes\n\n\nThanks,\nYour Cloud Computing team'

    for user in auth.list_users().iterate_all():
        gmail_message = sendEmail.create_message('cc.homework.3@gmail.com', user.email, 'Newsletter', text)
        sendEmail.send_message(service, 'me', gmail_message)
        print(user.email)
