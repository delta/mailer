"""Code to test the deltmail.mail module"""

from deltamail import mail


class TestMailFactory(object):
    """Class to test the MailFactory function"""

    def test_MailFactory(self):
        """Test the MailFactory function"""

        mf = mail.MailFactory(
                "sender@example.com",
                "Greetings from {{company}}", ['job@bob.com'],
                "Hello {{name}},\n{{msg}}",
                {
                    "company": "Festember", "name": "Job",
                    "msg": "Sorry, you are rejected. KBye."
                }
        )

        assert mf.from_addr == "sender@example.com"
        assert mf._subject == "Greetings from Festember"
        assert mf._parts[0][1] == "Hello Job,\nSorry, you are rejected. KBye."
