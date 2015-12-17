'''Defines the Campaign-* classes and the CampaignFactory function

This module defines the following classes:
    Campaign (Abstract class)
    BulkMailCampaign
    TransactionMailCampaign

It also defines the CampaignFactory method used to create the Campaign objects
easily.

TODO(thakkarparth007): Handle previewing in a better manner.
'''

from abc import ABCMeta, abstractmethod
import os

from deltamail.mail import MailFactory

# Upper limit on preview-file name length
MAX_PREVIEW_FILE_LEN = 70


class Campaign(object):
    '''
    Abstract class. Used to handle a bunch of mails to be sent.

    *-Campaign objects inherit from Campaign.
    *-Campaign objects just fill the _mails list, and
    The sending and previewing is done here itself.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def _create_mail_objects(self, from_addr, subject, mailing_list, template_str, global_vars):
        '''
        Populate the self._mails list

        Called by __init__
        This is the only method that is to be implemented by the *-Campaign
        classes. It fills the _mails list and the other operations on
        Campaign classes are all the same, and hence are defined in the
        Campaign class itself.
        '''
        pass

    def __init__(self, from_addr, subject, mailing_list, template_str, global_vars):
        '''
        Initialise the Campaign class.

        Calls the (abstract) _create_mail_objects method and populates
        the the self._mails list.

        Args:
            from_addr (str): The "From" address for the mail being sent.
            subject (str): The subject of the mail (can be a template).
            mailing_list (list): The list of of email-ids to whom the
                mails are to be sent. Type varies based on the *-Campaign
                class being used.
            template_str (str): The template string for the mail.
            global_vars (dict): The dictionary of global variables to fill
                up the template.

        Returns:
            None
        '''
        # will store the mail objects to be sent
        self._mails = []
        self._create_mail_objects(from_addr, subject, mailing_list, template_str, global_vars)

    def send(self, smtp_conn):
        '''
        Send the mails.

        Uses a envelopes.conn.SMTP instance to send the mails. Doesn't
        do anything other than to call the smtp_conn.send() method for each
        of the envelopes.Envelope objects in the Campaign. Just a
        helper/syntactic sugar.

        Args:
            smtp_conn (envelopes.conn.SMTP): Used to do the actual sending

        Returns:
            None
        '''
        for mail in self._mails:
            smtp_conn.send(mail)

    def preview(self, location="", preview_count=-1):
        '''
        Generate the html files to be sent in the `location` folder.

        Currently, the mails are being created as html files, and each
        file is stored as "SUBJECT-[to/cc/bcc]-RECEIVER_ID.html", and the
        filename is limited to MAX_PREVIEW_FILE_LEN number of characters
        (excluding the ".html" extension).

        Args:
            location (Optional[str]): Location to dump preview mail files.
                Defaults to CURRENT_WORKING_DIR/email-preview.
            preview_count (Optional[int]): Number of preview mails to
                generate. Set that to -1 if preview of all mails must
                be generated. Defaults to -1.

        Raises:
            Exception: If the location is given and isn't a folder,
                or, if the location isn't given and "email-preview"
                folder already exists.
        '''

        # TODO(thakkarparth007): Raise better exceptions.
        if location is "":
            location = os.path.join(os.getcwd(), "email-preview", "")
            os.mkdir(location)

        if os.path.isdir(location) is False:
            raise Exception(
                "Location given for preview ({0}) doesn't exist."
                .format(os.path.abspath(location))
            )

        if preview_count == -1:
            preview_count = len(self._mails)

        for mail in self._mails:
            receivers = [('to', addr) for addr in mail.to_addr]
            receivers += [('cc', addr) for addr in mail.cc_addr]
            receivers += [('bcc', addr) for addr in mail.bcc_addr]

            for receiver in receivers:
                if preview_count <= 0:
                    break
                preview_count -= 1

                filename = mail._subject + "-" + receiver[0] + ":" + receiver[1]
                filename = filename[:MAX_PREVIEW_FILE_LEN] + ".html"

                # replace \ and / with - in case the subject contains
                # those characters
                filename.replace(r"/", "-")
                filename.replace("\\", "-")

                # finally, write the body
                fpreview = open(os.path.join(location, filename), "w")
                fpreview.write(mail._parts[0][1])
                fpreview.close()

            if preview_count <= 0:
                break

    def preview_one_in_browser(self):
        '''
        Open the first mail in browser

        The method hasn't been implemented yet.

        Parameters:
            none

        Returns:
            None
        '''

        raise NotImplementedError("Yet to be implemented.")
        if len(self._mails) is 0:
            raise "No mails to be sent!"

        # fpreview = open()


class BulkMailCampaign(Campaign):
    '''
        Same mail sent to each person. (Allows usage of global variables)
    '''
    def _create_mail_objects(self, from_addr, subject, mailing_list, template_str, global_vars):
        '''
        Populate the _mails list. (Private method)

        Called by __init__
        This is the only method that is to be implemented by the *-Campaign
        classes. It fills the _mails list and the other operations on
        Campaign classes are all the same, and hence are defined in the
        Campaign class itself.

        Args:
            from_addr (str): The "From" address for the mail being sent.
            subject (str): The subject of the mail. Can be a template with
                only global variables
            mailing_list (list): The list of the email ids to whom the mails
                are to be sent.
            template_str (str): The template for the body of the mail. Can
                contain only global variables.
            global_vars (dict): The dictionary of global variables.

        Returns:
            None
        '''
        self._mails = [MailFactory(from_addr, subject, mailing_list,
                                   template_str, global_vars)]

    def __init__(self, from_addr, subject, mailing_list, template_str, global_vars):
        super(BulkMailCampaign, self).__init__(
            from_addr, subject, mailing_list, template_str, global_vars
        )

    def preview(self, location=""):
        '''
        Generate the html file to be sent in the `location` folder.

        Calls the Campaign.preview method with preview_count set to 1.
        The reason to do this is that for bulk mails, the same mail
        is sent. There is no point in creating separate preview files.
        Args:
            location (Optional[str]): Location to dump preview mail files.
                Defaults to CURRENT_WORKING_DIR/email-preview.

        Raises:
            Exception: If the location is given and isn't a folder,
                or, if the location isn't given and "email-preview"
                folder already exists.
        '''
        super(BulkMailCampaign, self).preview(location, 1)


class TransactionMailCampaign(Campaign):
    '''Personalised mails sent to each person.'''
    def _create_mail_objects(self, from_addr, subject, mailing_list, template_str, global_vars):
        '''
        Populate the _mails list. (Private method)

        Called by __init__
        This is the only method that is to be implemented by the *-Campaign
        classes. It fills the _mails list and the other operations on
        Campaign classes are all the same, and hence are defined in the
        Campaign class itself.

        The personal variables override the global variables of the same name,
        if any.

        Args:
            from_addr (str): The "From" address for the mail being sent.
            subject (str): The subject of the mail. Can be a template with
                global or personal variables.
            mailing_list (list): The list of the {"email","variables"} dicts
                to whom the mails are to be sent.
            template_str (str): The template for the body of the mail. Can
                contain global or personal variables.
            global_vars (dict): The dictionary of global variables.

        Returns:
            None
        '''

        self._mails = []

        for receiver in mailing_list:
            # copy the global variables in a new dict.
            # Override with personal variables if needed
            variables = dict(global_vars)

            for key in receiver["variables"]:
                variables[key] = receiver["variables"][key]

            self._mails.append(
                MailFactory(from_addr, subject, [receiver["email"]], template_str, variables)
            )

    def __init__(self, from_addr, subject, mailing_list, template_str, global_vars):
        super(TransactionMailCampaign, self).__init__(
            from_addr, subject, mailing_list, template_str, global_vars
        )


def CampaignFactory(from_addr, subject, mailing_list,
                    template_file, global_vars_file=""):
    '''
    Factory to construct BulkMailCampaign or TransactionMailCampaign object

    Creates the appropriate Campaign object based on the input parameters.

    Args:
        from_addr (str): The "From" address for the mail being sent.
        subject (str): The subject string for the mails being sent (can be template).
        mailing_list (list/str): A list of strings or a string (filename).
            If it's a list of strings, the strings are taken as email-ids.
            Otherwise, if a string is passed, it is taken as the filename of
            the mailing-list file (.ml file). In latter case, TransactionMailCampaign
            is returned. In former case, BulkMailCampaign is returned.
        template_file (str): The filename that contains the template that is to
            be used to send the mails.
        global_vars_file (Optional[str]): The filename that contains the global variables.

    Returns:
        Campaign: BulkMailCampaign or TransactionMailCampaign based on whether
            mailing_list is a list of email-ids, or is the filename of the .ml
            file.

    Raises:
        Exception: If template file doesn't exist.
            If global_vars_file is given and the file doesn't exist.
            If the mailing-list file doesn't exist (if mailing_list is filename).
            If first field of mailing list file isn't "email"

    TODO (thakkarparth007): Use better exception-names.
    '''

    # The following variables are used to initialise the appropriate class
    #
    #   template_str : The template string read from the template file
    #   global_vars  : The dictionary containing the global variables
    #   mailing_list : The list of dictionaries that contains the
    #                 mailing list

    # read the template file
    if os.path.exists(template_file) is False:
        raise Exception("Template list file ({0}) doesn't exist"
                        .format(os.path.abspath(template_file)))

    ftmpl = open(template_file, "r")
    template_str = ftmpl.read()
    ftmpl.close()

    # read the global vars file
    if global_vars_file != "" and os.path.exists(global_vars_file) is False:
        raise Exception("Global variables file ({0}) doesn't exist"
                        .format(os.path.abspath(global_vars_file)))

    contents = ""
    if global_vars_file != "":
        fglbl = open(global_vars_file, "r")
        contents = fglbl.read()
        fglbl.close()

    global_vars = dict([
        (line.split("=")[0].strip(), line.split("=")[1])
        for line in contents.splitlines() if line.rstrip() != ""
    ])

    # read the mailing_list if it is a string
    # in any case, convert it to a list of
    # dictionaries of form:
    #   { "email": "...", "variables": "" }
    if isinstance(mailing_list, str):
        mailing_list_file = mailing_list

        if os.path.exists(mailing_list_file) is False:
            raise Exception("Mailing list file ({0}) doesn't exist"
                            .format(os.path.abspath(mailing_list_file)))

        fml = open(mailing_list_file, "r")
        contents = fml.read().splitlines()
        fml.close()

        headers, rows = contents[0].split("\t"), contents[1:]

        if headers[0] != "email":
            raise Exception("First field of mailing list file is "
                            "required to be `email`")

        mailing_list = []
        for row in rows:
            if row.strip() == "":
                continue
            row = row.split("\t")
            if len(row) != len(headers):
                raise Exception("%s: Mismatch in number of columns." % (mailing_list_file,))
            mailing_list.append({
                "email": row[0],
                "variables": dict([
                    (headers[i], row[i])
                    for i in range(1, len(headers))
                ])
            })

        mail_constructor = TransactionMailCampaign

    else:
        mail_constructor = BulkMailCampaign

    return mail_constructor(from_addr, subject, mailing_list, template_str, global_vars)
