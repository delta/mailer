from abc import ABCMeta, abstractmethod
import os

from mail import MailFactory

# Upper limit on preview-file name length
MAX_PREVIEW_FILE_LEN = 30


class Campaign():
    '''
        *-Campaign objects inherit from Campaign.
        *-Campaign objects just fill the _mails list, and
        the sending and previewing is done here itself.
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def _createMailObjects(self, subject, mailingList,
                           templateStr, globalVars):
        '''
            Populate the self._mails list
        '''
        pass

    def __init__(self, subject, mailingList, templateStr, globalVars):
        # will store the mail objects to be sent
        self._mails = []
        self._createMailObjects(subject, mailingList, templateStr, globalVars)

    def send(self, mailer):
        '''
            Send the mails.

            Parameters:
                name        type        comments
                ---------------------------------------
                mailer      Mailer      Will be used to send the mails
        '''
        for m in self._mails:
            mailer.send(m)

    def preview(self, location=""):
        '''
            Generate the html files to be sent in the `location` folder.

            Parameters:
                name        type        comments
                ---------------------------------------
                location    str         The folder where the preview mails
                                        are to be dumped.
                                        Defaults to cwd/email-preview/
        '''

        if location is "":
            location = os.path.join(os.getcwd(), "email-preview", "")
            os.mkdir(location)

        if os.path.isdir(location) is False:
            raise Exception(
                "Location given for preview ({0}) doesn't exist."
                .format(os.path.abspath(location))
            )

        for mail in self._mails:
            for receiver in mail.mailingList:
                filename = mail.subject + "-" + receiver
                filename = filename[:MAX_PREVIEW_FILE_LEN]

                # replace \ and / with - in case the subject contains
                # those characters
                filename.replace("\/", "-")
                filename.replace("\\", "-")

                # finally, write the body
                fpreview = open(os.path.join(location, filename), "w")
                fpreview.write(mail.body)
                fpreview.close()

    def previewOneInBrowser(self):
        '''
            Open the first mail in browser

            Parameters:
                none
        '''

        raise NotImplementedError("Yet to be implemented.")
        if len(self._mails) is 0:
            raise("No mails to be sent!")

        # fpreview = open()


class BulkMailCampaign(Campaign):
    '''
        Same mail sent to each person. (Allows usage of global variables)
    '''
    def _createMailObjects(self, subject, mailingList,
                           templateStr, globalVars):
        '''
            Private method. Called by __init__
            Populate the self._mails list

            Parameters:
                name        type        comments
                ---------------------------------------
                subject     str         The subject of the mail. Can be a
                                        template with only global variables
                mailingList list        The list of the email ids to whom
                                        the mails are to be sent
                templateStr str         The template for the body of the
                                        mail. Can contain only global variables
                globalVars  dict       Dictionary of global variables
        '''

        self._mails = [
            MailFactory(subject, mailingList, templateStr, globalVars)
        ]

    def __init__(self, subject, mailingList, templateStr, globalVars):
        Campaign.__init__(self, subject, mailingList, templateStr, globalVars)


class TransactionMailCampaign(Campaign):
    '''
        Personalised mails sent to each person.
    '''
    def _createMailObjects(self, subject, mailingList,
                           templateStr, globalVars):
        '''
            Private method. Called by __init__
            Populate the self._mails list

            Parameters:
                name        type        comments
                ---------------------------------------
                subject     str         The subject of the mail. Can be a
                                        template with only global variables
                mailingList list        The list of {"email","variables"} dicts
                                        to whom the mails are to be sent
                templateStr str         The template for the body of the
                                        mail. Can contain only global variables
                globalVars  dict        Dictionary of global variables
        '''

        self._mails = []

        for receiver in mailingList:
            variables = globalVars
            # add personal variables. Override global variables if needed
            for key in receiver["variables"]:
                variables[key] = receiver["variables"][key]

            self._mails.append(
                MailFactory(subject, [receiver["email"]],
                            templateStr, variables)
            )

    def __init__(self, subject, mailingList, templateStr, globalVars):
        Campaign.__init__(self, subject, mailingList, templateStr, globalVars)


def CampaignFactory(subject, mailingList,
                    templateFile, globalVarsFile=""):
    '''
        Factory to construct BulkMail or TransactionMail object

        Parameters:
            name                type        comments
            -----------------------------------------
            subject             str         required
            mailingList         list/str    required    a list of strings or
                                                        a string (filename)
            templateFile        str         required    (filename)
            globalVarsFile      str         optional    (filename)
    '''

    # The following variables are used to initialise the appropriate class
    #
    #   templateStr : The template string read from the template file
    #   globalVars  : The dictionary containing the global variables
    #   mailingList : The list of dictionaries that contains the
    #                 mailing list

    # read the template file
    if os.path.exists(templateFile) is False:
        raise Exception("Template list file ({0}) doesn't exist"
                        .format(os.path.abspath(templateFile)))

    ftmpl = open(templateFile, "r")
    templateStr = ftmpl.read()
    ftmpl.close()

    # read the global vars file
    if globalVarsFile != "" and os.path.exists(globalVarsFile) is False:
        raise Exception("Global variables file ({0}) doesn't exist"
                        .format(os.path.abspath(globalVarsFile)))

    contents = ""
    if globalVarsFile != "":
        fglbl = open(globalVarsFile, "r")
        contents = fglbl.read()
        fglbl.close()

    globalVars = dict([(line.split("=")[0].strip(), line.split("=")[1])
                      for line in contents.splitlines()
                      if line.rstrip() != ""])

    # read the mailingList if it is a string
    # in any case, convert it to a list of
    # dictionaries of form:
    #   { "email": "...", "variables": "" }
    if type(mailingList) is str:
        mailingListFile = mailingList

        if os.path.exists(mailingListFile) is False:
            raise Exception("Mailing list file ({0}) doesn't exist"
                            .format(os.path.abspath(mailingListFile)))

        fml = open(mailingListFile, "r")
        contents = fml.read().splitlines()
        fml.close()

        headers, rows = contents[0].split("\t"), contents[1:]

        if headers[0] != "email":
            raise Exception("First field of mailing list file is "
                            "required to be `email`")

        mailingList = []
        for row in rows:
            row = row.split("\t")
            mailingList.append({
                "email": row[0],
                "variables": dict([
                    (headers[i], row[i])
                    for i in range(1, len(headers))
                ])
            })

        mailConstructor = TransactionMailCampaign

    else:
        mailConstructor = BulkMailCampaign

    return mailConstructor(subject, mailingList, templateStr, globalVars)
