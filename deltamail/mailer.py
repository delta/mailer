'''Defines the Mailer class that handles the actual sending of mails'''

import smtplib


class Mailer(object):
    '''
    A class that will do the job of sending the mails
    '''

    def __init__(self, host="localhost", port=25, login_id="", password=""):
        '''
        Initialise Mailer with the required SMTP configuration variables.

        Args:
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

        # connect to the server
        server = smtplib.SMTP(self.host, self.port)
        # server.set_debuglevel(1)
        # server.ehlo()
        server.starttls()
        server.login(self.login_id, self.password)

        # send the mail
        server.sendmail(mail.from_id, mail.mailing_list, mail.encode_in_mime())

        # close the connection
        server.quit()
