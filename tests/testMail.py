from deltamail import mail


class TestMail:
    def testMailFactory(self):
        m = mail.MailFactory("Greetings from {{company}}", ['job@bob.com'],
                             "Hello {{name}},\n{{msg}}",
                             {"company": "Festember", "name": "Job",
                              "msg": "Sorry, you are rejected. KBye."})

        assert(m.subject == "Greetings from Festember")
        assert(m.body == "Hello Job,\nSorry, you are rejected. KBye.")
