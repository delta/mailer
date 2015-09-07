import smtplib
import email


class Mailer:
    '''
    A class that will do the job of sending the mails
    '''

    # SMTP-Server details
    host = ""
    port = ""
    email = ""
    password = ""

    def __init__(self, host="localhost", port="25", email="", password=""):
        '''
        Accept the host, port, email and password for logging in to the SMTP
        server
        '''
        self.host = host
        self.port = str(port)
        self.email = email
        self.password = password

    def send(self, mail):
        '''
        Sends the mail object.
        '''
        # get the message ready
        msg = email.mime.text.MIMEText(mail.body)
        msg['Subject'] = mail.subject
        msg['From'] = self.email
        msg['To'] = mail.mailingList

        # connect to the server
        server = smtplib.SMTP(self.host + ":" + self.port)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(self.email, self.password)

        # send the mail
        server.sendmail(self.email, [msg['To']], msg.as_string())

        # close the connection
        server.quit()
