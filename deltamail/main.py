'''
This is the main python file of deltamailer.
It parses the command line arguements and tells
what the campaign factory should do
'''
import argparse
import os
import getpass

from deltamail.campaign import CampaignFactory
from deltamail.mailer import Mailer


def console_main():
    '''
    The main function of the program.
    Parses the command line arguements.
    Makes the choice between Hardsend /SmartSend
    Makes the choice between preview/send.
    '''

    description = '''
    A command line mailer application.

    There are two ways in which you can send mails. One way
    is to pass in individual parameters, and the other way
    is called "Smart Send".

    To send any mail (or mail campaign) the following parameters are required:
        - Subject of the mail campaign
        - Receivers of the mail campaign (A list of email ids who'll receive your mail)
            OR
          A mailing list file - a tab separated file with the first column named
          'email' and the all other columns are the variables you'd like in 
          the mail templates
        - Mail Template - A jinja compatible template to be used for the mail body
        - Global variables (options) - A list of variables that will be substituted
          in each of the mail body.

    Besides these, the username, password, port and host of the SMTP server that
    handles the actual sending of emails are required too. Optionally, a sendermailid
    is accepted, which is the "From" address in the mails being sent.

    ... more help coming soon ...
    (Till then, read the README.md file)
    '''
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    # This is required only in non-smart-send mode.
    parser.add_argument('-s', '--subject',     help='Subject of email')

    # The following two are required only in non-smart-send mode
    parser.add_argument('-r', '--receivers',   help='Receivers List in qoutes separated by commas')
    parser.add_argument('-R', '--mailinglist', help="path to the .ml file")

    # This file is required only in non-smart-send mode
    parser.add_argument('-t', '--template',    help="template file")

    parser.add_argument('-g', '--global_var',  help="global variable file")

    # The username is required. The sender-email, if not specified, will be taken
    # as username@smtp_host
    parser.add_argument('-u', '--username',    help="Username for SMTP", required=True)
    parser.add_argument('-p', '--port',        help="Port to be used", type=int, default=25)
    parser.add_argument('-m', '--sendermailid',help="The sender email")
    parser.add_argument('-o', '--host',        help="SMTP host IP or name", default="localhost")

    parser.add_argument('-pw', '--preview',    help="to preview the mail(**the mail wont be sent**)")
    parser.add_argument('-sm', '--smart_send', help="path for smart send")
    args = vars(parser.parse_args())


    # Checking if Username ,Port and Host are Provided

    # if not args["host"]:
    #    host = ""
    #    print "host isnt specified. Using localhost\n"

    # if not args["port"]:
    #    port = ""
    #    print "port isnt specified. Using 25\n"

    # if not args["username"]:
    #    raise Exception("Specify Username")
    # else:
    #    username = args["username"]

    # mailer config
    host = args['host']
    port = args['port']
    username = args['username']
    sendermailid = args['sendermailid'] or (username + '@' + host)

    # read the password
    print "Enter the password for %s@%s: " % (username, host)
    password = getpass.getpass()

    # send/preview?
    smart_send = args['smart_send']
    preview_dir = args['preview']

    # Choosing Smart Send or Hard Send
    if smart_send:
        campaign_object = CampaignFactory(*smart_send_fun(smart_send))
    else:
        campaign_object = CampaignFactory(*hard_send(args))

    # Choosing Preview or Sending the Mail
    if preview_dir:
        campaign_object.preview(preview_dir)
    else:
        mailer = Mailer(sendermailid, host, port, username, password)
        campaign_object.send(mailer)


def smart_send_fun(smart_send):
    '''
    This function assumes all files are the given directory
    and process them to mailer
    '''
    subject = os.path.join(smart_send, "subject.txt")
    receivers = os.path.join(smart_send, "mailinglist.ml")
    template = os.path.join(smart_send, "template.mmtmpl")
    global_var = os.path.join(smart_send, "globals.mvar")

    # For Subject
    # if there is no subject.txt in the provided directory
    # the basename is assumed as subject
    # if the file exists , the content of subject.txt is
    # copied to the var subject
    if not os.path.isfile(subject):
        subject = os.path.basename(smart_send)
    else:
        sub_file = open(subject, 'r')
        subject = sub_file.read()
        sub_file.close()


    # For receivers.ml
    # if the file doesnt exist or the user doesnt have permission , it exits

    try:
        with open(receivers):
            pass
    except IOError:
        raise SystemExit("The file mailinglist.ml either doesnt exist or \
            the user doesnt have permission to access the file\n")

    # For input.mmtmpl
    # if the file doesnt exist or the user doesnt have permission , it exits

    try:
        with open(template):
            pass
    except IOError:
        raise SystemExit("The file template.mmtmpl either doesnt exist or \
            the user doesnt have permission to access the file\n")

    # For globals.var
    # if the file isnt provided , empty string is sent
    # But if the file is specified and the file cannot be opened,
    # it throws an error

    if os.access(global_var, os.F_OK):
        try:
            with open(global_var):
                pass
        except IOError:
            print "The file globals.var doesnt have permission \
            to access the file by the user\n"
    else:
        # print "global_var isn't specified."
        global_var = ""
    return [subject, receivers, template, global_var]


def hard_send(args):
    '''
    This function gets the path of all
    files separately and sends them to mailer.py
    '''
    subject = args['subject']
    receivers = args['receivers']
    global_var = args['global_var']
    template = args['template']
    mailinglist = args['mailinglist']

    # For Subject
    # Check if subject is specified
    # **Only subject is accepted as a string
    # and not a file**

    if subject is None:
        raise Exception("Please Specify the Subject.")

    # For template
    # Check if template is None
    # or if file exits and user has permissions

    if template is None:
        raise Exception("Template Missing")
    elif not os.access(template, os.F_OK):
        raise Exception("Provide a Valid or Existing File")
    elif not os.access(template, os.R_OK):
        raise Exception("Provide Read Access to template.mmtmpl")


    # For mailinglist
    # there are two options
    # -R if the path to ml file is given
    # -r if the mail list is given directly
    # error raises if both are either present or not present
    # if -r is used , it is sent as a list of emails
    # if -R is used , whether the file exists or
    # the user has permissions

    if not receivers and not mailinglist:
        raise Exception("mailingList Missing")
    elif not receivers and mailinglist:
        if not os.access(receivers, os.F_OK):
            raise Exception("Provide a Valid File name")
        elif not os.access(receivers, os.R_OK):
            raise Exception("Provide Read Access to .ml file")
    elif receivers and not mailinglist:
        receivers = [each.strip() for each in receivers.split(',')]
    else:
        raise SystemExit("Either use -r or -R. Don't use both")


    # For globals.var
    # if the file isnt provided , empty string is sent
    # But if the file is specified and the file cannot be opened,
    # it throws an error

    if global_var:
        if not os.access(global_var, os.F_OK):
            raise Exception("Provide a Valid File name")
        elif not os.access(global_var, os.R_OK):
            raise Exception("Provice Read Access to the file")
    else:
        global_var = ""
    return [subject, receivers, template, global_var]


if __name__ == "__main__":
    console_main()
