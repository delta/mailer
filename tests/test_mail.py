"""Code to test the deltmail.mail module"""
import sys
from os import path

try:
    from unittest.mock import patch
except:
    from mock import patch

from deltamail import envelopes_mod as envelopes
from deltamail import mail


class TestMailFactory(object):
    """Class to test the MailFactory function"""

    @patch('deltamail.mail.formatdate', autospec=True)
    def test_MailFactory_vanilla(self, mock_formatedate):
        """Test the MailFactory function without attachments"""

        env_patcher = patch('deltamail.mail.envelopes', autospec=True)
        try:
            mock_env = env_patcher.start()

            from_addr = "sender@example.com"
            subject = "Greetings from {{company}}"
            mailing_list = ['job@bob.com', 'fob@bob.com']
            template_str = "Hello {{name}},\n{{msg}}"
            variables = {
                "company": "Festember", "name": "Job",
                "msg": "Have a good day!"
            }

            subject_evaled = u"Greetings from Festember"
            body_evaled = u"Hello Job,\nHave a good day!"
            date = "123456789"

            mock_formatedate.return_value = date

            mf = mail.MailFactory(from_addr, subject, mailing_list, template_str, variables)

            mock_formatedate.assert_called_once_with(localtime=True)
            mock_env.Envelope.assert_called_once_with(from_addr=from_addr,
                                                      subject=subject_evaled,
                                                      to_addr=mailing_list,
                                                      html_body=body_evaled,
                                                      headers={"Date": date})

            env_patcher.stop()

            mf = mail.MailFactory(from_addr, subject, mailing_list, template_str, variables)

            # Ideally we should be comparing mf with the Envelope object directly
            # created using the Envelope constructor. However since that comparison
            # is rather complicated, we're going with a simpler sanity check.
            # We'll just check if the return value of MailFactory is an
            # instance of the Envelope class. This should be fine in most cases
            # since we're already checking if the Envelope class is being
            # called with appropriate arguments above. Not foolproof, but
            # good enough.
            assert isinstance(mf, envelopes.Envelope)
        except:
            env_patcher.stop()
            raise sys.exc_info()

    @patch('deltamail.mail.formatdate', autospec=True)
    def test_MailFactory_attachments(self, mock_formatedate):
        """Test the MailFactory function with attachments"""

        env_patcher = patch('deltamail.mail.envelopes', autospec=True)
        try:
            mock_env = env_patcher.start()

            from_addr = "sender@example.com"
            subject = "Greetings from {{company}}"
            mailing_list = ['job@bob.com', 'fob@bob.com']
            template_str = "Hello {{name}},\n{{msg}}"
            attch1 = "~/emails/festember/reg.pdf"
            attch2 = "/home/pragyan.pdf"
            attch3 = "nittfest.pdf"
            variables = {
                "company": "Festember", "name": "Job",
                "msg": "Have a good day!",
                "$attachments": attch1 + ";" + attch2 + ";" + attch3
            }

            subject_evaled = u"Greetings from Festember"
            body_evaled = u"Hello Job,\nHave a good day!"
            date = "123456789"

            mock_formatedate.return_value = date

            mf = mail.MailFactory(from_addr, subject, mailing_list, template_str, variables)

            mock_formatedate.assert_called_once_with(localtime=True)
            mock_env.Envelope.assert_called_once_with(from_addr=from_addr,
                                                      subject=subject_evaled,
                                                      to_addr=mailing_list,
                                                      html_body=body_evaled,
                                                      headers={"Date": date})

            mf.add_attachment.assert_any_call(path.abspath(path.expanduser(attch1)))
            mf.add_attachment.assert_any_call(path.abspath(path.expanduser(attch2)))
            mf.add_attachment.assert_any_call(path.abspath(path.expanduser(attch3)))
            assert mf.add_attachment.call_count == 3

            env_patcher.stop()

            mf = mail.MailFactory(from_addr, subject, mailing_list, template_str, variables)

            # Ideally we should be comparing mf with the Envelope object directly
            # created using the Envelope constructor. However since that comparison
            # is rather complicated, we're going with a simpler sanity check.
            # We'll just check if the return value of MailFactory is an
            # instance of the Envelope class. This should be fine in most cases
            # since we're already checking if the Envelope class is being
            # called with appropriate arguments above. Not foolproof, but
            # good enough.
            assert isinstance(mf, envelopes.Envelope)

        except:
            env_patcher.stop()
            raise sys.exc_info()
