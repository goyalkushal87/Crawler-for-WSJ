
from flask_mail import Mail, Message

import flask
app = flask.Flask("mail")



app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
    MAIL_USERNAME = "enigma.ml.machine@gmail.com",
    MAIL_PASSWORD = "Pass@123"
	)
mail = Mail(app)
msg = Message("Send Mail Tutorial!",
sender="enigma.ml.machine@gmail.com",
recipients=["goyalkushal87@gmail.com"])
msg.body = "Yo!\nHave you heard the good word of Python???"           
mail.send(msg)
 