"""
Code to test the deltmail.campaign module

This test case sends the following mails:
    1. "BulkMail : Greetings from Festember" to mojo@jojo.com and phineas@ferb.com
        Both email ids appear in the mail (like CC).
    2. "TransactionMail : Greetings from Festember" to job@bob.com and pop@bob.com
        Two *separate* mails are sent. Unlike CC.
    3. "CampaignFactoryBulk : Greetings from Festember" to FOB@bob.com, pop@bob.com
        All email ids appear in the mail (like CC).
    4. "CampaignFactoryTransaction : Greetings from Festember" to job@bob.com, pop@bob.com,
        sop@bob.com. Three *separate* mails are sent. Unlike CC.

    In #3, The email body will look incomplete, because the name and message
    fields in the template.mmtmpl file haven't been filled (because it's a BulkMail).

    Other than these, the test suite also creates preview mails for each of the
    above mails preview-mails directory. Each Test class creates preview mails
    under the /preview-mails/<Test-class-name> directory.
"""

import sys
import os
import os.path as path

try:
    from unittest.mock import patch
    from unittest.mock import Mock
except:
    from mock import patch
    from mock import Mock

from deltamail.campaign import BulkMailCampaign, TransactionMailCampaign
from deltamail.campaign import CampaignFactory
from deltamail.campaign import MAX_PREVIEW_FILE_LEN
from deltamail.mail import MailFactory


class TestBulkMailCampaign(object):
    """Class to test deltamail.campaign.BulkMailCampaign class"""

    args = {
        "from_addr": "sender@example.com",
        "subject": "BulkMail : Greetings from {{company}}",
        "mailing_list": ["mojo@jojo.com", "phineas@ferb.com"],
        "template_str": "Hello Human, greetings from {{company}}.\nCopyright @ {{year}}",
        "global_vars": {"company": "Festember", "year": 2015}
    }

    subject_evaled = "BulkMail : Greetings from Festember"
    body_evaled = "Hello Human, greetings from Festember.\nCopyright @ 2015"

    @patch('deltamail.campaign.MailFactory', autospec=True)
    def __init__(self, mock_mf):
        """Create an instance of BulkMailCampaign for testing.
        Also test if it is initialized correctly."""
        self.bmc = BulkMailCampaign(**self.args)

        assert len(self.bmc._mails) == 1

        # MailFactory calls it `variables` and not `global_vars`
        # Rename it. Laziness
        self.args["variables"] = self.args["global_vars"]
        self.args.pop("global_vars", None)
        mock_mf.assert_called_once_with(**self.args)

        # acquire the actual Envelope object
        self.bmc._mails = [MailFactory(**self.args)]
        
        # Rename it back
        self.args["global_vars"] = self.args["variables"]
        self.args.pop("variables", None)

    @patch('deltamail.campaign.os.path.isdir', autospec=True)
    @patch('deltamail.campaign.os.mkdir', autospec=True)
    @patch('deltamail.campaign.open')
    def test_preview_default(self, mk_open, mock_mkdir, mock_isdir):
        """Test BulkMailCampaign.preview() with no args"""

        newdirpath = path.join(os.getcwd(), "email-preview", "")

        preview_file_name = self.subject_evaled + "-" + ",".join(self.args["mailing_list"])
        preview_file_name = preview_file_name[:MAX_PREVIEW_FILE_LEN] + ".html"
        preview_file_name = preview_file_name.replace(r"/", "-")
        preview_file_name = preview_file_name.replace("\\", "-")
        preview_file_name = preview_file_name.replace(r":", "-")

        preview_file_path = path.join(newdirpath, preview_file_name)

        open_return_mock = Mock()
        mk_open.return_value = open_return_mock

        mock_isdir.return_value = True
        
        self.bmc.preview()
        
        mock_mkdir.assert_called_once_with(newdirpath)
        mk_open.assert_called_once_with(preview_file_path, "w")
        open_return_mock.write.assert_called_once_with(self.body_evaled)
        open_return_mock.close.assert_called_once_with()

    @patch('deltamail.campaign.os.path.isdir', autospec=True)
    @patch('deltamail.campaign.os.mkdir', autospec=True)
    @patch('deltamail.campaign.open')
    def test_preview_with_location(self, mk_open, mock_mkdir, mock_isdir):
        """Test BulkMailCampaign.preview() with location argument"""
        newdirpath = "./tests/preview-mails/TestBulkMailCampaign/"

        preview_file_name = self.subject_evaled + "-" + ",".join(self.args["mailing_list"])
        preview_file_name = preview_file_name[:MAX_PREVIEW_FILE_LEN] + ".html"
        preview_file_name = preview_file_name.replace(r"/", "-")
        preview_file_name = preview_file_name.replace("\\", "-")
        preview_file_name = preview_file_name.replace(r":", "-")

        preview_file_path = path.join(newdirpath, preview_file_name)

        open_return_mock = Mock()
        mk_open.return_value = open_return_mock
        
        self.bmc.preview(newdirpath)
        
        mock_mkdir.assert_not_called()
        mk_open.assert_called_once_with(preview_file_path, "w")
        open_return_mock.write.assert_called_once_with(self.body_evaled)
        open_return_mock.close.assert_called_once_with()

    def test_send(self):
        """Test the BulkMailCampaign.send() method"""
        mock_mailer = Mock(spec=['send'])
        self.bmc.send(mock_mailer)
        mock_mailer.send.assert_called_once_with(self.bmc._mails[0])

    def test_preview_in_browser(self):
        """Test the preview_in_browser() method"""
        # UNTESTED!
        pass


