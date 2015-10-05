"""Code to test the deltmail.campaign module"""

import shutil

from deltamail.campaign import BulkMailCampaign, TransactionMailCampaign
from deltamail.campaign import CampaignFactory
from deltamail.mailer import Mailer

mailer = Mailer('mailtrap.io', 465, 'username', 'password', 'senderid')


class TestBulkMailCampaign(object):
    """Class to test deltamail.campaign.BulkMailCampaign class"""

    def __init__(self):
        """Create an instance of BulkMailCampaign for testing"""
        self.bmc = BulkMailCampaign("Greetings from {{company}}",
                                    ['job@bob.com'],
                                    "Hello {{name}},\n{{msg}}",
                                    {"company": "Festember",
                                     "name": "Job",
                                     "msg": "Sorry, you are " +
                                            "rejected. KBye."})

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
        assert mails[0].subject == "Greetings from Festember"
        assert mails[0].body == "Hello Job,\nSorry, you are rejected. KBye."

    def test_preview_default(self):
        """Test preview() with no args"""
        self.bmc.preview()

    def test_preview_with_location(self):
        """Test preview() with location argument"""
        # tested manually. Seems to work fine.
        self.bmc.preview("./tests/email-preview-bulk")

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
        self.tmc = TransactionMailCampaign("Greetings from {{company}}",
                                           [
                                             {
                                                 "email": 'job@bob.com',
                                                 "variables": {
                                                     "name": "Job",
                                                     "msg": "Sorry, you are " +
                                                            "rejected. KBye."}
                                             },
                                             {
                                                 "email": 'pop@bob.com',
                                                 "variables": {
                                                     "name": "Pop",
                                                     "msg": "Aww! You are " +
                                                            "selected. KBye."}
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
        assert mails[0].subject == "Greetings from Festember"
        assert mails[1].subject == "Greetings from Festember"

        assert mails[0].body == "Hello Job,\nSorry, you are rejected. KBye."
        assert mails[1].body == "Hello Pop,\nAww! You are selected. KBye."

    def test_preview_default(self):
        """Test preview() with no args"""
        self.tmc.preview()

    def test_preview_with_location(self):
        """Test preview() with location argument"""
        # tested manually. Seems to work fine.
        self.tmc.preview("./tests/email-preview-transaction")

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
        subject = "Greetings from {{company}}"
        f_mailing_list = "./tests/testCampaignFactory-files/mailingList.ml"
        f_template = "./tests/testCampaignFactory-files/template.mmtpl"
        f_global_vars = "./tests/testCampaignFactory-files/globalVars.mvar"

        mailingList = ['FOB@bob.com', 'pop@bob.com']

        self.bmc = CampaignFactory(subject, mailingList, f_template, f_global_vars)
        self.tmc = CampaignFactory(subject, f_mailing_list, f_template, f_global_vars)

    def teardown(self):
        """Cleanup the setup"""
        pass

    def test_initilization(self):
        """Test if CampaignFactory works fine"""
        loc1 = './tests/testCampaignFactory-files/email-preview-bulk/'
        loc2 = './tests/testCampaignFactory-files/email-preview-transaction/'

        self.bmc.preview(loc1)
        self.tmc.preview(loc2)

        self.bmc.send(mailer)
        self.tmc.send(mailer)
