import os

from .mail import MailFactory

# Upper limit on preview-file name length
MAX_PREVIEW_FILE_LEN = 30


class Campaign():
    '''
        *Campaign objects inherit from Campaign.
        *Campaign objects just fill the _mails list, and
        the sending and previewing is done here itself.
    '''

    # stores the raw mail objects
    _mails = []

    def send(self, mailer):
        for m in self._mails:
            mailer.send(m)

    def preview(self, location=""):
        if location is "":
            location = os.path.join(os.getcwd(), "email-preview", "")
            os.mkdir(location)

        if os.path.exists(location) is False:
            raise Exception(
                "Location given for preview (%s) doesn't exist." % location
            )

        for m in self._mails:
            filename = (m.subject + "-" + m.mailingList)[:MAX_PREVIEW_FILE_LEN]

            # replace \ and / with - in case the subject contains
            # those characters
            filename.replace("\/", "-")
            filename.replace("\\", "-")

            # finally, write the body
            fpreview = open(os.path.join(location, filename), "w")
            fpreview.write(m.body)
            fpreview.close()


class BulkMailCampaign(Campaign):
    '''
        Same mail sent to each person.
    '''
    def __init__(self, subject, mailingList, templateStr, variables):
        self._mails = [
            MailFactory(subject, mailingList, templateStr, variables)
        ]


class TransactionMailCampaign(Campaign):
    '''
        Personalised mails sent to each person.
    '''
    def __init__(self, subject, mailingList, templateStr, globalVars):
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


def CampaignFactory(self, subject, mailingList,
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
        raise Exception("Template file doesn't exist")

    ftmpl = open(templateFile, "r")
    templateStr = ftmpl.read()
    ftmpl.close()

    # read the global vars file
    if globalVarsFile is not "" and os.path.exists(globalVarsFile) is False:
        raise Exception("Global Variables file doesn't exist")

    fglbl = open(globalVarsFile, "r")
    contents = fglbl.read()
    fglbl.close()

    globalVars = dict([(line.split("=")[0].strip(), line.split("=")[1])
                      for line in contents.splitlines()
                      if line is not ""])

    # read the mailingList if it is a string
    # in any case, convert it to a list of
    # dictionaries of form:
    #   { "email": "...", "variables": "" }
    if type(mailingList) is str:
        mailingListFile = mailingList

        if os.path.exists(mailingListFile) is False:
            raise Exception("Mailing list file doesn't exist")

        fml = open(mailingListFile, "r")
        contents = fml.read().splitlines()
        fml.close()

        headers, rows = contents[0], contents[1:]
        if headers[0] is not "email":
            raise Exception("First field of mailing list file is "
                            "required to be `email`")

        mailingList = []
        for row in rows:
            mailingList.append({
                "email": row[0],
                "variables": dict([
                    (headers[i], row[i])
                    for i in range(1, len(headers))
                ])
            })

        mailConstructor = TransactionMailCampaign

    else:
        mailingList = [{"email": email, "variables": {}}
                       for email in mailingList]
        mailConstructor = BulkMailCampaign

    return mailConstructor(subject, mailingList, templateStr, globalVars)