class TestTransactionMailCampaign(object):
    """Class to test deltamail.campaign.TransactionMailCampaign class"""

    args = {
        "from_addr": "sender@example.com",
        "subject": "TransactionMail : Hey {{name}}, Greetings from {{company}}",
        "mailing_list": [
            {
                "email": 'job@bob.com',
                "variables": {
                    "name": "Job",
                    "msg": "You got a job!"
                }
            },
            {
                "email": 'pop@bob.com',
                "variables": {
                    "name": "Pop",
                    "msg": "You got popped!"
                }
            }
        ],
        "template_str": "Hello {{name}}, greetings from {{company}}.\n{{msg}}\nCopyright @ {{year}}",
        "global_vars": {"company": "Festember", "year": 2015}
    }

    evaled = [
        {
            "subject": "TransactionMail : Hey Job, Greetings from Festember",
            "body": "Hello Job, greetings from Festember.\nYou got a job!\nCopyright @ 2015",
        },
        {
            "subject": "TransactionMail : Hey Pop, Greetings from Festember",
            "body": "Hello Pop, greetings from Festember.\nYou got popped!\nCopyright @ 2015",
        }
    ]

    variables = [
        {
            "name": "Job",
            "msg": "You got a job!",
            "company": "Festember",
            "year": 2015
        },
        {
            "name": "Pop",
            "msg": "You got popped!",
            "company": "Festember",
            "year": 2015
        }
    ]

    @patch('deltamail.campaign.MailFactory', autospec=True)
    def __init__(self, mock_mf):
        """Create an instance of TransactionMailCampaign for testing.
        Also test if it is initialized correctly."""

        self.tmc = TransactionMailCampaign(**self.args)
        assert len(self.tmc._mails) == 2

        # MailFactory calls it `variables` and not `global_vars`
        # Rename it. Laziness
        global_vars = self.args["global_vars"]
        mailing_list = self.args["mailing_list"]

        self.args.pop("global_vars", None)

        self.args["variables"] = self.variables[0]
        self.args["mailing_list"] = [mailing_list[0]["email"]]
        # acquire the actual Envelope object
        self.tmc._mails[0] = MailFactory(**self.args)

        mock_mf.assert_any_call(**self.args)

        self.args["variables"] = self.variables[1]
        self.args["mailing_list"] = [mailing_list[1]["email"]]
        # acquire the actual Envelope object
        self.tmc._mails[1] = MailFactory(**self.args)
        mock_mf.assert_any_call(**self.args)
        
        # Undo the changes
        self.args["mailing_list"] = mailing_list
        self.args["global_vars"] = global_vars
        self.args.pop("variables", None)

    @patch('deltamail.campaign.os.path.isdir', autospec=True)
    @patch('deltamail.campaign.os.mkdir', autospec=True)
    @patch('deltamail.campaign.open')
    def test_preview_default(self, mk_open, mock_mkdir, mock_isdir):
        """Test TransactionMailCampaign.preview() with no args"""
        newdirpath = path.join(os.getcwd(), "email-preview", "")
        
        open_return_mock = Mock()
        mk_open.return_value = open_return_mock

        mock_isdir.return_value = True

        self.tmc.preview()

        mock_mkdir.assert_called_once_with(newdirpath)

        for i in range(len(self.evaled)):
            fname = self.evaled[i]["subject"] + "-" + self.args["mailing_list"][i]["email"]
            fname = fname[:MAX_PREVIEW_FILE_LEN] + ".html"
            fname = fname.replace(r"/", "-")
            fname = fname.replace("\\", "-")
            fname = fname.replace(r":", "-")

            fpath = path.join(newdirpath, fname)

            mk_open.assert_any_call(fpath, "w")
            open_return_mock.write.assert_any_call(self.evaled[i]["body"])

        assert mk_open.call_count == 2
        assert open_return_mock.write.call_count == 2
        assert open_return_mock.close.call_count == 2

    @patch('deltamail.campaign.os.path.isdir', autospec=True)
    @patch('deltamail.campaign.os.mkdir', autospec=True)
    @patch('deltamail.campaign.open')
    def test_preview_with_location(self, mk_open, mock_mkdir, mock_isdir):
        """Test TransactionMailCampaign.preview() with location argument"""
        newdirpath = "./tests/preview-mails/TestBulkMailCampaign/"

        open_return_mock = Mock()
        mk_open.return_value = open_return_mock

        self.tmc.preview(newdirpath)

        mock_mkdir.assert_not_called()

        for i in range(len(self.evaled)):
            fname = self.evaled[i]["subject"] + "-" + self.args["mailing_list"][i]["email"]
            fname = fname[:MAX_PREVIEW_FILE_LEN] + ".html"
            fname = fname.replace(r"/", "-")
            fname = fname.replace("\\", "-")
            fname = fname.replace(r":", "-")

            fpath = path.join(newdirpath, fname)

            mk_open.assert_any_call(fpath, "w")
            open_return_mock.write.assert_any_call(self.evaled[i]["body"])

        assert mk_open.call_count == 2
        assert open_return_mock.write.call_count == 2
        assert open_return_mock.close.call_count == 2

    def test_send(self):
        """Test the TransactionMailCampaign.send() method"""
        mock_mailer = Mock(spec=['send'])
        self.tmc.send(mock_mailer)
        mock_mailer.send.assert_any_call(self.tmc._mails[0])
        mock_mailer.send.assert_any_call(self.tmc._mails[0])
        assert mock_mailer.send.call_count == 2

    def test_preview_in_browser(self):
        """Test the preview_in_browser() method"""
        # UNTESTED!
        pass


