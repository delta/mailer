'''Defines the Mailer class that handles the actual sending of mails'''

import smtplib
from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


class Mailer(object):
    '''
    A class that will do the job of sending the mails
    '''

    def __init__(self, sender_email, host="localhost", port=25, login_id="", password=""):
        '''
        Initialise Mailer with the required SMTP configuration variables.

        Args:
            sender_email (str): The "from" address used to stamp on the emails being sent.
            host (str): The SMTP host. Defaults to "localhost".
            port (int): The open port of the SMTP server. Defaults to 25.
            login_id (str): The username of the SMTP server. Defaults to "".
            password (str): The password of the given username. Defaults to "".

        Returns:
            None
        '''
        self.host = host
        self.port = port
        self.login_id = login_id
        self.password = password
        self.sender_email = sender_email

    def send(self, mail):
        '''
        Send the mail object.

        Sends html emails currently. The emails being sent are currently all
        html mails, with no plain-text version of the message. This must be
        rectified. No attachments are supported currently.

        Args:
            mail (Mail): The mail object to be sent.

        Returns:
            None
        '''
        # raise NotImplementedError()

        # get the message ready
        msg = MIMEText(mail.body, 'html')
        msg['Subject'] = mail.subject
        msg['From'] = self.sender_email
        msg['To'] = ",".join(mail.mailing_list)
        msg["Date"] = formatdate(localtime=True)

        # connect to the server
        server = smtplib.SMTP(self.host, self.port)
        # server.set_debuglevel(1)
        # server.ehlo()
        server.starttls()
        server.login(self.login_id, self.password)

        # send the mail
        server.sendmail(self.sender_email, msg['To'], msg.as_string())

        # close the connection
        server.quit()
