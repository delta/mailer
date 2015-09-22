import smtplib
from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from email.Utils import formatdate


class Mailer:
    '''
    A class that will do the job of sending the mails
    '''

    # SMTP-Server details
    host = ""
    port = ""
    email = ""
    password = ""

    def __init__(self, host="localhost", port="25",
                 loginId="", password="", senderEmail=""):
        '''
        Accept the host, port, email and password for logging in to the SMTP
        server
        '''
        self.host = host
        self.port = int(port)
        self.loginId = loginId
        self.password = password
        self.senderEmail = senderEmail

    def send(self, mail):
        '''
        Sends the mail object.
        '''
        # raise NotImplementedError()

        # get the message ready
        msg = MIMEText(mail.body, 'html')
        msg['Subject'] = mail.subject
        msg['From'] = self.senderEmail
        msg['To'] = ",".join(mail.mailingList)
        msg["Date"] = formatdate(localtime=True)

        # connect to the server
        server = smtplib.SMTP(self.host, self.port)
        # server.set_debuglevel(1)
        # server.ehlo()
        server.starttls()
        server.login(self.loginId, self.password)

        # send the mail
        server.sendmail(self.email, msg['To'], msg.as_string())

        # close the connection
        server.quit()
