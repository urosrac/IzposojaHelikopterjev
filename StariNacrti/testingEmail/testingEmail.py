from flask import Flask
from flask_mail import Mail, Message
app = Flask(__name__)
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'ime.priimek@gmail.com',
    "MAIL_PASSWORD": ''
}
app.config.update(mail_settings)
mail = Mail(app)
@app.route("/")
def index():
    msg = Message(subject="Hello",
                  sender=app.config.get("MAIL_USERNAME"),
                  recipients=["ime.priimek@gmail.com"],
                  body="This is a test email I sent with Gmail and Python!")
    mail.send(msg)
    return "Message was send."
if __name__ == '__main__':
    app.run()