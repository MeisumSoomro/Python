from email.message import EmailMessage
from ep2 import password # variable declared in ep2 that holds password, 

import ssl
import smtplib                         #

email_sender = 'meisumsoomro@gmail.com'
email_password = password

email_reciever = 'hawoboc662@chotunai.com'

subject = "This is an announcement"
body = """                  # three brackets begin / end
    This is the message
"""

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_reciever
em['subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_reciever, em.as_string())