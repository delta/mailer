'''Contains the Mail class and the MailFactory function

Use the MailFactory function to create a Mail object.
Uses jinja2 templates.
'''
from jinja2 import Template


class Mail(object):
    '''Mail object - for internal usage'''
    def __init__(self, subject, mailing_list, body):
        '''
        Initialize Mail object.

        Args:
            subject (str): Subject of the mail. Cannot be a template.
            mailing_list (list): List of email addresses to whom the
                mail will be sent.
            body (str): The exact body of the mail (Can't be a template).

        Returns:
            None
        '''
        self.subject = subject
        self.mailing_list = mailing_list
        self.body = body


def MailFactory(subject, mailing_list, template_str, variables):
    '''
    Create a Mail object.

    Pass-in templates and get back the Mail objects with templates
    filled-in with the variables given.

    Args:
        subject (str): The subject of the mail. Can be a template.
        mailing_list (list): The list of the email addresses to whom
            the mail will be sent.
        template_str (str): The template of the mail-body.
        variables (dict): The dictionary of the variables used to fill-in
            the body and subject templates.

    Returns:
        Mail: An instance of Mail with values appropriately filled in.
    '''
    subject_templ = Template(subject)
    subject = subject_templ.render(**variables)

    body_template = Template(template_str)
    body = body_template.render(**variables)

    return Mail(subject, mailing_list, body)
