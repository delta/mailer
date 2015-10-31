"""
Code to test the deltmail.campaign module

This test case sends the following mails:
    1. "BulkMail : Greetings from Festember" to mojo@jojo.com and phineas@ferb.com
        Both email ids appear in the mail (like CC).
    2. "TransactionMail : Greetings from Festember" to job@bob.com and pop@bob.com
        Two *separate* mails are sent. Unlike CC.
    3. "CampaignFactoryBulk : Greetings from Festember" to job@bob.com, pop@bob.com, sop@bob.com
        All email ids appear in the mail (like CC).
    4. "CampaignFactoryTransaction : Greetings from Festember" to the above three 
        ids. Three *separate* mails are sent. Unlike CC.

    In #3, The email body will look incomplete, because the name and message
    fields in the template.mmtmpl file haven't been filled (because it's a BulkMail).

    Other than these, the test suite also creates preview mails for each of the 
    above mails preview-mails directory. Each Test class creates preview mails
    under the /preview-mails/<Test-class-name> directory.
"""

import shutil

from deltamail.campaign import BulkMailCampaign, TransactionMailCampaign
from deltamail.campaign import CampaignFactory
from deltamail.mailer import Mailer

mailer = Mailer('mailtrap.io', 465, 'username', 'password')


class TestBulkMailCampaign(object):
    """Class to test deltamail.campaign.BulkMailCampaign class"""

    def __init__(self):
        """Create an instance of BulkMailCampaign for testing"""
        self.bmc = BulkMailCampaign(
            "sender@example.com",
            "BulkMail : Greetings from {{company}}",
            ["mojo@jojo.com", "phineas@ferb.com"],
            "Hello Human, greetings from {{company}}.\nCopyright @ {{year}}",
            {"company": "Festember", "year": 2015}
        )

    def setup(self):
        """Setup for the tests"""
        # remove the email-preview folder possibly created in the
        # previous run of the test suite. This folder is created
        # in the test_preview_default() test
        shutil.rmtree('./email-preview', ignore_errors=True)

    def teardown(self):
        """Cleanup the setup"""
        pass

    def test_initialization(self):
        """
        Test if underlying Mail objects are initialized properly
        by BulkMailCampaign
        """
        mails = self.bmc._mails
        assert len(mails) == 1
        assert mails[0].from_id == "sender@example.com"
        assert mails[0].subject == "BulkMail : Greetings from Festember"
        assert mails[0].body == "Hello Human, greetings from Festember.\nCopyright @ 2015"

    def test_preview_default(self):
        """Test preview() with no args"""
        self.bmc.preview()

    def test_preview_with_location(self):
        """Test preview() with location argument"""
        # tested manually. Seems to work fine.
        self.bmc.preview("./tests/preview-mails/TestBulkMailCampaign/")

    def test_send(self):
        """Test the send() method"""
        self.bmc.send(mailer)

    def test_preview_in_browser(self):
        """Test the preview_in_browser() method"""
        # UNTESTED!
        pass


class TestTransactionMailCampaign(object):
    """Class to test deltamail.campaign.TransactionMailCampaign class"""

    def __init__(self):
        """Create an instance of TransactionMailCampaign for testing"""
        self.tmc = TransactionMailCampaign(
            "sender@example.com",
            "TransactionMail : Greetings from {{company}}",
            [
                {
                    "email": 'job@bob.com',
                    "variables": {
                        "name": "Job",
                        "msg": "Sorry, you are rejected. KBye."
                    }
                },
                {
                    "email": 'pop@bob.com',
                    "variables": {
                        "name": "Pop",
                        "msg": "Yay! You are selected. KBye."
                    }
                }
            ],
            "Hello {{name}},\n{{msg}}",
            {"company": "Festember"}
        )

    def setup(self):
        """Setup for the tests"""
        # remove the email-preview folder possibly created in the
        # previous run of the test suite. This folder is created
        # in the test_preview_default() test
        shutil.rmtree('./email-preview', ignore_errors=True)

    def teardown(self):
        """Cleanup the setup"""
        pass

    def test_initialization(self):
        """
        Test if underlying Mail objects are initialized properly
        by TransactionMailCampaign
        """
        mails = self.tmc._mails
        assert len(mails) == 2
        assert mails[0].from_id == "sender@example.com"
        assert mails[1].from_id == "sender@example.com"

        assert mails[0].subject == "TransactionMail : Greetings from Festember"
        assert mails[1].subject == "TransactionMail : Greetings from Festember"

        assert mails[0].body == "Hello Job,\nSorry, you are rejected. KBye."
        assert mails[1].body == "Hello Pop,\nYay! You are selected. KBye."

    def test_preview_default(self):
        """Test preview() with no args"""
        self.tmc.preview()

    def test_preview_with_location(self):
        """Test preview() with location argument"""
        # tested manually. Seems to work fine.
        self.tmc.preview("./tests/preview-mails/TestTransactionMailCampaign/")

    def test_send(self):
        """Test the send() method"""
        self.tmc.send(mailer)

    def test_preview_in_browser(self):
        """Test the preview_in_browser() method"""
        # UNTESTED!
        pass


class TestCampaignFactory(object):
    """Class to test deltamail.campaign.CampaignFactory class"""

    def setup(self):
        """Setup for the tests"""
        from_id = "sender@example.com"
        subject_bulk = "CampaignFactoryBulk : Greetings from {{company}}"
        subject_transaction = "CampaignFactoryTransaction : Greetings from {{company}}"
        f_mailing_list = "./tests/testCampaignFactory-files/mailingList.ml"
        f_template = "./tests/testCampaignFactory-files/template.mmtpl"
        f_global_vars = "./tests/testCampaignFactory-files/globalVars.mvar"

        mailingList = ['FOB@bob.com', 'pop@bob.com']

        self.bmc = CampaignFactory(from_id, subject_bulk, mailingList, f_template, f_global_vars)
        self.tmc = CampaignFactory(from_id, subject_transaction, f_mailing_list, f_template, f_global_vars)

    def teardown(self):
        """Cleanup the setup"""
        pass

    def test_initilization(self):
        """Test if CampaignFactory works fine"""
        loc1 = './tests/preview-mails/TestCampaignFactory/email-preview-bulk/'
        loc2 = './tests/preview-mails/TestCampaignFactory/email-preview-transaction/'

        self.bmc.preview(loc1)
        self.tmc.preview(loc2)

        self.bmc.send(mailer)
        self.tmc.send(mailer)
