from jinja2 import Template


class Mail():
    '''
        Mail object - for internal usage
    '''
    def __init__(self, subject, mailingList, body):
        '''
             Parameters:
                name        type        comments
                ---------------------------------------
                subject     str         Subject of the mail.
                                        Cannot be a template
                mailingList list        List of email addresses to whom the
                                        mail will be sent
                body        str         The exact body of the mail
        '''
        self.subject = subject
        self.mailingList = mailingList
        self.body = body


def MailFactory(subject, mailingList, templateStr, variables):
    '''
        Creates a Mail object

        Parameters:
            name        type        comments
            ---------------------------------------
            subject     str         The subject of the mail.
                                    Can be a template.
            mailingList list        The list of the email addresses to whom
                                    the mail will be sent
            templateStr str         The template of the body
            variables   dict        The values of the variables in the template
    '''
    subjectTempl = Template(subject)
    subject = subjectTempl.render(**variables)

    bodyTemplate = Template(templateStr)
    body = bodyTemplate.render(**variables)

    return Mail(subject, mailingList, body)
