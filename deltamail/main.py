'''
This is the main python file of deltamailer.
It parses the command line arguements and tells
what the campaign factory should do
'''
import argparse
import os
import getpass
import sys

from deltamail.campaign import CampaignFactory
import envelopes


def console_main():
    try:
        work()
    except:             # Catches *all* exceptions. https://wiki.python.org/moin/HandlingExceptions
        e = sys.exc_info()[1]
        print "\nError: " + str(e)
        sys.exit()


def work():
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

    # conn config
    host = args['host']
    port = args['port']
    username = args['username']
    sendermailid = args['sendermailid'] or (username + '@' + host)

    # read the password
    password = getpass.getpass(prompt="Password for %s@%s: " % (username, host))

    # send/preview?
    smart_send = args['smart_send']
    preview_dir = args['preview']

    # Choosing Smart Send or Hard Send
    if smart_send:
        smart_send = os.path.abspath(smart_send)
        campaign_object = CampaignFactory(sendermailid, *smart_send_fun(smart_send))
    else:
        campaign_object = CampaignFactory(sendermailid, *hard_send(args))

    # Choosing Preview or Sending the Mail
    if preview_dir:
        preview_dir = os.path.abspath(preview_dir)
        campaign_object.preview(preview_dir)
    else:
        conn = envelopes.conn.SMTP(host, port, username, password)
        campaign_object.send(conn)


def smart_send_fun(smart_send):
    '''
    This function assumes all files are in the given directory
    and prepares the arguements for CampaignFactory
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

    # For mailinglist.ml
    try:
        with open(receivers):
            pass
    except IOError:
        raise Exception("The file `mailinglist.ml` either doesn't exist or you don't have read access to the file.")

    # For input.mmtmpl
    # if the file doesnt exist or the user doesnt have permission , it exits

    try:
        with open(template):
            pass
    except IOError:
        raise Exception("The file `template.mmtmpl` either doesn't exist or you don't have read access to the file.")

    # For globals.var
    # if the file isnt provided , empty string is sent
    # But if the file is specified and the file cannot be opened,
    # it throws an error

    if os.access(global_var, os.F_OK):
        try:
            with open(global_var):
                pass
        except IOError:
            raise Exception("Please provide read access to `globals.mvar`")
    else:
        # print "global_var isn't specified."
        global_var = ""
    return [subject, receivers, template, global_var]


def hard_send(args):
    '''
    This function gets the path of all files separately
    and prepares the arguements for CampaignFactory
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
        raise Exception("Please specify the subject.")

    # For template
    # Check if template is None
    # or if file exits and user has permissions

    if template is None:
        raise Exception("Template is required.")
    elif not os.access(template, os.F_OK):
        raise Exception("`%s` doesn't exist." % (template,))
    elif not os.access(template, os.R_OK):
        raise Exception("Please provide read access to `%s`." % (template,))

    # For mailinglist
    # there are two options
    # -R if the path to ml file is given
    # -r if the mail list is given directly
    # error raises if both are either present or not present
    # if -r is used , it is sent as a list of emails
    # if -R is used , whether the file exists or
    # the user has permissions

    if not receivers and not mailinglist:
        raise Exception("Exactly one of -r or -R is required.")
    elif not receivers and mailinglist:
        if not os.access(mailinglist, os.F_OK):
            raise Exception("`%s` doesn't exist." % (mailinglist,))
        elif not os.access(mailinglist, os.R_OK):
            raise Exception("Please provide read access to `%s`." % (mailinglist,))
    elif receivers and not mailinglist:
        receivers = [each.strip() for each in receivers.split(',')]
    else:
        raise SystemExit("Either use -r or -R. Don't use both.")

    # For globals.var
    # if the file isnt provided , empty string is sent
    # But if the file is specified and the file cannot be opened,
    # it throws an error

    if global_var:
        if not os.access(global_var, os.F_OK):
            raise Exception("`%s` doesn't exist." % (global_var,))
        elif not os.access(global_var, os.R_OK):
            raise Exception("Please provide read access to `%s`." % (global_var,))
    else:
        global_var = ""
    return [subject, receivers, template, global_var]


if __name__ == "__main__":
    console_main()
