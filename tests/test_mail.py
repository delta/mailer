"""Code to test the deltmail.mail module"""

from deltamail import mail


class TestMailFactory(object):
    """Class to test the MailFactory function"""

    def test_MailFactory(self):
        """Test the MailFactory function"""

        mf = mail.MailFactory("Greetings from {{company}}", ['job@bob.com'],
                              "Hello {{name}},\n{{msg}}",
                              {"company": "Festember", "name": "Job",
                               "msg": "Sorry, you are rejected. KBye."})

        assert mf.subject == "Greetings from Festember"
        assert mf.body == "Hello Job,\nSorry, you are rejected. KBye."