class TestCampaignFactory(object):
    """Class to test deltamail.campaign.CampaignFactory class"""

    # We just check if the appropriate *-Campaign constructors are called
    # with correct arguments
    # 
    # Cases to consider:
    # a. MailingList is a string (filename), file doesn't exist
    # b. MailingList file exists, but is not well formed
    # c. MailingList file exists, and is well formed
    # d. MailingList is a list of email ids
    # 
    # For each of those:
    #   1. Template file doesn't exist
    #   2. Template file exists:
    #       2.1. Global Vars file doesn't exist, path not given
    #       2.2. Global Vars file doesn't exists, path given
    #       2.3. Global Vars file exists, path given.
    
    from_addr = "sender@example.com"
    subject = "Subject"

    correct_paths = {
        "fmailing_list": "tests/testCampaignFactory-files/mailingList.ml",
        "fmailing_list_bad": "tests/testCampaignFactory-files/mailingList_bad.ml",
        "ftemplate": "tests/testCampaignFactory-files/template.mmtmpl",
        "fglobal_vars": "tests/testCampaignFactory-files/globalVars.mvar"
    }

    def _path_settings(self, attr, val):
        if val == True:
            setattr(self, attr, self.correct_paths[attr])
        elif val == False:
            setattr(self, attr, "NON-EXISTING")
        else:
            setattr(self, attr, self.correct_paths[val])

    def _run(self, exception_expected):
        exception_raised = False
        ret = None
        try:
            ret = CampaignFactory(self.from_addr, self.subject,
                            self.fmailing_list, self.ftemplate,
                            self.fglobal_vars)
        except:
            e = sys.exc_info()[1]
            exception_raised = True

            if not exception_expected:
                raise e

        assert exception_raised == exception_expected
        return ret
    
    def test_non_existing_fmailing_list(self):
        """Test CampaignFactory if mailing_list is a string, but the file
        doesn't exist"""
        self._path_settings("fmailing_list", False)
        
        # 1. Template file doesn't exist
        self._path_settings("ftemplate", False)
        self._path_settings("fglobal_vars", False)

        self._run(True)

        # 2. Template file exists
        # 2.1. Global Vars file doesn't exist, path not given
        self.fglobal_vars = ""
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", False)

        self._run(True)
        self.fglobal_vars = "fglobal_vars"

        # 2.2. Global Vars file doesn't exists, path given
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)

        # 2.3. Global Vars file exists, path given.
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", True)
        
        self._run(True)

    def test_existing_malformed_fmailing_list(self):
        """Test CampaignFactory if mailing_list is a string, the file
        exists, but is malformed"""
        self._path_settings("fmailing_list", "fmailing_list_bad")
        
        # 1. Template file doesn't exist
        self._path_settings("ftemplate", False)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)

        # 2. Template file exists
        # 2.1. Global Vars file doesn't exist, path not given
        self.fglobal_vars = ""
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)
        self.fglobal_vars = "fglobal_vars"

        # 2.2. Global Vars file doesn't exists, path given
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)

        # 2.3. Global Vars file exists, path given.
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", True)
        
        self._run(True)

    def test_existing_well_formed_fmailing_list(self):
        """Test CampaignFactory if mailing_list is a string, the file
        exists, and is wellformed"""
        self._path_settings("fmailing_list", "fmailing_list")
        
        # 1. Template file doesn't exist
        self._path_settings("ftemplate", False)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)

        # 2. Template file exists
        # 2.1. Global Vars file doesn't exist, path not given
        self._path_settings("ftemplate", True)
        # self._path_settings("fglobal_vars", True)
        self.fglobal_vars = ""

        ret = self._run(False)
        self.fglobal_vars = "fglobal_vars"
        assert isinstance(ret, TransactionMailCampaign) 

        # 2.2. Global Vars file doesn't exists, path given
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)

        # 2.3. Global Vars file exists, path given.
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", True)
        
        ret = self._run(False)
        assert isinstance(ret, TransactionMailCampaign)

    def test_mailing_list(self):
        """Test CampaignFactory if mailing_list is a list of bad email-ids"""
        # self._path_settings("fmailing_list", "fmailing_list")
        self.fmailing_list = ["job@foo", "bofoo.com", "mo@fo.com"]
        
        # 1. Template file doesn't exist
        self._path_settings("ftemplate", False)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)

        # 2. Template file exists
        # 2.1. Global Vars file doesn't exist, path not given
        self._path_settings("ftemplate", True)
        # self._path_settings("fglobal_vars", True)
        self.fglobal_vars = ""

        ret = self._run(False)
        self.fglobal_vars = "fglobal_vars"
        assert isinstance(ret, BulkMailCampaign)

        # 2.2. Global Vars file doesn't exists, path given
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", False)
        
        self._run(True)

        # 2.3. Global Vars file exists, path given.
        self._path_settings("ftemplate", True)
        self._path_settings("fglobal_vars", True)
        
        ret = self._run(False)
        assert isinstance(ret, BulkMailCampaign)
