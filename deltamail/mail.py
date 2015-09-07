from jinja2 import Template


class Mail():
    '''
        Mail object - for internal usage
    '''
    def __init__(self, subject, mailingList, body):
        self.subject = subject
        self.mailingList = mailingList
        self.body = body


def MailFactory(subject, mailingList, templateStr, variables):
    '''
        Creates a Mail object
    '''
    subjectTempl = Template(subject)
    subject = subjectTempl.render(**variables)

    bodyTemplate = Template(templateStr)
    body = bodyTemplate.render(**variables)

    return Mail(subject, mailingList, body)
