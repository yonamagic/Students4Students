import smtplib, ssl
class Mailing:
    @staticmethod
    def send_email(receiver_email = "jhonbenartzi123@gmail.com", subject="Welcome bro", content="Welcome to Syeto family :)"):

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "syeto2020@gmail.com"  # Enter your address
        # receiver_email = "jhonbenartzi123@gmail.com"  # Enter receiver address
        password = "Syeto2020Syeto"
        # message = """\
        # """+subject+"""
        #
        # """+content+""""""
        message = """\
        Syeto Admins\
        Subject: Welcome!
        Welcome to the Syeto family!"""
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(from_addr=sender_email, to_addrs=receiver_email, msg=message)


Mailing.send_email()