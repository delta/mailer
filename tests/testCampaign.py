from deltamail.campaign import BulkMailCampaign, TransactionMailCampaign
from deltamail.campaign import CampaignFactory


class TestBulkMailCampaign:
    def setUp(self):
        self.bmc = BulkMailCampaign("Greetings from {{company}}",
                                    ['job@bob.com'],
                                    "Hello {{name}},\n{{msg}}",
                                    {"company": "Festember",
                                     "name": "Job",
                                     "msg": "Sorry, you are " +
                                            "rejected. KBye."})

    def tearDown(self):
        pass

    def testInitialization(self):
        mails = self.bmc._mails
        assert(len(mails) == 1)
        assert(mails[0].subject == "Greetings from Festember")
        assert(mails[0].body == "Hello Job,\nSorry, you are rejected. KBye.")

    def testPreviewDefault(self):
        self.bmc.preview()
        pass

    def testPreviewWithLocation(self):
        # tested manually. Seems to work fine.
        self.bmc.preview("./tests/email-preview-bulk")
        pass

    def testSend(self):
        # UNTESTED!
        pass

    def testPreviewInBrowser(self):
        # UNTESTED!
        pass


class TestTransactionMailCampaign:
    def setUp(self):
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

    def tearDown(self):
        pass

    def testInitialization(self):
        mails = self.tmc._mails
        assert(len(mails) == 2)
        assert(mails[0].subject == "Greetings from Festember")
        assert(mails[1].subject == "Greetings from Festember")

        assert(mails[0].body == "Hello Job,\nSorry, you are rejected. KBye.")
        assert(mails[1].body == "Hello Pop,\nAww! You are selected. KBye.")

    def testPreview(self):
        # tested manually. Seems to work fine.
        pass

    def testSend(self):
        # UNTESTED!
        pass

    def testPreviewInBrowser(self):
        # UNTESTED!
        pass


class TestCampaignFactory():
    def setUp(self):
        subject = "Greetings from {{company}}"
        fMailingList = "./tests/testCampaignFactory-files/mailingList.ml"
        fTemplate = "./tests/testCampaignFactory-files/template.mmtpl"
        fGlobalVars = "./tests/testCampaignFactory-files/globalVars.mvar"

        mailingList = ['FOB@bob.com', 'pop@bob.com']

        self.bmc = CampaignFactory(subject, mailingList,
                                   fTemplate, fGlobalVars)
        self.tmc = CampaignFactory(subject, fMailingList,
                                   fTemplate, fGlobalVars)

    def tearDown(self):
        pass

    def testInitilization(self):
        loc1 = './tests/testCampaignFactory-files/email-preview-bulk/'
        loc2 = './tests/testCampaignFactory-files/email-preview-transaction/'

        self.bmc.preview(loc1)
        self.tmc.preview(loc2)
