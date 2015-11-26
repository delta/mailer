'''Contains the Mail class and the MailFactory function

Use the MailFactory function to create a Mail object.
Uses jinja2 templates.
'''
import os.path as path
from email.utils import formatdate

from deltamail import envelopes
from jinja2 import Template


def MailFactory(from_id, subject, mailing_list, template_str, variables):
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
            the body and subject templates and to attach files.

    Returns:
        Mail: An instance of Mail with values appropriately filled in.
    '''

    if '$attachments' in variables:
        attachments = variables['$attachments'].split(";")
        variables.pop('$attachments')
    else:
        attachments = []

    subject_templ = Template(subject)
    subject = subject_templ.render(**variables)

    body_template = Template(template_str)
    body = body_template.render(**variables)

    envl = envelopes.Envelope(from_addr=from_id, subject=subject,
                              to_addr=mailing_list, html_body=body,
                              headers={"Date": formatdate(localtime=True)})

    for attch in attachments:
        envl.add_attachment(path.abspath(path.expanduser(attch)))

    return envl
