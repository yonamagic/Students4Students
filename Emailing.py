# from flask import render_template
#
import os
import smtplib
import sys

from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



class Emailing:

    @staticmethod
    def welcome(username='yonamagic'):
        return """\
          <html>
            <head></head>
            <body>
              <p>ברוכים הבאים למשפחת Syeto!, """ + username + """<br>
                 אנחנו רואים שנרשמת לאתר, תתחדש יא איבני!<br>
              </p>
            </body>
          </html>
          """

    @staticmethod
    def forgot_password(username, link):
        return """\
          <html>
            <head></head>
            <body>
              <p>
              שלום, """ + username + """ <br>
              יש להיכנס ללינק המצורף כדי לאפס את סיסמתך. <br>
              """+link+"""
              <br>
              בברכה, <br>
              צוות Syeto.
              </p>
            </body>
          </html>
          """

    @staticmethod
    def render_template(template, **kwargs):
     ''' renders a Jinja template into HTML '''
     # check if template exists
     if not os.path.exists(template):
        print('No template file present: %s' % template)
        sys.exit()# me == my email address

    @staticmethod
    def send_email(addressee, subject, html):
        # addressee == recipient's email address
        me = "syeto2020@gmail.com"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = addressee


        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nHow are addressee?\nHere is the link addressee wanted:\nhttp://www.python.org"
        # html = render_template()
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        # Send the message via local SMTP server.
        mail = smtplib.SMTP('smtp.gmail.com', 587)

        mail.ehlo()

        mail.starttls()

        mail.login('syeto2020@gmail.com', 'Syeto2020Syeto')
        mail.sendmail(me, addressee, msg.as_string())
        mail.quit()

# Emailing.send_email("jhonbenartzi123@gmail.com", "Welcome ya habibi!", Emailing.welcome())